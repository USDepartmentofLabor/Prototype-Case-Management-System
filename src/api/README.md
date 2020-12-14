# EPS API

## Local Dev Setup

Local dev is done using Vagrant. Follow these steps to setup your local dev environment.

### VM Setup

1. Clone the report

    `$ git clone git@git.ascend.network:ilab-toolkit/eps-api.git`

1. Change into the application directory

    `$ cd eps-api`

1. Setup the vagrant box

    `$ vagrant up`

1. Log into the VM

    `$ vagrant ssh`

1. Create a local directory for file upload storage.

    `$ mkdir /tmp/storage_files; touch /tmp/storage_files/KEEPME`

1. Change into the application directory in the VM

    `$ cd app`
    
1. (Optional) Add the following to your `~/.profile` file. It will create the local file upload directory each time you restart the VM.

    ```shell script
    if [ ! -d "/tmp/storage_files" ]; then
        mkdir /tmp/storage_files; touch /tmp/storage_files/KEEPME
    fi
    ```

### Python/Flask Setup

1. Setup the python virtual environment

    `$ python3 -m venv venv`

1. Active python virtual environment

    `$ . venv/bin/activate`

1. Upgrade the virtual environments versions of pip and wheel.

    `$ pip install --upgrade pip wheel`

1. Install application requirements

    `$ pip install -r requirements.txt`

1. Run database migrations

    `$ flask db upgrade`

1. Seed development database. This will add the admin login

    `$ flask seed-db`

1. Create translations

    `$ pybabel compile -d translations`

1. Run the API

    `$ flask run --host=0.0.0.0` or `$ make run`

**Note**: When installing new modules with pip please run

`$ make freeze`

to update `requirements.txt`. Regular `$ pip freeze > requirements.txt` adds a line for pkg-resources version 0 which
Elastic Beanstalk does not like.

### Metabase Setup

Metabase was downloaded to the `~/app/metabase` directory as part of
`vagrant up`. Follow these steps to setup and run Metabase.

1. Change to Matabase directory

    `$ cd ~/app/metabase`

1. Run Metabase

    `$ ./run_metabase.sh`

1. Setup Metabase

    `$ ./setup_metabase.sh`

#### Metabase Setup Notes

- You may need to make the scripts for steps 2 and 3 executable. You
  can do this by executing the command `$chmod +x <script_name>`.
- Metabase does not have a quick command to set it up to start on system boot.
  So you'll need to run `$ ./run_metabase.sh` for each development session.
  
## Datasets

The API comes with Flask CLI commands to load development and demo datasets. They are  based on the standard
child labor surveys, labor inspection surveys and one standalone survey. The datasets can be loaded locally with
the following commands.

`$ flask load-dev-dataset <base_url>`

`$ flask load-demo-dataset <base_url>`

`base_url` is required

Note this will re-create the database. It runs the `$ flask recreate-db` and `$ flask seed-db`
commands before loading data.

### Loading in local dev environment

Run the following command to load the dev dataset locally.

`$ flask load-dev-dataset http://localhost:5000`

Run the following command to load the demo dataset locally.

`$ flask load-demo-dataset http://localhost:5000`

### Loading the EB based development API

This section assumes the following:

