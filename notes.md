# notes in lrn_django_01 -> django_notes.md
# to run project
## start and stop docker container, services and network
docker compose up
in browser: http://localhost:8000/ or 127.0.0.1:8000
docker compose down

## Test
bash: docker-compose run --rm app sh -c "python manage.py test -v 2"

## validate django web browser running




# API COURSE - London App Developer -Build a backend REST API
## Course structure s3 - udemy london app

## Setup
1. create giihub repo
2. clone into local folder
3. setup docker hub credentials
  login -> hub.docker.com
  docker hub -> account settings
  -> Security -> Access tokens
  -> Generate new Token -> (so what needs to access has your authorization to access docker) Name so you can identify it
  -> Copy token
  -> Github repo -> settings -> Secrets and Variables -> Actions
  -> New repository secret -> Name: DOCKERHUB_USER / secret: dockerhub username -> Add Secret
  -> New repository secret -> Name: DOCKERHUB_TOKEN / secret: dockerhub token -> Add Secret
  * To revoke access just delete the secret in github or the token in dockerhub

## Docker compose
* run al commands through docker compose
i.e: docker-compose run --rm app sh -c "python manage.py collecstatic"
--rm removes the container once it finishes runing
app (name of the app)
sh - c passes in a shell command // command: "python manage.py collecstatic"

## Setup In the Code Editor
after cloning the github repo

### 1. generate requirements.txt
  Python version
  djangorestframework
  for this excerise:
  Django>=3.2.4,<3.3
  djangorestframework>=3.12.4,<3.13
  
### 2. create file: 'dockerfile' in root
* see dockerfile in project for full detail in commands
*FROM python:3.9-alpine3.13 alpine is a light unix version recommended for Docker, bare minimal very few dependencies
* ENV PYTHONUNBUFFERED 1 (to see messages in console without delay)
* Expose 8000 -> let us connect to python dev server running in docker 
* COPY neccesary files and empty dirs to be created in image 
* RUN with && avoids creating separate image layers if RUN commands are separate
* VENV to avoid having issues with base python version
* Add USer django-user -> Alpine To avoid using root for security reasons if user gets hacked, it has less privileges than root
* ENV py is the venv folder name - > py/bin to avoid typing py/bin/ etc...
* User -> Changes from root to django-user

#### warning found (use docker --debug to expand):
 - LegacyKeyValueFormat: "ENV key=value" should be used instead of legacy "ENV key value" format (line 4)


### create empty directories that need to be copied in step 2 (dockerfile)

### 3. create .dockerignore
```bash
# Git
.git
.gitignore

# Docker
.docker

# Python
app/__pycache__/
app/*/__pycache__/
app/*/*/__pycache__/
app/*/*/*/__pycache__/
.env/
.venv/
venv/
```

### 4. Build image
in project app root dir
start docker desktop
run:
```bash
docker build .
```

### 5. Create Docker Compose file (.yml)

#### 1. Write the file:
modern 2026 09: file name: compose.yaml instead of docker-compose.yml
```bash
version: "3.9" # -> Version of the Docker compose syntax [getting warning that is obsolete] -> 2026 09 modern way follows Compose Specification and does not use VERSION attribute

services: # Main services section
  app: # app related parameters
    build:
      context: . # Build docker file in current directory
    ports:
      - "8000:8000" # maps 8000 in local machine to port 8000 in docker container this is how to access the network when wan't to connect to the server image that is running
    volumes:
      - ./app:/app # Mapping directories in our system into docker container. To be able to update the local code changes into the app running in the docker conntainer in real time. Avoids having to rebuild the image with every code update
    command: > # The '>' avoids quoting hell and allows to split the single command line into multiple lines for easier readability
      sh -c "python manage.py runserver 0.0.0.0:8000" # command used to run the services: we can override when manually executing docker compose run commnand [by default runs this command: in compose file if there is no command specified in the bash: docker compose run <command> command ]
```

#### 2. Build the file
bash: docker-compose build -> runs this and follows steps from 'dockerfile'
In this case would create the same image as in point 4 (docker build .), but using the .yml as reference and adding info to the image name

### 5 Linting
#### Setup
You don't want to add packages in production that are only needed in dev server so:
* add flake8 to dev server
  1. create requirements.dev.txt file
    flake8>=3.9.2,<3.10
  2. in compose.yaml add:
    servies > app > build > args: > - DEV=true **true and false in lowercaps**
  4. in dockerfile add:
    COPY ./requirements.dev.txt /tmp/requirements.dev.txt
    ARG DEV=false > overrides to TRUE in .yml for dev (services>app>build>args)
  5.in dockerfile add: 
    Add to RUN a conditional if shell command scritp: 
    If DEV = true > is going to install the dev dependencies
    **in shell commands spaces between [] are imoportant see[ $DEV = "true" ]**
      ```sh script
      if [ $DEV = "true" ]; \
           then /py/bin/pip install -r /tmp/requirements.dev.txt ; \
       fi && \
    ```
  6. TEST to see if syntax is ok
      bash run: docker-compose build

  7. Add configuration file for Flake 8
    exclude > only run linting on code we created
    create app/.flake8 file

  8. run flake8 to test it runs ok 
    **should not generate errors as we did not create any code yet**
    run it through Docker Compose:
    bash: docker-compose run --rm app sh -c "flake8"
    2026 09 modern: bash: docker compose --rm app sh -c "flake8"
    * if you see no errors then it means it is ok

