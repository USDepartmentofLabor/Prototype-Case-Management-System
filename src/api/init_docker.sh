#!/bin/bash

docker-compose run eps /eps-api/metabase/setup_metabase_docker_compose.sh

docker-compose run eps flask db upgrade
docker-compose run eps flask seed-db
