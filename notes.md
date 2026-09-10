# notes in lrn_django_01 -> django_notes.md
# to run project


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

## In the Code Editor
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
```bash
version: "3.9" # -> Version of the Docker compose syntax

services: # Main services section
  app: # app related parameters
    build:
      context: . # Build docker file in current directory
    ports:
      - "8000:8000" # maps 8000 in local machine to port 8000 in docker container this is how to access the network when wan't to connect to the server image that is running
    volumes:
      - ./app:/app # Mapping directories in our system into docker container. To be able to update the local code changes into the app running in the docker conntainer in real time. Avoids having to rebuild the image with every code update
    command: >
      sh -c "python manage.py runserver 0.0.0.0:8000" # command used to run the services: we can override when manually executing docker compose run commnand [by default runs this command: in compose file if there is no command specified in the bash: docker compose run <command> command ]
```

#### 2. Build the file
bash: docker-compose build -> runs this and follows steps from 'dockerfile'



## TDD Test Driven Development
Create test first, develop logic after

## TLS Certificate - Let's Encrypt
TLS requires a certificate — basically a cryptographically signed proof that "this server really is yoursite.com," issued by a trusted authority. Let's Encrypt is the free, automated service almost everyone uses now to get one. That certificate is what your browser checks before showing the padlock icon.