#### correcting some linting errors (example from post fix db race condition)
docker-compose run --rm app sh -c "python manage.py <wait_for_db> && flake8"
* F401 'django.contrib.admin' imported but unused -> add # noqa to have it ignored by flake8


### 6 Create Django project in docker image
```bash
docker-compose run --rm app sh -c "django-admin startproject app ."
```
It adds an app folder inside the local project_name/app folder with the django project.
The local folder is linked [bind] to the docker folder by the volumes: parameter in the compose.yaml file


### 7 Run Django Dev with Docker Compose and validate in browser to test is ok
```bash
docker-compose up
```

in browser: http://localhost:8000/ or 127.0.0.1:8000
in docker desktop > open in terminal > pip list, etc...
in console should see ping update
* To stop the server:
   detach > bash: docker compose down
   or > Ctrl + C

## Setup GitHub Actions
Common use case automations:
* Deployment -> In a separate Udemy Training
* Code linting
* Unit Test

### Triggers
Trigger -> Whenever code is pushed to Github
Job -> Run Unit Tests
Result -> Success / Fail

2000 Free minutes/month

### Github Actions Configuration
/Users/alejandroguttero/code_imac/lrn_django_api/app/app/tests.py
* create config file at: .github/workflows/[checks].yml [workflows/<any_name>.yml]
* set triggers
* Add steps for running testing and linting
* configure docker hub authentication
  docker hub allows to pull images to local machine (github actions pulls images)
  rates limits (amount images per time frame)
    anonymus 100/6h (ip based)
    authentication 200/6h
  docker login (through GitHub secrets)

#### workflows/checks.yml file
name: <name> -> process name
on: [push] -> trigger on pushed files

jobs: -> section to list automations
  test-lint: [process id]
    name: Test Lint [human friendly name]
    runs-on: -> Git hub runner(os where jobs will run) - ubuntu-24.04
      for Python you need something linux based like ubuntu
      check GitHub actions documentation:
        https://github.com/features/actions
    steps:
      - name: Login to Docker Hub
        uses: docker/login-action@v1 -> Premade action in Github repo
        with: -> premade action parameters
          username: ${{ secrets.DOCKERHUB_USER }}
          password: ${{ secrets.DOCKERHUB_TOKEN }}

      - name: Checkout
        uses: actions/checkout@v2 -> we need to Checkout code in orer to run the next step
      - name: Test
        run: docker-compose run --rm app sh -c "python manage.py test"
      - name: Lint
        run: docker compose run --rm app sh -c "flake8"

if any of the steps fails it will return a code other than Zero

Docker compose and docker install are already preinstalled in ubuntu-24-04 runner

#### Errors ! [remote rejected] refusing to allow a Personal Access Token to create or update workflow `.github/workflows/checks.yml` without `workflow` scope

You are getting this error because GitHub blocks your Personal Access Token (PAT) from modifying GitHub Actions workflow files unless it has been explicitly granted permission to do so.

Reco: 
sol 0: Use SSH Keys
sol 1: using fine-grained token
sol 2: using classic token

Docs:
Add a PAT:
https://stackoverflow.com/questions/68811838/refusing-to-allow-a-personal-access-token-to-create-or-update-workflow

Connect with SSH
https://docs.github.com/en/authentication/connecting-to-github-with-ssh

Udemy session 26 help:
https://www.udemy.com/course/django-python-advanced/learn/lecture/32238778#questions/21530138




#### Confgure dockerhub credentials in GitHub
* add, commit and push git files
* validate in repo > actions that there is a workflow

      - https://github.com/marketplace/actions/checkout

## TDD Test Driven Development
Create test first, develop logic after

### Testing in Django - See Udemy Overview Session 27
https://docs.djangoproject.com/en/6.1/topics/testing/
#### Framework tools:
Django Test Suite / Framework -> Based on the ´unittest´ library + django features
  * Test client - dummy web browser
  * Simulate authentication
  * temporary database
Django REST Frameworks also adds features
  * API test client

