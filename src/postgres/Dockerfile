FROM postgis/postgis:latest

ARG METABASE_USER_PASSWORD

COPY ./generate_init_sql.sh .
RUN bash ./generate_init_sql.sh
