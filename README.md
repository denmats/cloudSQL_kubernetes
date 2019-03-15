# Enable the Cloud SQL Admin API in your project! 
# run script start.sh

sh start.sh

# that's it.







# Fully automated script for deploying the python 'microservices' application: 
        - the script will set service account with according roles and permissions,
	- create two secrets,
	- create cloud sql instance,
	- create user 'proxyuser' to manage the cloud sql,
	- create cluster,
	- create database 'mydb' with three tables users, bookings, movies,
	- fill them with data from csv files,
	- create deployment microservices (using a little changed Jan's deploy-deployment-pods.yaml)
	- create services for the deployment
 
#(link to Jan's branch python-mysql https://gitlab.com/itacademywroclaw/microservices.git)
	
	
