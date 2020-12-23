# Prototype Case Management System

Prototype Case Management System

This document provides instructions on getting up and running with the CMS.
Additional, more detailed, documentation can be found:

* [Programmer's Guide](docs/programmers_guide/cms_programmers_guide.md)
* [User Manual](docs/user_manual/cms_user_manual.md)

## Development Environment Set Up

A development environment needs to provide the following:

* Docker
* Docker Compose

Note that other environments may be set up differently but verified steps are provided below.

### Using Docker

* Install Docker
* Install Virtualbox
* Clone repo
* from ```~/extended-prototype/```
* Start Docker machine using ```docker-machine start```
* Start Docker containers using ```docker-compose up```

### Setting up

First, build all the services with ```docker-compose build```
Then you'll want to run the migrations with ```docker-compose run eps flask db upgrade```
You can also need to initialize metabase with ```docker-compose run eps /eps-api/metabase/setup_metabase_docker_compose.sh```
or setup metabase manually by accessing `metabase.localhost` after you start the docker services in the next section

### Local Development

A local development environment can be built done using ```docker-compose up``` without any arguments.
With default arguments, the webapp is available in the browser at <https://localhost>.
The api is located at <https://api.localhost>.
Metabase is located at <https://metabase.localhost>

## API

### Creating and Activating the Python Virtual Environment

* from ```~/extended-prototype/src/api/```
* ```python3 -m venv venv```
* ```source venv/bin/activate```
* ```pip install -r requirements.txt```

### Starting the API for local development

The API is configured to run via docker-compose with default environment values
already provided. The API can be started independent of other components with
```docker-compose up eps```. This will start the api service along with its dependencies

### Testing the API

To set up the api for testing, either set the `FLASK_ENV` and `FLASK_CONFIG` environment variables to
`testing` in a `docker-compose.override.yml` file and run ```docker-compose run eps pytest /eps-api``` or
run ```docker-compose -f docker-compose.yml -f docker-compose.testing.override.yml run eps pytest /eps-api```.

### Development Data

To seed the application with development data, you can run
```docker-compose run eps flask seed-db```

You can also optionally do:
```docker-compose run eps flask load-impaq-dataset```
or
```docker-compose run eps flask load-dev-dataset```

## Web Application

### Running

The webapp can be ran from docker using ```docker-compose up www-angular```.
The application will be available on the browser at <http://localhost>.

**Note:** Running the webapp along with the nginx service (such as in ```docker-compose up```)
then the webapp will be available on port 443 with <https://localhost>

The web application can also be run manually with

* from ```~/extended-prototype/src/webapp/```
* ```npm install```
* ```ng serve --host 0.0.0.0```
* Runs @ <http://localhost:4200>

Doing so will allow for live reloading of the webapp upon changes to the source files

## Environment Variables

### EPS

| EnvVar | Default | Description |
|----------------------------|------------------------------------|-------------------------------------------------------------------------------------------------------------------------------|
| FLASK_DEBUG |  | Enables flask debug mode |
| FLASK_ENV |  | Specifies the flask environment to load |
| FLASK_CONFIG | default | Specifies which app configuration to load. Available configurations are, `development`, `testing`, `production`, `default` |
| SECRET_KEY | hard to guess string |  |
| JWT_SECRET_KEY | hard to guess string |  |
| JWT_ACCESS_TOKEN_EXPIRES | 900 | TTL for JWT access tokens |
| JWT_BLACKLIST_ENABLED | true |  |
| JWT_BLACKLIST_TOKEN_CHECKS | access,refresh |  |
| WEB_APP_URL | [http://localhost:4200](http://localhost:4200) | URL for the EPS web application |
| MAIL_SERVER | email-smtp.us-east-1.amazonaws.com | URL for email SMTP server |
| MAIL_PORT | 587 | Port SMTP server is listening on |
| MAIL_USE_TLS | true | Specifies whether SMTP should use TLS |
| MAIL_USERNAME | None | Username for application email account |
| MAIL_PASSWORD | None | Password for application email account |
| MAIL_SUBJECT_PREFIX | None | Email subject line prefix |
| MAIL_SENDER | None | Email sender field |
| METABASE_URL | [http://localhost:3000](http://localhost:3000) |  |
| METABASE_USERNAME | None |  |
| METABASE_PASSWORD | None |  |
| METABASE_AUTH_ID | None |  |
| METABASE_DB | 0 |  |
| METABASE_SECRET_KEY | None | The embedding secret key from Metabase. |
| STORAGE_PROVIDER | LOCAL | File upload storage provider |
| STORAGE_KEY | None | Cloud storage access key |
| STORAGE_SECRET | None | Cloud storage secret key |
| STORAGE_CONTAINER | /tmp | Cloud storage bucket. Storage folder path for `LOCAL` provider |
| STORAGE_ALLOWED_EXTENSIONS | txt,doc,docx,xls,xlsx,pdf,png,jpg,jpeg,md | Whitelist of allowed file extensions |
| DEV_DATABASE_URL | sqlite:///\<basedir>/eps-api-dev.sqlite | Only used in `development` configuration |
| TEST_DATABASE_URL | sqlite:///\<basedir>/eps-api-test.sqlite | Only used in `testing` configuration |
| PROD_DATABASE_URL | sqlite:///\<basedir>/eps-api.sqlite | Only used in `production` configuration |
| DATA_DB_URI | sqlite:///\<basedir>/data.sqlite | URI of the data database |
| DATA_DB | data_pg | Name of the data database |

### POSTGRES

Environment variables inherited from postgres docker image: [https://hub.docker.com/_/postgres](https://hub.docker.com/_/postgres)

### WWW-NGINX

| EnvVar | Default | Description |
|----------------------------|------------------------------------|-------------------------------------------------------------------------------------------------------------------------------|
| UPSTREAM_ANGULAR_URL | None | Internal URL for the webapp service instance |
| UPSTREAM_FLASK_URL | None | Internal URL for the api server instance |
| UPSTREAM_METABASE_URL | None | Internal URL for the metabase server instance |
| DOWNSTREAM_METABASE_URL | None | External URL for metabase |
| SERVER_URL | None | External URL for the api |
| WEBAPP_URL | None | External URL for the webapp |

Image based on nginx image: [https://hub.docker.com/_/nginx](https://hub.docker.com/_/nginx)

### METABASE

Environment variables inherited from metabase docker image: [Metabase Documentation:v0.37.4 / Operations Guide / Environment Variables](https://www.metabase.com/docs/latest/operations-guide/environment-variables.html)
