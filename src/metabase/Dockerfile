FROM metabase/metabase:v0.37.3
COPY ./init.py .
COPY ./docker-entrypoint.sh .
RUN chmod a+x ./init.py
RUN chmod a+x ./docker-entrypoint.sh
ENV ADMIN_EMAIL="ilabtoolkit@gmail.com"
ENV ADMIN_USERNAME="admin"
ENV ADMIN_PASSWORD="admin1"
ENV MB_DB_TYPE="postgres"
ENV MB_DB_USER="postgres"
ENV MB_DB_PASS="paiV9Xae"
ENV MB_DB_HOST="postgres"
ENV MB_DB_PORT="5432"
ENV MB_DB_DBNAME="metabase_pg"
ENTRYPOINT ./docker-entrypoint.sh
#CMD /app/bin/start
