# notes in lrn_django_01 -> django_notes.md
# to run project
## start and stop docker container, services and network
docker compose up
in browser: http://localhost:8000/ or 127.0.0.1:8000
docker compose down

or:
python manage.py runserver 0.0.0.0:8000 in docker container to see initial empty django dev server home screen

## Test
bash: docker-compose run --rm app sh -c "python manage.py test -v 2"

## validate django web browser running
localhost:8000/admin

## API Swagger
http://localhost:8000/api/docs



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

### To setup a second device
1. install docker desktop
2. clone project > git clone
3. replicate .env files
4. build and start containers > docker compose up --build
5. check no errors - check django is running
6. check or run migrations (see log info in docker desktop)
7. if needed clear the DV volume and manually re run migrations (see s48 down in .md)
8. Create django super_user (see s52 down in .md)
  -  bash: docker-compose run --rm app sh -c "python manage.py createsuperuser"

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

## test and lint:
bash: docker-compose run --rm app sh -c "python manage.py wait_for_db && flake8"
bash: flake8 .
2026 Modern Tool -> Ruff (does not have dependencies)
ZAG -> Validate how to setup RUFF instead of flake8 for alpine
### RUFF Setup
*setup
  - pip install ruff
  - ruff check .
  - ruff check --fix . (auto fix lint and formatting)

*exclude
```toml
[tool.ruff]
# Files and directories that Ruff should completely ignore
exclude = [
    ".git",
    "__pycache__",
    "build",
    "dist",
    "venv",
    ".venv",
    "*/migrations/*",  # Excludes all Django auto-generated migration files
]
# Optional: You can also specify your line length rule here
line-length = 119
```
option 2 - standalone ruff.toml
```toml
# Files and directories that Ruff should completely ignore
exclude = [
    ".git",
    "__pycache__",
    "build",
    "dist",
    "venv",
    ".venv",
    "*/migrations/*",
]

line-length = 119
```

#### RUFF in DOCKER ALPINE
ZAG: validate how to install in docker image of alpine linux
Gemini:
To install Ruff inside an Alpine Linux docker image, you can use pip install ruff just like any other Python package.However, because Alpine uses a lightweight C library (musl instead of glibc), Python packages with compiled binaries (like Ruff, which is written in Rust) historically required heavy build tools to compile from source. Fortunately, the Ruff team now publishes pre-compiled musllinux wheels, meaning it installs almost instantly without needing a full Rust compiler in your container.Here are the two ways to set it up in your Dockerfile:

1. Option 1: The Modern & Clean Way (Using pip)Simply add ruff to your requirements.txt file or install it directly in your Dockerfile.

```dockerfile
FROM python:3.11-alpine3.19

# Upgrade pip to ensure it can find the modern musllinux wheels
RUN pip install --no-cache-dir --upgrade pip

# Install ruff (it will automatically download the pre-compiled Alpine wheel)
RUN pip install --no-cache-dir ruff

# ... the rest of your Django setup
```

2. Option 2: The Multi-Stage Way (Best for keeping production images tiny)If you only want Ruff during development or testing and want to keep your final production image as small as possible, you can copy the pre-built binary directly from Ruff's official Docker image:

```dockerfile
FROM python:3.11-alpine3.19

# Copy the pre-compiled ruff binary straight into your path
COPY --from=ghcr.io/astral-sh/ruff:latest /ruff /usr/local/bin/ruff

# Now you can run 'ruff' anywhere in this container without installing it via pip!
```

3. 
A Common Gotcha for Junior Devs on Alpine ⚠️If your project uses older Python packages that don't have modern Alpine wheels, your build might freeze or fail because it's trying to compile from source. If that happens, you need to temporarily install Alpine's build essentials before running pip install:

