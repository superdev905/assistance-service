#/bin/bash!
docker context use default
docker-compose --file docker-compose.test.yml up --build
docker tag assistance-service-prod_assistance-api cchcprod.azurecr.io/assistance-prod:latest
docker push cchcprod.azurecr.io/assistance-prod:latest
docker context use azurecontext
docker compose --file docker-compose.prod.yml up --build 