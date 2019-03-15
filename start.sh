#!/bin/sh
#REMEMBER >>> Enable the Cloud SQL Admin API in your project!

PROJECT_ID=$(gcloud config get-value project)
INSTANCE_NAME=$(cat /dev/urandom | tr -dc 'a-za-z' | fold -w 8 | head -n 1)
CLUSTER_ZONE="us-central1-a"
CLUSTER_REGION="us-central1"
INSTANCE_CONNECTION_NAME=$PROJECT_ID":"$CLUSTER_REGION":"$INSTANCE_NAME
DB_ROOT_PASS="123"
DB_NAME="mydb"
DB_USER="proxyuser"
DB_USER_PASS="123"
CLUSTER_NAME=$(cat /dev/urandom | tr -dc 'a-za-z' | fold -w 8 | head -n 1)
#CLUSTER_NAME="mycluster"
SA_NAME="cloud-sql-sa"
FULL_SA_NAME=${SA_NAME}"@"${PROJECT_ID}".iam.gserviceaccount.com"

#General settings
gcloud config set project ${PROJECT_ID}
gcloud config set compute/zone ${CLUSTER_ZONE}



# Create Cloud SQL

#echo "Cloud SQL instance creation started. This process takes a long time (5-10min)."
gcloud sql instances create $INSTANCE_NAME \
--database-version MYSQL_5_7 \
--tier=db-g1-small \
--region=us-central


#Create Proxy User
gcloud sql users create ${DB_USER} --host=% --instance=${INSTANCE_NAME}   --password=${DB_USER_PASS}

#Create service-account
gcloud iam service-accounts create ${SA_NAME} --display-name ${SA_NAME}

# This is the policy for the container that will communicate with Cloud SQL Proxy
gcloud projects add-iam-policy-binding ${PROJECT_ID} \
--member serviceAccount:${FULL_SA_NAME} \
--role roles/cloudsql.admin

gcloud projects add-iam-policy-binding ${PROJECT_ID} \
--member serviceAccount:${FULL_SA_NAME} \
--role roles/editor


gcloud iam service-accounts keys create credentials.json --iam-account ${FULL_SA_NAME}

gcloud container clusters create ${CLUSTER_NAME} \
--num-nodes 3 \
--enable-autorepair \
--zone ${CLUSTER_ZONE} \
--service-account=${FULL_SA_NAME}

#Create configmap to pass variables to deployment.yaml and proxy.yaml
kubectl create configmap yaml-config --from-literal=project-id=$PROJECT_ID --from-literal=instance-connection-name=$PROJECT_ID":"$CLUSTER_REGION":"$INSTANCE_NAME

#Create two secrets
kubectl create secret generic cloudsql-instance-credentials \
--from-file=credentials.json=credentials.json

kubectl  create secret generic cloudsql-db-credentials \
--from-literal=user=${DB_USER} \
--from-literal=password=${DB_USER_PASS}

#Deployment proxy container and create database with tables
export DB_USER=$DB_USER
export DB_USER_PASS=$DB_USER_PASS
export PROJECT_ID=$PROJECT_ID
export INSTANCE_CONNECTION_NAME=$INSTANCE_CONNECTION_NAME

sh db-mysql-fill-data.sh