```dockerfile
RUN apk add --no-cache --virtual .build-deps gcc musl-dev python3-dev libffi-dev \
    && pip install --no-cache-dir -r requirements.txt \
    && apk del .build-deps
```
(Since Ruff has native musl support, you won't need this block just for Ruff [1]—but keep it in mind for your other Django dependencies!)

### Database Migration
bash: python manage.py makemigrations
bash: python manage.py migrate
Run after wait_for_db - if there is no new migrations it just moves forward
Added migrate to Docker compose so it runs migrations after waiting for db to start
Added wait_for_db to checks.yml so it also waits for DB ready before running tests

## Django User model config - custom - Session 45
*default user model 
  - uses username instead of email
  - not easy to customise
* Reco: 
  - create a custom model for new projects
  - set custom model before running migrations
  - Base on AbstractBaseUser and PermissionsMixin Classes

* Common issues:
  - Run migrations before setting custom model
  - Typos in config (settings.py, etc)
  - Indentation in manager or model

* Steps:
  - Create model (AbstractBaseUser + PermissionsMixin Classes)
  - Create custom manager
  - Set AUTH_USER_MODE in settings.py
  - create and run migrations

### Design - fields
* user model:
  - email (EmailField)
  - name (CharField)
  - is_active (BooleanField)
  - is_staff (BooleanField)

* user model manager:
  - used to manage objects
  - Custom logic for creating object
    - hash password
  - used by django CLI
    - create superuser

* BaseUserManager (default that comes from django)
  - useful helper methods
    - normalize_emails
  - Methods to define ourselves
    - create_user
    - create_superuser

#### Code
##### s47 test_models.py
- core/tests/test_models.py
- test: bash: docker-compose run --rm app sh -c "python manage.py test -v 2"
  - first test run fails: missing pos arg 'username' (which is in default django user model) - ok

##### s48 models.py
Steps:
- core/models.py
- modify settings.py
  - At bottom of file add: AUTH_USER_MODEL = 'core.User'
- make migrations
  - bash: docker-compose run --rm app sh -c "python manage.py makemigrations"
  - check that core/migrations/0001_initial.py is created
- run migrate
  1. if already run migrate before: error -> Exception: Inconsisten Migration history
  2. Need to clear the volume first to erase existing DB
    - docker volume ls
    - find: lrn_django_api_dev-db-data
    - delete: docker volume rm lrn_django_api_dev-db-data
    - if error volume in use: bash: docker compose down to shut down container and volume
  3. run directly this step if migration has never been run before. Otherwise go to step 1
    - bash: docker-compose run --rm app sh -c "python manage.py wait_for_db && python manage.py migrate"
    - chek that migrations run ok - core.0001_initial should be in the list
  - run test:
    - bash: docker-compose run --rm app sh -c "python manage.py test -v 2"

##### s49 feature to normalize user email
1. core/tests/test_models.py > code to test normalization
2. test the test to see it fails
    bash: docker-compose run --rm app sh -c "python manage.py test"
3. add email=self.normalize_email(email) to core/models.py

##### s50 feature to require emsil address
1. core/tests/test_models.py > code to test required
2. test the test to see it fails
  bash: docker-compose run --rm app sh -c "python manage.py test"
3. add code if not email: raise ValueError('email required') to core/models.py
  
##### s51 add feature superuser functionality
similar to s50

##### s52 Test user model
steps:
1. docker compose up
2. localhost:8000
3. localhost:8000/admin
4. bash: docker-compose run --rm app sh -c "python manage.py createsuperuser"
5. email -> admin@example.com / pass -> p underscore 123
6. If you forget user, need to clear DB or run createsuperuser
if it runs ok: username should be email - credential email + pass

## Django Admin setup - Section 10

### Config
1. enable per model in admin.py
  - fieldset
  - Readorder
  - field display
  - Readonly field, etc

### Code Setup
* core/tests/test_admin.py - session 55
1. setUp() - modules required for unittest setup for admin - exception with camelCase
2. test_user_lists
3. test that test fails; python manage.py test 
3. or to test specific module use dot notation: python manage.py test core.tests.test_admin 

* list the users - session 56
* core/admin.py
reverse > admin:core_user_changelist

*edit_user_page - session 57 # Need to fix it as we changed the username as key user id field for user email
* core/admin.py
reverse > admin:core_user_change
3. click in user email to go to edit user page
4. Get FieldError at /admin/core/user/1/change 1>user.id
5. test the test should generate the same error 'FieldError'
6. code customization to UserAdmin model to support model without username
  - fieldsets = (..  )  see in code -> overrides 'username' which does not exist
  - from django.utils.translation import gettext_lazy as _
    This integrates with django translation system so _ translates the text // Good practice if in the future need to translate pages
    We need it to translate the values and create section titles for the data groups of the edit user page (Personal Info, Permissions, Important dates, None)

  *add user page - Session 58
  similar to previous

# API design Sections  
## API Documentation Section 11 s59
need to document:
- Endpoints
- Supported methods (Get, Post, Put, Patch, Delete)
- Payload format (inputs)
  - parameters
  - Json Content format
- Response format (output)
- Authentication process

### Options to create documentation
* Manual
  - Word Doc
  - Markdown
* Automated
  - use metadata from code
  - Automate generation of docs
  - Tools:
    - DRF Django Rest Framework

#### Tools / Libraries
* DRF Django Rest Framework
  - drf-spectacular - OpenAPI 3.0 ok 2026
    - important to name with doc strings the code as is the base to 
    - Generate Schema file
    - Parse the schema to GUI
  - serve swagger with API
  - modern way (use built-in template views)?
    - drf-spectacular render Swagger UI and ReDoc natively
    - Expose 3 endpoints
      - Raw YAML/JSON schema
      - Interactive swagger UI
      - clean ReDoc reader

#### Tool setup
* drf-spectacular
  - add to reqs.txt
  - re build container: docker-compose build
  - check for errors, validate with pio list
  - configure in settings.py
    - INSTALLED_APPS > 
      - 'rest_framework'
      - 'drf_spectacular'
    - ADD TO BOTTOM > defines to django the schema to use
      - REST_FRAMEWORK = {'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',}
  - cofigure app/urls.py > see code import and config paths:
    - from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

### Swagger SIDECAR Pattern [GEMINI]

The modern way to serve the OpenAPI 3 schema generated by drf-spectacular is to use its built-in template views. You don't need external HTML templates or third-party UI managers; drf-spectacular renders Swagger UI and ReDoc natively using CDN-hosted assets.

For a modern, professional API setup, you should expose three endpoints: the raw YAML/JSON schema, the interactive Swagger UI, and the clean ReDoc reader.

Here is the cleanest production-ready implementation you can teach your junior developer:

#### 1. The Core URL Routing (urls.py)

Add the following to your main urls.py file. This architecture splits the raw data definition from the user interfaces.
```python
from django.urls import path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

urlpatterns = [
    # 1. The Raw Schema Endpoint (Generates the JSON/YAML file)
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    
    # 2. Swagger UI (Interactive, great for quick developer testing)
    path('api/schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    
    # 3. ReDoc (Clean, highly readable, great for external stakeholders)
    path('api/schema/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]
```
#### 2. Recommended Settings (settings.py)
To ensure the views load reliably and present the data properly, configure the SPECTACULAR_SETTINGS dictionary in your settings file:
```python
SPECTACULAR_SETTINGS = {
    'TITLE': 'Your Project API',
    'DESCRIPTION': 'Comprehensive API documentation for our modern Django application.',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,  # Hides the documentation endpoints themselves from the docs
    
    # Modern UI Optimization:
    'SWAGGER_UI_DIST': 'SIDECAR',   # Optional: See note below regarding assets
    'SWAGGER_UI_FAVICON_HREF': 'SIDECAR',
    'REDOC_DIST': 'SIDECAR',
}
```

#### Junior Developer Pro-Tip: The "Sidecar" Pattern

By default, drf-spectacular loads the JavaScript and CSS for Swagger and ReDoc from a remote CDN (unpkg.com). In modern setups—especially closed network enterprise environments or high-security production environments—relying on a CDN can cause the UI to break if the internet is flaky or if strict Content Security Policies (CSP) are active.

To serve these static assets locally and securely without downloading files manually:
1. Have your junior run: pip install drf-spectacular-sidecar
2. Add 'drf_spectacular_sidecar' to your INSTALLED_APPS.
3. Set the 'SWAGGER_UI_DIST': 'SIDECAR' configurations as shown in the settings code above.
 
Django will now treat the UI assets as standard local static files, which can be collected using python manage.py collectstatic.


## Build User API -Section 12 s64
### API functions:
- User registration
- Creating Auth Token
- Viewing/updating profile

### Code Setup
- user/create
  - POST register new user
- user/token
  - POST > new token (receives userid and pwd returns token )
- user/me
  - PUT/PATCH - update user profile
  - GET - retrieve user profile

#### create new django app for user API
1. bash or docker compose: python manage.py startapp user
2. clean up files
  - migrations > all migrations consolidated in core app
  - admin > idem
  - models > idem
  - tests > create subfolder tests/ (remember to add __init__.py)
3. in app/settings.py
  - add user app to INSTALLED APPS
4. create user endpoint s67
  - create user/tests/test_user_api.py
  - validate test fails: python manage.py test user.tests.test_user_api (fails on NoReverseMatch 'user')
5. Create user serializer: user/serializers.py s68
  - serializer converts json objects to/from python objects
  - recives from json, validates type, converts to python object or model in actual DB
6. Create View that uses the serializer: users/views.py
7. connect URL to view
  - create user/urls.py
  - connect view in app/urls.py (import inlude, add path in urlpatterns)

## create authentication api s69
### Types of Authentication
* Basic
  - Send http auth with every request you make including user name and pwd > bad
* Token
  - use a token in the HTTP header for every request
  - Balance of simplicity and security
  - OOB support by DRF
  - support by most clients
* JWT Json Web token
  - Access and Refresh Token > More Advanced
  - Similar to Token (Token in HTTP header for every request)
  - Requires more libraries / dependencies
* Session
  - Use cookies > common for authentication websites


#### Token auth how it works
1. Create token (POST username/password)
2. Store token on client (Session or Local Storage, Cookie, Database)
3. Every request to server must include token in http headers

Pros:
1. Supporte OOB by django
2. Simple to use
3. Supporte by all clients
4. Avoid sending username/password each time

cons:
1. Token needs to be secure on the client side (risky in a shared device)
2. Requires a database for the requests (not an issue unless you have to authenticate millions of users)

Logging out
* happens on the client side
* deletes the token

Why no logount API endpoint?
* unreliable (client can't logout if: user deletes the app (while logged in), or erases session cookies or loses internet access)
* Not useful on API (unless you have a specific use case)

### password encryption setup?
- in the admin/user/change page under password is the algorithm, iterations and salt info.
- algorithm: pbkdf2_sha256 iterations: 260000 salt: vL3zSL...

By default, Django handles this automatically using PBKDF2. If you want to change the default algorithm (e.g., to Argon2 or Bcrypt), you override the setting in your settings.py. Django always uses the first hasher listed in the array to hash new passwords, while the remaining entries are used to verify older, existing passwords.

For example, to use Argon2 as your primary hasher, add this to your project configuration:

```python
# settings.py

PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.Argon2PasswordHasher",  # First entry = Default for new passwords
    "django.contrib.auth.hashers.PBKDF2PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher",
    "django.contrib.auth.hashers.BCryptSHA256PasswordHasher",
]
```

### How to Revoke tokens
find out if using JWTs, or DRF (Database Tokens), or django-rest-knox (Enhanced Database Tokens)

Knox is a highly recommended alternative to standard DRF tokens because it securely hashes tokens in the database and natively supports multiple logged-in devices per user. It includes and API endpoint to revoke current token (logout) or revoke all tokens assigned to that user (log out all devices)

#### For DRF: (Standard Database Tokens)
If you are using DRF’s built-in rest_framework.authtoken, tokens are stored directly in the database. "Revoking" a token means deleting it from the database.

DRF expects you to use your login/logout architectural patterns to manage this. However, it takes very few lines of code to write your own custom method and endpoint.

##### Implementation - Funciona pero no documenta OK
ZAG: solo devuelve el mensaje de detail como response y status 200 (buscar como devolver el user email??)
ZAG: Buscar como crear un revoke que un admin pueda aplicar a un usuario determinado.
ZAG: Crear el unittest
Create a custom API view that deletes the token tied to the current requesting user.


```python
# ZAG: BY GEMINI - TESTED ok
# views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import extend_schema, OpenApiResponse
from rest_framework.permissions import IsAuthenticated

@extend_schema(
    request=None,  # Tells Swagger that no request body / serializer is required
    responses={200: OpenApiResponse(description="Successfully logged out. YEAH")}, # Optional: documents the response
)

class RevokeTokenView(APIView):
    """Logout the user by revoking/deleting their auth token."""
   authentication_classes = [authentication.TokenAuthentication]
   permission_classes = [IsAuthenticated]

    def post(self, request):
        """Delete the token associated with the current authorized user."""
        # request.auth holds the actual Token model instance when using TokenAuthentication
        request.auth.delete()
        return Response({"detail": "Token successfully revoked."}, status=status.HTTP_200_OK)
```

Map it in your urls.py:
```python
# urls.py
from django.urls import path
from .views import RevokeTokenView

urlpatterns = [
    path('api/auth/revoke/', RevokeTokenView.as_view(), name='revoke-token'),
]
```

#### Test code
In Django REST Framework, the best practice is to test that a valid authenticated request successfully deletes the token, and that trying to access a protected endpoint with that same token afterward correctly returns a 401 Unauthorized status.

```python
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework.authtoken.models import Token

LOGOUT_URL = reverse('user:logout')  # Change 'user:logout' to match your exact URL namespace/name
MANAGE_USER_URL = reverse('user:me') # The URL for your ManageUserView


class LogoutApiTests(APITestCase):
    """Test the logout/token revocation API endpoint."""

    def setUp(self):
        # Create a test user
        self.user = get_user_model().objects.create_user(
            email='test@example.com',
            password='password123',
            name='Test User'
        )
        # Create a database token for this user
        self.token = Token.objects.create(user=self.user)
        
        # Authenticate the API client using standard DRF Token Authentication
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)

    def test_logout_successful(self):
        """Test that posting to logout endpoint destroys the token."""
        # Check that the token exists in the database before the request
        self.assertTrue(Token.objects.filter(key=self.token.key).exists())

        # Make the POST request to logout
        response = self.client.post(LOGOUT_URL)

        # Assert correct status code and response payload
        self.assertEqual(response.status_value, status.HTTP_200_OK)
        self.assertEqual(response.data, {"detail": "Successfully logged out."})
        
        # Assert that the token was deleted from the database
        self.assertFalse(Token.objects.filter(key=self.token.key).exists())

    def test_cannot_access_protected_endpoint_after_logout(self):
        """Test that the token is invalid for future requests after logout."""
        # 1. Execute logout
        self.client.post(LOGOUT_URL)

        # 2. Try to make an authenticated request using the same client credentials
        response = self.client.get(MANAGE_USER_URL)

        # Assert that access is now denied
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_logout_unauthenticated_fails(self):
        """Test that unauthenticated requests to logout are blocked."""
        # Clear credentials to mimic an anonymous user
        self.client.credentials()

        response = self.client.post(LOGOUT_URL)

        # Assert that the endpoint is protected
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
```

💡 Code Breakdown
* self.client.credentials: This builds the Authorization: Token <key> header automatically for every request sent by that client instance until cleared.
* Token.objects.filter(...).exists(): Instead of relying purely on the HTTP status codes, this directly probes your database state to prove the backend target operation occurred safely.

What does your urls.py file look like for the user app? If you haven't mapped the route yet, paste it here so I can give you the exact path syntax that aligns with the reverse() routing lookup names used in the test.


### Code Setup Token API s70
1. Code the unitest in user/tests/test_user_api.py
2. Test that test fails to NoReverseMatch (correct any syntax errors in the test if any found in the error message)
3. Edit app/settings.py - add INSTALLED_APPS 'rest_framework.authtoken' > support for token auth
4. Edit user/serializers.py > import authenticate, gettext as _
  - create class AuthTokenSerializer and methods
5. Create view: user/views.py
  - import ObtainAuthToken
  - import api_settings
  - import AuthTokenSerializer
  - Add class CreateTokenView(ObtainAuthToken)
6. Edit user/urls.py - add token/ endpoint to URLPATTERNS
7. it was already included in app/urls.py in the previous s68 code
8. run unittest check

### Code Setup Manage User APIs72
1. code tests for manage user api
  - create class PrivateUserApiTests(TestCase)
2. code update user api > Edit user/serializers.py
  - add update method to class UserSerializer
3. code update user/views.py
  - import authentication
  - import permissions
  - add class ManageUserView
4. code update user/urls.py
  - add me/ endpoint > ManageUserView.as_view()
5. run tests
6. validate that django applies authtoken migrations (3)

### Test User API in Browser s74
1. re-start docker to have django apply migrations
2. swagger: http://localhost:8000/api/docs
3. Create a user > user > POST
  - can use json format or app/x-form-data
4 Get Token: - see them in django admin / tokens
dev 1: 5a9cdfb3c71c588035783644f11ce3214fd96943
dev2: 6f60fcea096f788b1b67b4b5c5f0d187057caf7f

5. Click Authorize > Token auth:
  - type: Token <token value without quotes> 
6. test /me endpoint
   - GET > simpler test
   - PUT -> replaces entire object
   - PATCH -> specific key value to change

## Recipe API Design Section 13
Features:
- Create
- List
- View Detail
- Update
- Delete

## Endpoints
* recipes/
    GET - List all recipes
    POST - Create recipe
* recipes/<recipe_id>/
    GET - View details of recipe
    PUT/PATCH - Update recipe
    DELETE - Delete recipe

## APIView vs Viewsets classes
* What is a View:
  - Handles a request made to a URL (coded functions)
  - Django uses functions
  - DRF uses classes
    - Reusable logic
    - You are allowed to Override behaviour
  - DRF also supports decorators
  - APIView and Viewsets are DRF base classes

* What is an API View:
  - Focused around HTTP methods
  - Class methods for HTTP methods
    - GET, POST, PUT, PATCH, DELETE
  - Provide flexibility over URLs and logic
  - Useful for non CRUDS APIs
    - Avoid for simple Create, Read, Update, Delete APIs
    - Great for Bespoke logic (ie: auth, jobs, external apis)

* What is a Viewset:
  - Focused around actions
    - Retrieve, list, update, partial update, destroy
  - Map to Django Models
  - Use Routers to generate URLs
  - Great for CRUD operations over models

## Coding Recipe API
### Models
1. TDD edit core/tests/test_models.py
  - import Decimal (default django class used for recipe price values)
  - from core import models ()
  - test to create a recipe
2. test the test to see it fail
3. edit core/models.py
  - import settings -> needed for field user in class Recipe
  - best practice to reference user model (settings.AUTH_USER_MODEL) to allow for user model changes in a single place vs hardcoded everywhere
4. Edit core/admin.py
    - add admin.site.register(models.Recipe)
5. run makemigrations (added recipe class table to models.py)
6. run tests again -v 2 (validate that migrates core_0002)

### recipe app and api listing s80
1. create recipe app: manage.py startapp recipe
2. remove unused files: 
  - migrations/
  - admin.py
  - models.py
  - tests.py 
3. add (add tests/ + __init__.py)
4. add app to INTALLED APPS in settings.py
5. TDD: recipe/tests/test_recipe_api.py
6. Test the test to fail (expect to fail in import serializers which are not created yet)
7. create recipe/serializers.py > ModelSerializer
8. Test again. It should fail to NoReverseMatch
9. Create recipe/views.py
10. Configure recipe/urls.py
  - DefaultRouter allows to automatically create routes for all options of the view
      router = DefaultRouter()
      router.register('recipes', views.RecipeViewSet)
    autogenerates URLs for the functionality enabled in the viewset (CRUD -> GET, POST, PUT, DEL)
11. add include to app/urls.py
12. Re run test and check it passes ok

### recipe api detail s83
1. TDD recipe/tests/test_recipe_api.py
  - import RecipeDetailSerializer
2. test that fails (no RecipeDetailSerializer)
3. Code serializer recipe/serializers.py
4. code recipe/views.py - need to override standard list viewset to add override for specific one for the detail endpoint
5. Code actual api call create recipe test
  - recipe/tests/test_recipe_api.py
6. Test should fail, to integrity error
  - we have not coded the view to set the authenticated user with the recipe (assign user_id FK to the recipe obj see s86 > def perform_create)
  - The viewset includes 90% of the functionality to reate a new object. It does not include the logic to set the object user to the authenticated user (see s86)

### recipe api functionality s86
1. Edit recipe/views.py
  - add def perform_create(self, serializer)
  Test should pass ok
  - Build additional tests s87
2. Test in APi browser s88

## TAGs API Design Section 14 s90
### Features:
* Add ability to add recipe tags
* Create model for tags
* Add tag API endpoints
* update recipe endpoint to suppor tags
  - adding and listing tags

### Data Model
* name : Name of the tag to create
* user: User who created/owns tag

### Endpoints:
* /api/recipe/tags
  - POST - Create tag
  - PUT/PATCH - Update tags
  - DELETE - Remove tags
  - GET - List available tags

### Code implementation Part 1
#### Create Tag data model s91
1. Create Test > core/tests/test_models.py
    - add create_user helper at top
    - add test_create tag
  - Test should fail to Attr Error: core.models no attribute 'Tag'
2. Create Tag class in core/models.py
  - add tag (many to many) to recipe class
  - add class Tag with FK to settgins.AUTH_USER_MODEL
  - Test should fail to missing migration > psycopg2 InvalidCursorName
3. run makemigrations > Run test, should pass ok
  - if it asks to delete test DB say yes (didn't close prpoperly in prev test)
4. Register tag model in core/admin.py

#### Create Tag listing API s92
1. TDD > recipe/tests/test_tags_api.py
  - Test should fail to 
2. Create tag serializer and Tag listing api > recipe/serializers.py
3. Add view: recipe/views.py
  - import mixins (Mix into a view to add additional functionality)
  - import model Tag
  - add TagViewSet(mixins.ListModelMixin, viewsets.GenericViewSet)
4. register api routes in recipe/urls.py
  - add router registration > router.register('tags', views.TagViewSet)
5. Test should pass ok

#### Code update/delete tag api s93
1. TDD -> detail tag url builder function + test_update_tag
  - Test should faild to NoReverseMatch
2. recipe/views.py > add mixins.UpdateModelMixin to class TagViewSet
  - Test should pass ok
3 repeat for delete op
  - Test fails in 405 != 204 // 405: Not Suppported status code
  - add in views.py > mixins.DestroyModelMixin
  - Test should pass ok

### Nested Serializers
* Serializer within a serializer
* Used for fields that are complex objects
* when using in class definition the nested class needs to be declare before the nesting class
* example  "tags" could be a nested serializer
```json
{
  "title":"Some title",
  "user": "Jeff",
  "tags": [
    {"name":"Tag 1"},
    {"name":"Tag 2"}
  ]
}
```
* Limitations
 - By default: Read Only - can read but can't create objects with nested serialzier
 - Can write custom logic to override the read-only limitation

### Code Implementation Part2
#### Create Tags with nested serializers s99
1. TDD > recipe/tests/test_recipe_api.py (instead of test_tag_api)
  - we are adding support to create recipes that include tags (create or use existing tags) in the create recipe process
  - Test should fail to count of tags 0!=2 (we did not create the create feature yet)
2. Create feature to create tag while creating recipe s100 recipe/serializers.py
  - Move TagSerializer class to the top as will be nested inside RecipeSerializer class
  - add method to override read-only limitation
    - def create(self, validated_data): (see code)
  - Test should pass ok
3. Feature to udpate tags assigned to a recipe s101
  - test should fail. not allowed to write nested fields
  - override method s102 > recipe/serializers.py
  - Test should pass ok
4. Test API with swagger / django admin

## Ingredients API Section 15 s105
### Tasks
* Ability to add ingredients to recipes
* Create model for ingredients
* Add Ingredients API
* Update Recipe endpoint
  - Create Ingredients
  - Manage Ingredients

### Data Model (similar to tags)
- Name: Name of ingredient to create
- User: User who owns ingredient

### Ingredients Endpoint
- /api/recipe/ingredients/
  - GET - List ingredients
- /api/recipe/ingredients/<id>/
  - GET - Get ingredient details
  - PUT/PATCH - update ingredient
  - DELETE - Remove ingredient
- /api/recipe/
  - PUT - Create ingredients (as part of recipe)
- /api/recipe/<id>
  - PUT/PATCH - Create or modify ingredients

### Code implementation notes
1. add model class Ingredient in core/models.py and many to many field to recipe class
2. TDD core/tests/test_models.py
3. run makemigrations
4. add model to admin page > core/admin.py
5. TDD recipe/tests/test_ingredients_api.py
6. Build IngredientSerializer > recipe/serializers.py (above recipe due to nesting)
7. Add IngredientViewSet in recipe/views.py
8. Register urls in recipe/urls.py
9. add features to create/manage recipes with ingredients TDD and code > 
  - recipe/tests/test_recipe_api.py
  - recipte/serializers.py

#### Refactor TagViewSet / IngredientViewSet
* Very similar code
* Refactor using inheritance
* see recipe/views_unrefactored.py

## Image API Section 16 s 121
### Tasks
* Handling static/media files
* Addind image dependencies
* Update recipe data model to support image field
* add image upload endpoint

### Endpoints
/api/recipes/<id>/upload-image/
  - POST - Upload Image

### Dependiencies for images
* Pillow # ZAG OK 2026 - fork of PIL (Python Imaging Library)
  - Requires in docker: zlib, zlib-dev // AND jpeg-dev

#### Other libraries (ZAG reserach 2026 Gemini)
  - pillow good for: general image editing (resize, crop, rotate, convert formats, draw basic text or shapes)
  - ZAG: OpenCV best for computer vision and video (real time object detection, face recognition, advanced image manipulation)
  - ZAG: NumPy / Scikit-image: scientific and mathematical analysis (images as arrays of numbers for data science or medical imaging)

### Setup dependencies s122 
1. dockerfile > linux packages needed to install and use the pillow library
2. requirements.txt > Pillow>=8.2.0,<8.3.0
3. docker compose build 

## Media and Static files in Django & Docker
* media: files uploaded at runtime (i.e. user upload recipe image)
* static: files generated on build (django and developer generated)
* django configuration settings.py
  - STATIC_URL - Base URL for static files to be served (ie: /static/static)
  - MEDIA_URL (ie: /static/media)
  - MEDIA_ROOT - Root on the file system to store the files (ie: /vol/web/media)
  - STATIC_ROOT (ie: /vol/web/static)
* Docker Volumes > stores persistent data
  - configure: /vol/web - store static and media subdirectories

### Mapping Django dev and Django Prod & Collect Static command S123
  - django command to gather all static files
  - run python manage.py collecstatic > Puts all static files into STATIC_ROOT in production

### Static files configuration s124
1. dockerfile
mkdir needs to be after django-user for file permission purposes. So the djang-user owns these directories
```sh
django-user && \
mkdir -p /vol/web/media && \ #-p creates all subdirs
mkdir -p /vol/web/static && \
chown -R django-user:django-user /vol && \ # chown change owner -R (recursive)
chmod -R 755 /vol # change mode: change permisions 755 
```
2. run: docker compose build
3. Update Docker-compose yml file
  * sets a volume to vol directory in docker image for persistent data under dev in local machine
  * add new volume under app:
    - dev-static-data:/vol/web
  * declare under volumes:
    - dev-static-data:
4. settings.py
```python
STATIC_URL = '/static/static/' # change existing one in settings.py
MEDIA_URL = '/static/media/'

MEDIA_ROOT = '/vol/web/media'
STATIC_ROOT = '/vol/web/static'
```
5. URL mappings to support using media files with dev server > app/urls.py
  - import static, import settings
  - if settings.DEBUG:...
  ```python
  from django.conf.urls.static import static
  from django.conf import settings # to retrieve the setting in the if DEBUG

  # to enable django dev to serve media files
  if settings.DEBUG:
      urlpatterns += static(
          settings.MEDIA_URL,
          document_root=settings.MEDIA_ROOT,
      )
```

## Modify recipe model to handle images s125
### Core Code implementation
1. TDD core/tests/test_models.py
2. core/models.py
  - import uuid, os > for file management functions
  - generate file path for new recipe image
  - add image field to Recipe Class
3. run makemigrations
4. validate test runs ok

### API code implementation s126
1. TDD recipe/tests/test_recipe_api.py
  - import tempfile, os
  - from PIL import Image
2. Code api upload feature s127
  - recipe/serializers.py -> image file upload serializer
  - recipe/views.py
    - change get_serializer_class (elif)
    - add actions via actions decorator @action -> add additional functionalities to standard viewset funcs like list, update, delete
      - add custom action: upload_image
  - settings.py
    - Enable image uploads to work thru browsable interface
    - SPECTACULAR_SETTINGS = COMPONENT_SPLIT_REQUEST: True 
3. Test in browsable interface
  - id of recipe
  - multipart/form-data to be able to upload image (DSC05176.jpg)
  - look for file in docker volume /media/uploads/recipe/{uuid}.jpg
  - localhost:8000/static/path should serve the image in browser
    - http://localhost:8000/static/media/uploads/recipe/c68966a0-f3e7-41e9-9be8-190bd6618343.jpg
  - added 'image'(to the 'descrption' list) to Serializers.py in RecipeDetailSerializer > recipe detail endpoint now returns the file name
4. PENDING: deleting the recipe does not delete the image from server/container

## Filterin in API Section 17 s130
### Tasks
* filter recipe by ingredients / tag
  - Find certain types of recipes based in the tags/ingredients assigned to the recipe
  - (ie: tag 'vegan', find all recipes with tag 'vegan')
* Filter tags / ingredients by assigned
  - filter a list of options to show to the user of ingredients or tags they want to filter by
  - (shows a list of tags and ingredients that are currently assigned to any recipe they own)
* Define OpenAPI parameters
  - Update documentation

### Example endpoints > query parameters
* Filter recipe by tag(s):
  - GET /api/recipe/recipes/?tags=1,2,3
* Filter recipe by ingredient(s):
  - GET /api/recipe/recipes/?ingredients=1,2,3
* Filter tag by assigned: (don't show any tags that don't have a recipe associated with them)
  - GET /api/recipe/tags/?assigned_only=1
* Filter ingredients by assigned: (don't show any ingredients that don't have a recipe associated with them)
  - GET /api/recipe/ingredients/?assigned_only=1

### AutoGen OpenAPI Schema examples s
* some things need to be manually configured
  - Custom query params
  - Use DRF Spectacular extend_schema_view decorator

### Code implementation filtering recipes s131
1. TDD recipe/tests/test_recipe_api.py
2. recipe/views.py
* from drf_spectacular.utils import (
    extend_schema_view,
    extend_schema,
    OpenApiParameter,
    OpenApiTypes,
)
* add method to RecipeViewSet
* modify get_queryset
3. Add documentation changes - recipe/views.py Above class RecipeViewSet
```python
@extend_schema_view(
    # we are extending the info for the list endpoint
    list=extend_schema(
        parameters=[
            OpenApiParameter(
                'tags',
                OpenApiTypes.STR, 
                description='Comma separated list of tag IDs to filter',
            ),
            OpenApiParameter(
                'ingredients',
                OpenApiTypes.STR,
                description='Comma separated list of ingredient IDs to filter',
            ),
        ]
    )
)
```
4. code tag and ingredient filtering s 134 > recipe/views.py
in class BaseRecipeAttrVeiwSet
modify get_queryset to return the filtered query if tag or ingredient filter is requestd
Add @extend schema
5. Test
6. Test in browser

## Deployment Overivew
### Deployment options
https://www.youtube.com/watch?v=IoxHUrbiqUo
1. installing on a server - old school, complex to mantain
2. docker - Good por MVP - runs on a single server - difficult to scale
3. Docker orchestration server - AWS / Kubernetes / Serverless AWS Fargate
4. Serverless technology
  - Google Cloud Run / Google App Engine
  - AWS elastic Beanstalk / ECS Fargate

### Choice for this training
- MVP > Single VPS on AWS (EC2)
- Docker / Docker compose 
- Check development course terraform (udemy)

### Steps
1. Configure for deployment
2. Create server in AWS
3. Deploy App

### Detail Steps
1. Setup a proxy (reverse proxy)
2. Handle static/media files
3. Configuration for app in the server

* Components
- WSGI > Web Server Gateway Interface
- Persistent data (stateless) (no user files or DB)
- Reverse Proxy (http requests)
  - Best Practice for Django Apps > WSGI great at python code, but not at serving requests

1. nginx
2. uWSGI / equivalent to uvicorn
3. Docker compose

### Docker Compose Setup
- app service > runs WSGI
- Postgres DB (persistent data in DB)
- DB Volume: postgres-data
- Reverse Proxy: Nginx
- Static data volume: CSS, JS, Media Files

### Handling configuration
- Source code > Git
- Credentials
  - Env Variables
  - or Secret Managers
- Env Variables
  - create .env on server
  - set values in docker compose

### AWS Setup
- Security: lot of hackers for AWS accounts 
  - use MFA
  - use strong password
  - keep local machine secure
  - delete account when not in use

## Deployment implementation s139
### Dockerfile, run.sh, reqs.txt
1. config Dockerfile
  - copy scripts + chmod -R /scripts at the end
  - add to temp build: dependendy linux-headers (WDGI pagckage)
  - add /scripts: dir to the path: ENV PATH="/scripts:/py/bin:$PATH"
  - add CMD ["run.sh"] > the script that runs our application (can be overriden by docker compose) (ej dev server runs python manage.py runserver)
2. in local project root create /scripts/run.sh
- first line: #!/bin/sh (marks file as Shell script file)
- set -e (any cmd that fails, forces to crash the whole script)
- python manage.py wait_for_db (wait for DB to be available)
- python manage.py collectstatic --noinput (collects all static files and puts in static files directory > nginx )
- python manage.py migrate (for any pending migration to execute)
- uwsgi --socket :9000 --workers 4 --master --enable-threads --module app.wsgi 
    * runs uwsgi services
    * TCP Port 9000 (nginx connects here)
    * 4 wsgi workers (app runs on 4 workers // config based on CPUs in server) 
    * master: set UWSGI daemon or running app as master thread > main thing runnning on server
    * enable-threads (so that if app is using multi threads can be used thru WSGI)
    * module app.wsgi > run app/app/wsgi.py
3. in requirements.txt add uwsgi>=2.0.19,<2.1
4. run docker compose build - Check it completes with no errors

### reverse proxy config - nginx
1. create /proxy/default.conf.tpl in local project root folder (tpl = template)
- LISTEN_PORT -> env var
- location /static -> mapping to serve
- location / -> redirect to uwsgi {APP_HOST}:{APP_PORT} // nginx params // max file size 10MB (if need larger increase here)
2. setup uwsgi params /proxy/uwsgi_params -> all that django needs to work with nginx
- info: https://uwsgi-docs.readthedocs.io/en/latest/Nginx.html#what-is-the-uwsgi-params-file
3. create /proxy/run.sh > to start our proxy server
- envsubst inserts (pipes) env config (tpl) to final conf (reads env var values and pase them to nginx conf)
- nginx -g 'daemon off;' starts server on foreground (as is running in docker container, we want it to be the main app, and logs go into screen. It runs until server down or docker container stops )
4. docker file to run nginx as service for our project - s141
- create /proxy/Dockerfile
- nginx default image runs in root user. for security as we don't need root, we use the -unprivileged / More secure way to run app
- LISTEN_PORT=8000 servers listens on (can be changed)
- APP_HOST=app (name where wsgi service runs. Can be changed )
- APP_PORT=9000 (port for wsgi app, can be changed)
- touch creates an empty file to have permission to ovewrite content when populate conf.tpl in run.sh
- chown nginx -> gives ownership to nginx user to default.conf file
- chmod +x (execute permission to run run.sh)
5. test build docker file > see it builds ok
- CD to proxy
- docker build . (. local dir)

### Env Variables configuration
#### Plan
- store config in a file
- Retrieve values with docker compose
- Assign/pass to applications

#### implementation - how env files work
* .env file
  - DB_NAME=dbname
* docker-compose.yml
  environment:
    - DB_HOST=db
    - DB_NAME=${DB_NAME}
    - DB_USER=${DB_USER}
* retrirve from python:
  import OS
  MY_CONFIG = os.environ.get("MY_CONFIG")
* .env.sample -> .env file template (not .gitignored)

### Docker compose and .env for deployment s143 s144
1. create docker-compose-deploy.yml in project root folder
- restart: always  (if app crashes it restarts automatically by docker)
- proxy: reverse proxy server
  - context ./proxy (to use /proxy folder to build the image)
  - ports: 80(local machine>server):8000(host, inside container)
  - volumes: static-data: is a shared volume for app and proxy (is accessible to both)
2. create .env.sample in project root folder
  - list all variables needed to run service with temp test value. Change once deploy to server
  - template to use in server so don't need to manually type it in AWS deployment
3. Update app/app/settings.py to use .env values instead of hardcoded ones
  - SECRET_KEY - delete existing one =os.environ.get('SECRET_KEY', 'changeme')
  - toggle DEBUG mode (True in local dev, False when we deploy to prod)
    - DEBUG = bool(int(os.environ.get('DEBUG', 0))) (sets in env var 'DEBUG' 1:True 0:False)
  - ALLOWED_HOSTS = [] > Security, only allows access to specific hostnames
    - set comma separated list of hostnames
    - add below: ALLOWED_HOSTS.extend(filter(None,os.environ.get('ALLOWED_HOSTS', '').split(','),))
4. Update docker-compose.yml (dev compose) services>app>environment> - DEBUG=1
5. Run prod app in local machine to test it (simulation before actual deployment)
  - copy .env.sample to project_root .env (ignored bi .gitignore)
  - change port 80 to 8000 in docker-compose-deploy (my local machine proably uses 80 for something else)
  - cd to project root folder
  - run: docker-compose -f docker-compose-deploy.yml down
  - run: docker-compose -f docker-compose-deploy.yml up
6. Test in browser 127.0.0.1:8000/api/docs > swagger
7. change port back to 80 in docker-compose-deploy
8. Commit and push to git

#### Debugging: 
Error: run.sh not found in PATH (this was a typo in ENV PATH in docker file)
- IF NEED TO REBUILD DUE TO dockerfile error:
      - docker compose -f docker-compose-deploy.yml up --build

- recommended to delete and rebuild images: app and proxy

* How to validate the run.sh file inside the container

If you rebuild and still get an error like executable file not found in $PATH or No such file or directory, you can validate the script's presence, permissions, and format inside the container using these steps:
1. Start a temporary override container

If the container is crashing instantly upon boot, you cannot use standard docker exec commands. Instead, force the container to start using sh or bash as its entry point, bypassing your broken execution loop:
```bash
docker compose -f docker-compose-deploy.yml run --entrypoint /bin/sh <service_name>
```
(Replace <service_name> with the name of the service defined inside your docker-compose-deploy.yml file, such as app or web).

2. Check the File and Permissions

Once inside the interactive terminal of the container, run:
```bash
ls -la /scripts/run.sh
```

• Verify existence: Ensure the path matches exactly.
• Verify permissions: The output should show executable permissions (e.g., -rwxr-xr-x). If it doesn't, you need to add RUN chmod +x /scripts/run.sh into your Dockerfile.

3. Check for Line Endings (CRLF vs LF)

A very common hidden error—especially if you edit files on Windows—is line ending mismatches. Windows saves files with CRLF (\r\n), but Linux expects LF (\n). If run.sh contains Windows line endings, Linux will look for an interpreter named bash\r and fail with a misleading "file not found" error.
To check this inside the container, run:
```bash
cat -v /scripts/run.sh
```
If you see ^M at the end of every line, your file has Windows line endings. You will need to fix this in your text editor on your host machine (switch line endings from CRLF to LF) and rebuild again.

## AWS Deploy
### AWS Virtual Server Tasks
1. Create AWS account and user
2. Login to AWS console
3. Create a new vitual server
4. optional calculate cost [] with aws calculator - estimated USD 9/month
5. Connect to server via SSH
  - install apps, download and run code
6. in windows install SSH tool (Mac brings it by default)
  - Chocolatey (package manager) / Run choco install openssh

### Create AWS account s146
1. aws.com / create account
2. save root user safely
3. Create an IAM user with less privileges for dev-ops // IAM = Identity Access Manager
4. MFA for root user 2026 > Profile > Security > MFA > Register MFA device



#### IAM access 2026 Gemini
To configure IAM user that can log into the console and set up a virtual server running Docker:
Select the AWS managed policy named AmazonEC2FullAccess.

Because Docker runs inside a virtual server—which AWS calls an Amazon EC2 instance—the user needs permissions to provision and manage those servers. [2] 

##### Recommended IAM Configuration
When setting up this user in the [AWS IAM Console](https://console.aws.amazon.com/iam/), you should attach the following policies depending on how strictly you want to limit their access:

* AmazonEC2FullAccess (Recommended): This gives the user full permission to launch, stop, and terminate EC2 virtual servers, create Key Pairs for SSH access, and configure Security Groups (firewall rules) to allow traffic to your Docker containers.

* PowerUserAccess (Alternative): If this user will also need to use other container services like Amazon Elastic Container Service (ECS) or Amazon Elastic Container Registry (ECR) to store Docker images, PowerUserAccess allows full database, compute, and container application development permissions without allowing full account administration. [3] 

##### Mandatory Console Access Setup
When creating the user, ensure you check the box to "Provide user access to the AWS Management Console". You can then choose to auto-generate a password or assign a custom password for their initial login. [4, 5] 
##### Essential Step After Launching the Server
The IAM policy only grants access to control the AWS environment itself. Once the user launches an EC2 instance using the console, they will need to connect to the server's operating system via SSH or [AWS EC2 Instance Connect](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ec2-instance-connect-configure-IAM-role.html) to actually run the shell commands to install and configure Docker: [1, 2, 6] 

```bash
# Example commands the user will run inside the server terminal:
sudo apt-get update
sudo apt-get install docker.io -y
sudo systemctl start docker
```

##### Doc references
[1] [https://docs.aws.amazon.com](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/iam-policies-ec2-console.html)
[2] [https://docs.aws.amazon.com](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ec2-instance-connect-configure-IAM-role.html)
[4] [https://docs.aws.amazon.com](https://docs.aws.amazon.com/IAM/latest/UserGuide/console_controlling-access.html)
[6] [https://docs.aws.amazon.com](https://docs.aws.amazon.com/IAM/latest/UserGuide/access_controlling.html)


### Create SSH Keys
In local device
1. cd ~/
2. if not .ssh dir generate a key:
  - bash: ssh-keygen -t ed25519 -C "machinename" or "your_email@example.com" this last is the label
  - ZAG: ed25519 is the industry standard algorithm for security and speed
  - enter file where to save key: ~/.ssh/id_ed25519
  - enter password twice (empty for no password) 
3. copy key: bash: pbcopy ~/.ssh/id_ed25519.pub
4. Other option create a rsa algorithm key:
  - bash: ssh-keygen -t rsa -b 4096 > creates id_rsa and id_rsa.pub files
5. Cat to display and copy .pub content
6. in AWS Console - Search EC2 to go to EC2 Dashboard > Key Pairs > actions > import key pair
  - name: aguttero 2026 imac
  - paste content of public key
  - click: import key pair
7. validate keys are in ~/.ssh and store aws_rsa keys in there 

ZAG PENDING: 
review steps in AI Engineer Production s23 + MFA
- MFA
- Cost Monitoring


### Configure and connect to EC2 instance s148
1. EC2 Dashboard > Launch instance
  - name: recipe-api-dev-server / Number of instances: 1 (charges $ associated)
  - choose AMI: aws linux 2 AMI HVM - Kernel 5.10, SSD Volume type // 
  - 2026- Linux 20203 AMI VHM - Kernel 6.18
  - Instance type: (size) 2022 t2.micro // 2026 t3.micro
  - Choose Key Pair
  - Network Settings
    - We'll create a new security group called 'launch-wizard-1' with the following rules:
    - Allow SSH traffic from anywhere (can be restricted to specific IP)
    - Allow HTTP traffic from internet
  - Configure Storage
    - 2022: min 8GB Gp2 // 2026: min 8GB gp3 (gp3 should be cheaper than gp2) gp3 $0.08 GB/month
    - ZAG: Validate how much space do you need for your server and how to scale it and speed. (IOPS and MB/s)
    - ZAG: Valdiate backup / File System / Advanced details
  - click: Launch instance
  - Validate in EC2 dashboard > Instances - running instance
  - click instance id > Public IP
  - copy public IP address
2. Connect:
  - cd ~/.ssh
  - bash: ssh-add aws_id_rsa + password > Identity added...
  - bash ssh ec2-user@<paste aws ec2 instance ip>
  - Are you sure want to connecting: yes
  - should see Amazon Linux console propt and welcome image

#### add key for second device access to server and connect
1. Generate and copy new SSH key pair
2. Connect to EC2 server from first device
  - ssh ec2-user@<paste aws ec2 instance ip>
3. Add pub key to authorized_keys file
  - bash: nano ~/.ssh/authorized_keys
  - go to end of file
  - create new line and paste pub key
4. Test from second device: 
  - bash: ssh-add aws_id_rsa + password > Identity added...
  - bash ssh ec2-user@<paste aws ec2 instance ip>
  - yes

### Set Deploy Key s149 - Approve server to pull code from GitHub
1. Generate ssh key in EC2 instance
  - bash: ssh-keygen -t ed25519 -b 4096
  - leave pass blank
  - bash: cat ~/.ssh/id_ed25519.pub
  - copy content
2. Github > Project > Settings > Deploy Keys > add deply key
  - Title: server
  - Key: paste .pub key value
  - Don't need to allow write access (we only need to pull code from the server)
  - add key
  ZAG: Validate fine grain security > GitHub Apps
  
### Setup server dependencies
There is a cheat sheet in
https://github.com/LondonAppDeveloper/build-a-backend-rest-api-with-python-django-advanced-resources/blob/main/deployment.md#install-and-configure-depdencies
1. Install git: sudo yum install git -y (yum package manager)
2. install docker + permissions (see cheatsheet)as permissions changed need to logout (bash: exit) and ssh back again
3. bash: exit (logout)
4. bash: ssh ec2-user@<paste aws ec2 instance ip> (connect again)
5. install docker compose (see cheatsheet)
6. clone git project - Copy SSH url for the code clone / say yes to continue connecting
7. Validate clone ok with ls - should see lrn_django_api
8. git pull origin to pull updates
9. Copy .env.sample to .env > bash: cp .env.sample .env 
10. edit .env with vi or with nano
  - DB_NAME=recipedb
  - DB_USER=recipeuser
  - DB_PASS=securepassword (generate random pwd)
  - DJANGO_SEC_KY=(generate random key)
  - DJANGO_ALL_HOST= <host name of ec2 instance> Networking > Public IPv4 DNS
11. save ctrl+x > y // cat .env to validate

##### Generate random passwords from terminal:
###### POSTGRES
1. USE OPENSSL
* What it does: Generates a highly secure, 44-character random string.
* Why it's best for .env: The -base64 flag ensures the output uses standard letters, numbers, and basic symbols (+, /, =) that won't break your .env parsing rules or require complex URL encoding.
bash: openssl rand -base64 32

2. Using LC_ALL=C tr (Alphanumeric Only)
* If you want to completely avoid special characters (like / or $) that can sometimes cause parsing syntax errors in specific programming languages or Docker frameworks, run this:
bash: LC_ALL=C tr -dc 'A-Za-z0-9' < /dev/urandom | head -c 32; echo
* What it does: Pulls raw random data from your system's hardware entropy pool (/dev/urandom) and filters it down to a clean, 32-character alphanumeric password.

3. Crucial PostgreSQL .env Rules:

* Avoid the # Character: 
If your generated password accidentally includes a # symbol, some framework .env loaders will interpret everything after it as a code comment, cutting your password in half and causing "Access Denied" database errors. If you see a #, just run the generator command again.

*  Special Characters in Connection Strings: 
If your Docker container connects to Postgres using a full connection URI (e.g., postgresql://user:password@localhost:5432/db), certain characters like @, :, or / in your password must be URL-encoded (e.g., @ becomes %40). Method 2 above completely bypasses this headache.

###### DJANGO
For a Django SECRET_KEY, you need a cryptographically secure string that is completely unpredictable and at least 50 characters long.
Django secret key can safely contain a dense mix of alphanumeric characters and special symbols. In fact, Django's native key generator explicitly utilizes a specific set of 50 punctuation and alphanumeric characters (abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)).

1. Method 1: The Native Django Way (Recommended)
If you already have Django installed in your environment or Docker container, you can leverage Django's built-in utility. Run this single command:
bash: 
python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"


2. Method 2: Python Standard Library (No Django Required)
If you are setting up your .env file before configuring your Python environment or building your Docker image, you can use Python's built-in secrets module (available by default in Python 3.6+):
bash: 
python3 -c "import secrets; chars = 'abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)' ; print(''.join(secrets.choice(chars) for _ in range(50)))"

3. Method 3: Pure Shell Command (Fastest)
If you don't want to use Python at all, you can pull highly secure, random data directly from your system's hardware pool (/dev/urandom) using this command on your Mac or EC2 instance:
bash: 
LC_ALL=C tr -dc 'A-Za-z0-9!@#$%^&*(-_=+)' < /dev/urandom | head -c 50; echo


#### cheatsheet commands:
* Install Git:
sudo yum install git -y

* Install Docker, make it auto start and give ec2-user permissions to use it:
sudo amazon-linux-extras install docker -y or sudo yum install docker -y
sudo systemctl enable docker.service (enables docker servies on the system)
sudo systemctl start docker.service (docker info to see docker version doccker --help)
sudo usermod -aG docker ec2-user (gives ec2-user permission to run docker containers)

* Install Docker Compose:
sudo curl -L "https://github.com/docker/compose/releases/download/1.29.1/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose (installs docker compose)
sudo chmod +x /usr/local/bin/docker-compose (gives permission to execute the command)

* Use Git to clone your project:
git clone <project ssh url>

### run server s152

## TLS Certificate - Let's Encrypt
TLS requires a certificate — basically a cryptographically signed proof that "this server really is yoursite.com," issued by a trusted authority. Let's Encrypt is the free, automated service almost everyone uses now to get one. That certificate is what your browser checks before showing the padlock icon.
