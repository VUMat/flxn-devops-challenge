How to install/deploy:

Build docker image:  
``docker build -t helloworld-app .``

Run dockerimage locally:
``docker run -p 5000:5000 helloworld-app``


Description:





add a prioritized list of five or more development tasks you would
do next to improve your solution to the code challenge.


Things to improve:
- GKE autopilot -> GKE if have specific requirenments /cost concern

- scan steps to pipeline 
        - static code analysis
        - lint steps
        - test coverage
        - container vulnerability scan


- create terraform (IaC) to deploy GCP infra
- capability to deployephemeral GKE cluster for CI/CD and test/dev environmentss  
- add code to setup GKE (gcloud cli) 
- fine-tune firewall in GKE to limit access for github actions 


Service account for GKE with minimal privileged permissions:
gcloud services enable cloudresourcemanager.googleapis.com #enable api to edit  IAM policies

Create a service account:
gcloud iam service-accounts create SA_min_gke \
    --display-name="SA for GKE minimal privileged"

Add the roles/container.nodeServiceAccount role to the service account

gcloud projects add-iam-policy-binding 	phrasal-aegis-381319  \
    --member "serviceAccount:SA-min-gke@phrasal-aegis-381319.iam.gserviceaccount.com" \
    --role roles/container.nodeServiceAccount

Optionally we can grant access to private registry to this account.

Create a gcp service account for deploying from github actions with role KubernetesAdmin


Create a regional cluster with a multi-zone node pool

gcloud container clusters create mygkecluster \
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
    --service-account SA-min-gke@phrasal-aegis-381319.iam.gserviceaccount.com


Optionally we can add --enable-stackdriver-kubernetes for monitoring purpose if we are using stackdriver


following secrets needs to be set up in github actions: 
CLUSTER_NAME
DOCKER_PASSWORD
DOCKER_USERNAME
GKE_CLUSTER_REGION
GKE_PROJECT_ID
