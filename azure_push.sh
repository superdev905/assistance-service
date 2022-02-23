#/bin/bash!
docker context use default
docker-compose --file docker-compose.test.yml up --build
docker tag assistance-service_assistance-api-test cchcdev.azurecr.io/assistance-service:latest
docker push cchcdev.azurecr.io/assistance-service:latest
docker context use azurecontext
docker compose --file docker-compose.azure.yml up --build