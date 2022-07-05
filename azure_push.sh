#/bin/bash!
#first one
#docker login azure
#second one
#docker context create aci azurecontext
#context change
docker context use default
#deploy on local to do docker image
docker-compose --file docker-compose.test.yml up --build
#image tagged
docker tag assistance-service_assistance-api-test cchcdev.azurecr.io/assistance-service:latest
# pushing image
docker push cchcdev.azurecr.io/assistance-service:latest
# workaround on azure acr login failed
#az acr login --name  cchcdev
#azure context
docker context use azuretest1
#deploying on azure
docker compose --file docker-compose.azure.yml up --build