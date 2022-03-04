#/bin/bash!
cp .env_prod .env
docker context use default
docker-compose --file docker-compose.image.yml up --build
docker tag assistance-service-prod_assistance-api cchcprod.azurecr.io/assistance-prod:latest
docker push cchcprod.azurecr.io/assistance-prod:latest
docker context use azureprod
docker compose --file docker-compose.prod.yml up --build