#### Test location
choose either: (can't use both)
  * tests.py added in each subapp
  * tests/ directory in main app
    * test modules start with test_
    * test directories must contain __init__.py file

#### Test Database
* Django creates a DB for tests and clears data for every single test by default (is possible to override if needed i.e. a specific dataset)

#### Test Clases provided by Django
* SimpleTestCase -> No DB integration -> useful when DB not needed -> saves time
* TestCase -> requires DB
```python
from django.test import SimpleTestCase
from django.test import TestCase
from subapp import views (where code to test resides)
```
##### steps
1. import test class
2. import objects to test
3. define test class
4. add test method -> def test_mmmmmm
5. setup inputs (values, edge cases)
6. execute code to be tested
7. check output

bash: python manage.py test
bash: docker-compose run --rm app sh -c "python manage.py test"

##### Verbose Test


bash: python manage.py test -v 2
bash: docker-compose run --rm app sh -c "python manage.py test -v 2"

The Verbosity Levels Explained
-v 0 (Silent): Minimal output. It hides everything except errors, critical failures, and the final summary.
-v 1 (Normal): The default mode. It displays simple dots (.) for success, F for failures, and E for errors.
-v 2 (Verbose): This is what you want. It prints the names of all tests being executed, along with setup notifications (like creating the test database).
-v 3 (Debug): Ultra-verbose. It shows absolutely everything from level 2 plus internal debug logs, raw SQL queries being executed, and mock server initializations.

### Mocking
Override or change behaviour of dependencies for test purposes
  To avoid unintended side effects
  Isolate code being tested

Why:
Avoid relying on external services
Avoid unintended consequences (ie send emails)
Speed up tests

How:
use uniitest.mock library
  MagicMock / Mock class - Replace real objects
  patch - Overrides code in tests

### Testing Web requests - see code for examples
uses django REST Framework APIClient
```python
from rest_framework.test import APIClient
```
* based on django TestClient
* Make requests
* Check result
* Override authentication

### Common test issues
* __init__.py in test dir
* indentation
* Missing test_ prefix for method
* ImportError -> tests.py and /tests dir

## PostgreSQL DB Configuration
### Architecture
Docker Compose
  Serv1: App -> depends_on DB service
  Serv2 : DataBase

Network

Volumes
* Maps a directory in container to a dir in local machine

### Setup in yml file - Session 34
DB_HOST=[db_serv_name] 'should match the service name for the db service image
ie:
  db:
    image: docker db image

DB_HOST=db

#### to test it:
bash: docker compose up

## Django DB configuration - Session 35
### Setup info needed in settings.py
Pull config values from env variables:
os.environ.get ('DB_HOST')
  Engine
  Hostname (ip or domain name for DB)
  Port number (default PostgreSQL 5432)
  Database Name
  Username
  Password
### Posgtres adapter for Django
Psycopg2 - will be deprecated -> use psycopg (3.1.12+)
psycopg2-binary (only good for dev, avoid for production)
ZAG: validate dependencies for psyscopg psycopg (3.1.12+)
#### psycopg2 dependencies: (udemy tutorial)
  C compiler
  python3-dev
  libpq-dev
equivalent packages por Alpine (trial and error / stackflow)
  postgresql-client
  build-base
  postgresql-dev
  musl-dev

Good Practice: delete packages that were needed for installation, but are not needed anymore for running

#### edit to setup postgres adapter psycopg2 in docker and Alpine image
dockerfile
requirements.txt
see session 35 in udemy
bash: docker compose build
Validate it builds ok (no errors)

### Django db config in settings.py  - Session 37
PostgreSQL connection settings:
https://docs.djangoproject.com/en/6.1/ref/databases/#postgresql-notes

udemy django v3:
import os

change default database from sqlite3 to Postgres -- see code

### fixing database race condition in docker - Session 38
ZAG: Validate how to do this in django v6
https://docs.djangoproject.com/en/3.2/howto/custom-management-commands/

add to django a wait for db ready custom django command (in core app) so that it starts just after the DB is ready so that Django does not crash in the startup process.

test wait_for_db command:
bash: docker-compose run --rm app sh -c "python manage.py wait_for_db"

test and lint:
bash: docker-compose run --rm app sh -c "python manage.py wait_for_db && flake8"

#### Core app creation django v3 - Session 39
* create core app
bash: docker-compose run --rm app sh -c "python manage.py startapp core"
delete uneeded files in core/
  - views.py
  - tests.py
create tests/ and __init__.py

* add core to settings.py installed apps list

* add core/management/commands/wait_for_db.py - Session 40
* add __init__.py to all subdirs

#### TDD process: Session 40 for test_commands.py & wait_for_db.py
0. build empty command
1. build empty unitest
2. fail unitest to prove that testing process work
3. code test to validate command
4. code command
5. test command

### Database Migration
bash: python manage.py makemigrations
bash: python manage.py migrate
Run after wait_for_db - if there is no new migrations it just moves forward



## TLS Certificate - Let's Encrypt
TLS requires a certificate — basically a cryptographically signed proof that "this server really is yoursite.com," issued by a trusted authority. Let's Encrypt is the free, automated service almost everyone uses now to get one. That certificate is what your browser checks before showing the padlock icon.
