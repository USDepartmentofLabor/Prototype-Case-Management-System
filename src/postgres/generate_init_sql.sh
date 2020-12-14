#!/bin/bash

cat > /docker-entrypoint-initdb.d/init.sql <<EOF
CREATE USER metabase_pg_user;

CREATE DATABASE api_pg;
CREATE DATABASE api_test_pg;
CREATE DATABASE metabase_pg;
CREATE DATABASE data_pg;
CREATE DATABASE data_test_pg;

ALTER USER metabase_pg_user WITH encrypted password '$METABASE_USER_PASSWORD';

\c api_pg
CREATE EXTENSION postgis;
\c api_test_pg
CREATE EXTENSION postgis;

EOF
