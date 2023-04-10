# Description:

This repo has app.py Python Flask web application that creates a connection to a SQLite database and returns the total number of visits to the homepage. The application runs on port 5000 and is set to debug mode.

<details>
  <summary>Description of files in this repo:</summary>

 - app.py - a simple Python "hello world" app with db;
 - requirements.txt - list of requirements for python app and tests;
 - Dockerfile to containerize the helloworld-app;
 - helm folder - helm template to deploy app to Kubernetes using helm;
 - .github/workflows/build-and-deploy.yml GitHub Actions pipeline
 - .github/workflows/prod-deploy.yml GitHub Actions pipeline to deploy to prod

  </details>


Pipeline flow description

- pipeline "build and deploy" triggers when PR opened for "main" branch
- Checkout code
- Set up python dependencies
- Run Flake8 code quality check
- Log in to container registry (Dockerhub)
- Build and Push Docker image to registry 
- Run Trivy vulnerability scanner
- Authenticate to GCP and get credentials to GKE
- Deploy helloworld-app to GKE using Helm
- Create PR to branch "prod"
- After merge of changes from branch main to prod prod-deploy pipeline triggers and deploy the same docker image using helm with prod-values


This pipeline performs static code analysis using flask8, container vulnerability scan using trivy. 
Main branch in my github repo protected and not allowing to push code without pull request. However, I can't enforce this settings on private account and it is still possible to push directly to main branch.



# How to:

## Install/deploy app with docker locally:

Build docker image:  
``docker build -t helloworld-app .``

Run dockerimage locally:
``docker run -p 5000:5000 helloworld-app``

## Deploy app to GKE using Github Actions: 

### Requirenments:
 - Github repo
 - GCP account
 - Dockerhub (container registry)


### GCP service accounts:

1. Create Service account for GKE with minimal privileged permissions:
gcloud services enable cloudresourcemanager.googleapis.com #enable api to edit  IAM policies. 
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

2. Create a gcp service account for github actions with role KubernetesAdmin 
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
CLUSTER_NAME        #name of the gke cluster
DOCKER_PASSWORD     #creds to push container to registry
DOCKER_USERNAME     #creds to push container to registry
DOCKER_REPO         #vumat/helloworld-app:latest
GKE_CLUSTER_REGION  #us-west1 region where your gke cluster located
GKE_PROJECT_ID      #id of google cloud project
GCP_CREDS           #json of service account
```

2. Make sure your branch is protected (no push without PR) by configuring it in repo settings. Add reviewers as well.

3. Push code to your repository. Made sme changes in non main branch, push it and create PR to main branch. It should automatically create "Build and Deploy" Github Actions pipeline. Pipeline works as a check for PR.  




## Things to improve:

1. add terraform code (IaC) to depoy and manage GCP resources 
2. update gcp github actions service account to use Workload Identity Federation / Keyless access instead of service account to improve security
3. add capability to deploy ephemeral GKE cluster for CI/CD and test/dev environmentss  (cluster that will be deleted after all tests) to reduce cloud costs
4. fine-tune firewall in GKE to limit access for github actions to improve security 

5. update helm templates to make sure you are using load balancer with existing IP (which should have dns name attach to it)
6. add more scan steps to pipeline 
   - docker lint steps
   - test coverage