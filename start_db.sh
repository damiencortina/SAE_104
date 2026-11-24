#/bin/bash
docker build -t db_sae_104 .
docker rm db_sae_104
docker run -d --name db_sae_104 -p 8080:3360 db_sae_104
docker start db_sae_104