- You are accessing the EB instance from within your Vagrant VM.
- You have copied the security group pem file from [here](https://drive.google.com/open?id=1Q95WXkwclf35NI_B0J1TM8mX4taxt_Lu) to `$HOME/.ssh` in your Vagrant VM.
- You have your admin Toolkit AWS account setup as your AWS CLI default profile.

You must ssh into the EB EC2 instance for the API to run the load command. Run
the following commands to run the load on the dev API EC2.

1. ssh into the EC2 instance

    `$ eb ssh eps-dev-api --profile default`

1. Change to the directory of the currently deployed API

    `$ cd /opt/python/current/app`

1. Source the environment variables setup by EB

    `$ source /opt/python/current/env`

1. Activate the python environment used by the API

    `$ source /opt/python/run/venv/bin/activate`

1. Run the load against the dev API

    `$ flask load-dev-dataset https://eps-dev-api.dbmspilot.org`

1. Or load the demo dataset using the demo API

    `$ flask load-demo-dataset https://eps-demo-api.dbmspilot.org`

### Dataset Description

#### Surveys

The dev dataset comes with the following surveys.

- Standard Followup Form
- Standard Household Intake Form
- Standard Intake Form
- Age and Country Survey
- Productivity and Quality
- Employee Work Premises
- Health and Safety
- Workplace Fairness

#### Case Definition and Cases

The dataset defines one case definition. The case definition is based on a
household and its members. There will be one Household Intake and one Intake
and three Followup for each child in the household. The loader creates ten cases
and the data in the survey responses is completely random.

#### Standalone

The dataset includes one "Standalone" survey - Age and Country Survey. The
loader loads 100 completely random responses.

## Migrations

To create and run migrations run these commands.

`$ flask db migrate`

`$ flask db upgrade`

## Testing

The project has functional (implementation) and unit tests. This section
describes how to setup and run the tests.

### Setup

Testing depends on the same environment variables as the running application
does. However, pytest does not read a .env file. Therefore, you need to
manually set the environment variables.

One way to do this is using a .env script such as `test.env` to set the them.
Below is an example `test.env` file. Most variables are already filled out
except for email username and password and AWS keys. You will need to fill
those in before sourcing the script.

```bash
export FLASK_APP=application.py
export FLASK_DEBUG=1
export FLASK_CONFIG=testing
export FLASK_ENV=testing
export SECRET_KEY=''
export JWT_SECRET_KEY=''
export JWT_ACCESS_TOKEN_EXPIRES=86400
export JWT_BLACKLIST_ENABLED=true
export JWT_BLACKLIST_TOKEN_CHECKS=access,refresh
export SERVER_NAME=localhost:5000
export TEST_DATABASE_URL=postgresql:///api_test_pg
export DATA_DB_URI=postgresql:///data_test_pg
export MAIL_SERVER=email-smtp.us-east-1.amazonaws.com
export MAIL_PORT=587
export MAIL_USE_TLS=true
export MAIL_USERNAME=
export MAIL_PASSWORD=
export MAIL_SUBJECT_PREFIX='[EPS LOCAL TESTING] '
export MAIL_SENDER='no-reply@dbmspilot.org'
export AWS_ACCESS_KEY=
export AWS_SECRET_KEY=
export AWS_REGION=us-east-1
export WEB_APP_URL=https://eps-test.dbmspilot.org
export METABASE_URL=http://localhost:3000
export METABASE_USERNAME=ilabtoolkit@gmail.com
export METABASE_PASSWORD=admin1
export DATA_DB='data_test_pg'
```

### Environment Variables

| EnvVar | Default | Description |
|----------------------------|------------------------------------|-------------------------------------------------------------------------------------------------------------------------------|
| FLASK_APP |  | Flask env var pointing to the flask app instance to load |
| FLASK_DEBUG |  | Enables flask debug mode |
| FLASK_ENV |  | Specifies the flask environment to load |
| FLASK_CONFIG | default | Specifies which app configuration to load. Available configurations are, `development`, `testing`, `production`, `default` |
| SECRET_KEY | hard to guess string |  |
| JWT_SECRET_KEY | hard to guess string |  |
| JWT_ACCESS_TOKEN_EXPIRES | 900 | TTL for JWT access tokens |
| JWT_BLACKLIST_ENABLED | true |  |
| JWT_BLACKLIST_TOKEN_CHECKS | access,refresh |  |
| WEB_APP_URL | [http://localhost:4200](http://localhost:4200) |  |
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

### Test Database

The tests depend on a test database in the VM. For new VMs, the test database
is created when the VM is provisioned. If you already have your VM provisioned
and don't want to re-create it you can run the following command.

`$ sudo -u postgres createdb api_test_pg`

### Running the tests

Follow these steps to run the tests. These steps assume you are already ssh'ed
into the VM.

1. Change into the application directory.

    `$ cd app`

1. Start the python environment

    `$ source venv/bin/activate`

1. Set the testing environment variables

    `$ source test.env`

1. Run the tests

    `$ pytest -v`

### SQLAlchemy-Continuum note

The test database is re-created with the `test_db` fixture in the `tests/conftest.py` file. Changes to existing tables
are not recognized by SQLAlchemy-Continuum during this step. So when tables are changed (new columns etc), you must
go into the test database and manually drop the version table associated with the table that was changed. You only
need to do this the first time you try to run tests after making the database changes.

## Docker

This project is set up to run via docker-compose

### Docker Setup

First of all, install `docker` and `docker-compose` for your environment.
Once installed, navigate to the project folder and run `docker-compose up`.
This will build and start all containers for the project.

When setting up for the first time, also run `./init_docker.sh` to set up metabase and the local DB.

### Running commands

You can execute commands in running containers via docker-compose with the `run` command. The command format is
`docker-compose run <service> <command>`. Look in `docker-compose.yml` for available services.

As an example, to run the tests you can run `docker-compose run eps pytest tests/`

### Logs

In the terminal window, there will be a combined log output of all the running services. However, to get the logs
of a specific service you can use the `logs` command.

Use `docker-compose logs <service>` to give a full output of logs or use the `-f` flag
to follow log output continuously `docker-compose logs -f <service>`. You can omit `<service>` to get
logs from all services.

## File upload (AWS S3)

File upload is accomplished via flask-cloudy, which exposes several environment variables for configuration.
To set up for AWS S3 storage, use the following environment variables like so:

```.env
STORAGE_PROVIDER=S3
STORAGE_KEY=<Account access key>
STORAGE_SECRET=<Account secret key>
STORAGE_CONTAINER=esp-api-store  # Or other bucket name
```

## Internationalization (I18n) and Localization (L10n)

The API uses `flask-babel` for internationalization and localization. When checking out the project
from version control the first time, you need to manually compile translations. As listed in step 7 of
"Python/Flask Setup", to do so, run the following command:

`$ pybabel compile -d translations`.

When adding or changing string that need to be translated, you need to update
the translations files. To do so run the following commands:

1. Extract strings to be translated

    `pybabel extract -F babel.cfg -k lazy_gettext -o messages.pot app`

1. Create the translation files for the languages you are supporting.

    `pybabel update -i messages.pot -d translations`

1. Update the translation files

1. Compile the translations

    `$ pybabel compile -d translations`.

## Deployment

### Background

There are two environments in Elastic Beanstalk (EB) hosting the API:

- `eps-dev-api`: for a dev API
- `eps-demo-api`: for the demo API

Each are part of the `eps-api` EB application.

Each environment should map to one of our main branches. The mapping is:

| Branch | Environment |
|--------|-------------|
| `development` | `eps-dev-api` |
| `testing` | TBD |
| `master` | `eps-demo-api` |

The EB configuration has been setup to reflect this mapping but in case your
local configuration is not correct, the EB config.yml file is included here.

```yaml
branch-defaults:
  development:
    environment: eps-dev-api
    group_suffix: null
  master:
    environment: eps-demo-api
    group_suffix: null
environment-defaults:
  eps-dev-api:
    branch: development
    repository: null
  eps-demo-api:
    branch: master
    repository: null
global:
  application_name: eps-api
  default_ec2_keyname: eps-kp
  default_platform: arn:aws:elasticbeanstalk:us-east-1::platform/Python 3.6 running
    on 64bit Amazon Linux/2.9.2
  default_region: us-east-1
  include_git_submodules: true
  instance_profile: null
  platform_name: null
  platform_version: null
  profile: null
  sc: git
  workspace_type: Application
```

### Assumptions

This section assumes you have the AWS and EB CLIs installed, properly setup
and initialized and generally know how to use them. Quick highlights are below.

#### Setup AWS CLI

```bash
$ aws configure
AWS Access Key ID [None]: <AWS_ACCESS_KEY>
AWS Secret Access Key [None]: <AWS_SECRET_KEY>
Default region name [None]: us-east-1
Default output format [None]: json
```

- `<AWS_ACCESS_KEY>` is your AWS Access Key
- `<AWS_SECRET_KEY>` is your AWS Secret Key
- "Default region name" can be the AWS region of your choice
- "Default output format" can be the output format you prefer

#### Configure EB

Since the EB application and environments are already setup, you would just need
to run the following command to initialize EB.

```bash
$ eb init
Do you wish to continue with CodeCommit? (y/N) (default is n): n
```

### Deploying the API

You can deploy the API by entering commands directly at the command line or
by utilizing the project's Makefile.

**Note**: When deploying it is important to deploy the correct branch to the correct
environment. Make sure you are on the correct branch before deploying.

#### Deploying using the make

The project's Makefile contains targets to make deploying easier.

- `deploy-dev` to deploy to the dev environment
- `deploy-demo` to deploy to the demo environment

I.E., to deploy to the dev environment while on the development branch, run the
following command.

`$ make deploy-dev`

#### Deploying from the command line

The general command to deploy the API to a particular environment is:

`$ eb deploy <ENVIRONMENT_NAME> --profile default`

To deploy the dev environment from commandline run the following command.

`$ eb deploy eps-dev-api --profile default`

To deploy the demo environment from commandline run the following command.

`$ eb deploy eps-demo-api --profile default`
