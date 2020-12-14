FROM nginx:1-alpine

COPY ./docker-entrypoint.sh .
RUN chmod a+x ./docker-entrypoint.sh

EXPOSE 80

ENTRYPOINT ./docker-entrypoint.sh
# CMD ["nginx", "-g", "daemon off;"]
