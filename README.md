# Description:

This repository has a Python Flask web application, app.py, that creates a connection to a SQLite database and returns the total number of visits to the homepage. The application runs on port 5000 and is set to debug mode.

<details>
  <summary>Description of files in this repo:</summary>

- `app.py` - a simple Python "hello world" app with a database.

- `requirements.txt` - a list of requirements for the Python app and tests.

- `Dockerfile` - file to containerize the hello-world app.

- `helm folder` - helm template to deploy the app to Kubernetes using helm.

- `.github/workflows/build-and-deploy.yml` - GitHub Actions pipeline.

- `.github/workflows/prod-deploy.yml` - GitHub Actions pipeline to deploy to production.
  </details>


## Pipeline flow description

- The pipeline "build and deploy" is triggered when a pull request is opened for the "main" branch.
- Checkout the code.
- Set up Python dependencies.
- Run Flake8 code quality check.
- Log in to the container registry (Dockerhub).
- Build and push the Docker image to the registry.
- Run Trivy vulnerability scanner.
- Authenticate to GCP and get credentials for GKE.
- Deploy the hello-world app to GKE using Helm.
- Create a pull request to the "prod" branch.
- After merging the changes from the main branch to the prod branch, the prod-deploy pipeline is triggered to deploy the same Docker image using Helm with prod-values.

The "main" and "prod" branches in my GitHub repository are protected and does not allow code to be pushed without a pull request. However, I can't enforce these settings on a private GitHub account, and it is still possible to push code directly to the main branch.



# How to:

## Install/deploy app with docker locally:

Build docker image:  
```
docker build -t helloworld-app .
```

Run dockerimage locally:
```
docker run -p 5000:5000 helloworld-app
```

## Deploy app to GKE using Github Actions: 

### Requirenments:
 - Github repo
 - GCP account
 - Dockerhub (container registry)


### GCP service accounts:

1. Create a service account for GKE with minimal privileged permissions.
- Enable the API to edit IAM policies:
gcloud services enable cloudresourcemanager.googleapis.com
- Create a service account for GKE:
```
gcloud iam service-accounts create SA_min_gke \
    --display-name="SA for GKE minimal privileged"
```
- Add the roles/container.nodeServiceAccount role to the GKE service account
```
gcloud projects add-iam-policy-binding 	[PROJECT_ID]  \
    --member "serviceAccount:[SA_EMAIL]" \
    --role roles/container.nodeServiceAccount
```
Optionally we can grant access to private registry to this account.

2. Create a GCP service account for GitHub Actions with the KubernetesAdmin role:
```
gcloud iam service-accounts create sa-github-actions \
    --display-name="SA for GithubActions deployments" 
```
- Add the roles/container.nodeServiceAccount role to the GKE service account

```
gcloud projects add-iam-policy-binding [PROJECT_ID] \
  --member serviceAccount:[SA_EMAIL] \
  --role roles/container.admin
```
3. Create a regional cluster with a multi-zone node pool using gcloud cli.

```
gcloud container clusters create CLUSTER_NAME \
    --region us-west1 \
    --num-nodes 1 \
    --machine-type n1-standard-1 \
    --disk-size=10GB \
    --enable-autorepair \
    --enable-autoscaling \
    --max-nodes 3 \
    --min-nodes 1 \
    --node-locations us-west1-a,us-west1-b,us-west1-c \
    --node-labels env=production \
    --service-account SA-min-gke@[PROJECT_ID].iam.gserviceaccount.com
```

Optionally we can add --enable-stackdriver-kubernetes for monitoring purpose (if we are using stackdriver)

### GitHub Actions

1. Setup following secrets needs to be set up in github actions prior running pipeline: 
```
CLUSTER_NAME        #the name of the GKE cluster
DOCKER_PASSWORD     #credentials to push the container to the registry
DOCKER_USERNAME     #credentials to push the container to the registry
DOCKER_REPO         #the name of the Docker repository and tag, e.g., vumat/helloworld-app:latest
GKE_CLUSTER_REGION  #the region where your GKE cluster is located, e.g., us-west1
GKE_PROJECT_ID      #the ID of the Google Cloud project
GCP_CREDS           #the JSON key file of the service account
```

2. Ensure that your branch is protected by configuring it in the repository settings to disallow direct pushes without a pull request. Additionally, consider adding reviewers to the pull request process to ensure code quality and security.

2. Push your code changes to the repository. Make sure to create a pull request from a non-main branch to the main branch. This should trigger the "Build and Deploy" GitHub Actions pipeline, which will build the app, create a Docker image, push it to the registry, and deploy it to the GKE cluster using Helm. The pipeline serves as a check for the pull request. Once the "Build and Deploy" pipeline completes successfully, it will automatically create a pull request to the prod branch. After merging this pull request to the prod branch, it will trigger the "Prod-Deploy" pipeline, which will deploy the app to the same cluster but using the prod-values.yaml file to ensure a production-ready deployment.






## Things to improve:

1.  Add Terraform code (IaC) to deploy and manage GCP resources.
2.  Update the GCP GitHub Actions service account to use Workload Identity Federation/Keyless access instead of a service account to improve security.
3.  Add the capability to deploy an ephemeral GKE cluster for CI/CD and test/dev environments (a cluster that will be deleted after all tests) to reduce cloud costs.
4.  Fine-tune the firewall in GKE to limit access for GitHub Actions to improve security.
5.  Add automatic PR creation from the main to the prod branch. Prod PR merge will trigger prod deploy. Known issue of not triggering GitHub Actions when an automatic PR is created.
6.  Ensure no downtime during deployment.
7.  Add more scan steps to the pipeline:
      Docker lint steps
      Test coverage

