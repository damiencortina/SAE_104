#!/bin/bash

# start docker network
docker network rm network
docker network create network

CONTAINER_NAME="miambiodb"
docker stop ${CONTAINER_NAME}
docker rm ${CONTAINER_NAME}
docker run --name ${CONTAINER_NAME} --network network -p 3307:3306 --env MARIADB_USER=miambio --env MARIADB_PASSWORD=getmemycarrots --env MARIADB_ROOT_PASSWORD=my-secret-pw --env MARIADB_DATABASE=miambio --mount type=bind,src=./sql_projet.sql,dst=/docker-entrypoint-initdb.d/miambio.sql mariadb:latest