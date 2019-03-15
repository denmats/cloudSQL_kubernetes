#!/bin/bash
export PROJECT_ID="$(gcloud config get-value project -q)"

#Build toolbox image
docker build --no-cache -t  gcr.io/${PROJECT_ID}/toolbox:2.0 .
docker push gcr.io/${PROJECT_ID}/toolbox:2.0

export PROJECT_ID
envsubst < proxy.yaml | kubectl apply -f -

sleep 20s
POD_NAME=`echo "$(kubectl get pods)" | grep -i proxy | cut -f1 -d ' '`
kubectl exec -it $POD_NAME -c ubuntu -- mysql -u$DB_USER -p$DB_USER_PASS -h 127.0.0.1<<EOF

/*create database mydb*/
create database if not exists mydb;

/*turn into mydb*/
use mydb;

/*create tables: users, bookings, movies*/
create table if not exists users(id varchar(100) primary key, name varchar(100), last_active varchar(20));
create table if not exists bookings(id varchar(100) primary key, date varchar(20), movies varchar(100));
create table if not exists movies(title varchar(100) primary key, rating varchar(10), director  varchar(100), id varchar(100));


load data local infile '/opt/users.csv' into table users
 fields terminated by ',' enclosed by ' '
 lines terminated by '\n'
 (id, name, last_active);


load data local infile '/opt/bookings.csv' into table bookings
 fields terminated by ',' enclosed by ' '
 lines terminated by '\n'
 (id, date, movies);


load data local infile '/opt/movies.csv' into table movies
 fields terminated by ',' enclosed by ' '
 lines terminated by '\n'
 (title, rating, director, id);
EOF

echo -e  "The database 'mydb' is created, table 'users', 'bookings', 'movies' are created"


#Remove proxy deployment.yaml
#kubectl delete -f proxy.yaml

#Build and push images of our microservices
docker build --no-cache -t  gcr.io/${PROJECT_ID}/users ./users
docker push gcr.io/${PROJECT_ID}/users

docker build --no-cache -t  gcr.io/${PROJECT_ID}/bookings ./bookings
docker push gcr.io/${PROJECT_ID}/bookings

docker build --no-cache -t  gcr.io/${PROJECT_ID}/movies ./movies
docker push gcr.io/${PROJECT_ID}/movies


#Deploy microservice application
export PROJECT_ID
export INSTANCE_CONNECTION_NAME
envsubst < deployment.yaml | kubectl apply -f -

#Create services for deployment
kubectl create -f deployment-svc.yaml
