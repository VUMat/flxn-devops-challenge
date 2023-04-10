## How to install/deploy app with docker locally:

Build docker image:  
``docker build -t helloworld-app .``

Run dockerimage locally:
``docker run -p 5000:5000 helloworld-app``


# Description:

This pipeline performs static code analysis using flask8, container vulnerability scan using trivy. 
Main branch in my github repo protected and not allowing to push code without pull request. However, I can't enforce this settings on private account and it is still possible to push directly to main branch.

## Things to improve:

- scan steps to pipeline 
        - docker lint steps
        - test coverage

- env promotion process 
- update helm templates to make sure you are using load balancer with existing IP (which should have dns name attach to it)

- create terraform (IaC) to deploy GCP infra
- capability to deploy ephemeral GKE cluster for CI/CD and test/dev environmentss  (cluster that will be deleted after all tests)
- add code to setup GKE (gcloud cli) 
- fine-tune firewall in GKE to limit access for github actions 
- update gcp github actions service account to use Workload Identity Federation / Keyless access instead of service account


# How to:

## Requirenments:
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

3. Push code to your repository. It should automatically create "Build and Deploy" Github Actions pipeline