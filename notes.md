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
1. generate requirements.txt
  Python version
  djangorestframework
  for this excerise:
  Django>=3.2.4,<3.3
  djangorestframework>=3.12.4,<3.13
  
2. create file: 'dockerfile' in root
* see dockerfile in project for full detail in commands
*FROM python:3.9-alpine3.13 alpine is a light unix version recommended for Docker, bare minimal very few dependencies
* ENV PYTHONUNBUFFERED 1 (to see messages in console without delay)
* Expose 8000 -> let us connect to python dev server running in docker  


## TDD Test Driven Development
Create test first, develop logic after

## TLS Certificate - Let's Encrypt
TLS requires a certificate — basically a cryptographically signed proof that "this server really is yoursite.com," issued by a trusted authority. Let's Encrypt is the free, automated service almost everyone uses now to get one. That certificate is what your browser checks before showing the padlock icon.
