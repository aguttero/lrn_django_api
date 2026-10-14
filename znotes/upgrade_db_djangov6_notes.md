# upgrade from django V4 to v6 plan
1. find out current versions all dependencies
2. find out upgrade process
3. find out contingency process
3. execution
4. validation

## run commands
* 1st time deploy docker service:

* start app
sh: docker-compose -f docker-compose-deploy.yml up -d

* stop app
* sh: docker-compose -f docker-compose-deploy.yml down

* view logs
sh: docker-compose -f docker-compose-deploy.yml logs

* upgrade
- git pull
- Rebuild server image: 
  - sh: docker-compose -f docker-compose-deploy.yml build app
- Recreate and Restart without restarting dependiencies (db, proxy)
  - sh: docker-compose -f docker-compose-deploy.yml up --no-deps -d app


## Current versions
### commands to get env vars and data:
sh: printenv
sh: docker-compose logs
sh: docker-compose ps > list containers

* django version in docker:
- sh: docker exec -it <container_id_or_name> python manage.py --version

* docker container env values:
- Docker compose running:
  sh: docker container ls (container id, name, etc)
  sh: docker exec -it <id_or_container_name> printenv
  sh: docker-compose help
- sh: docker-compose ps (names, status, ports)
- sh: docker compose exec -it <nombre_del_servicio> printenv
  sh: docker-compose images (container, repo, tag, image)


- Docker compose not running:
-  docker run --rm <nombre_de_la_imagen> printenv


### Dev local machine version
docker: sh: docker --version: 29.1.3

### Requirements.txt 
* Prod:
requirements.txt
Django>=4.0.4,<4.1
djangorestframework>=3.13.1,<3.14
psycopg2>=2.9.3,<2.10
drf-spectacular>=0.22.1,<0.23
Pillow>=9.1.0,<9.2
uwsgi>=2.0.20,<2.1

* Dev:
requirements.dev.txt
flake8>=4.0.1,<4.1

### AWS EC2 2026 10 version
Linux:
  sh: cat /etc/os-release
  sh: uname -a
  Amazon Linux 2023.12.20260930
docker: sh: docker --version: 25.0.14


## Claude Prmpt
in your role of devops teacher to a junior developer. I need a conceptual plan and then a detailed execution check-list to migrate a kitchen recipe django rest api service which runs in docker in an aws ec2 server to the  current latests versions of django, docker,  apline linux, postgres, python, nginx proxy and python packages. The service is running over docker with django 4.0, django DRF 3.13, psycopg2 2.9, drf-spectacular 0.22, pillow 9.1, uswgi 2.0,  python 3.9-alpine3.13, postgres13.23-alpine, nginx 1.31.6, docker 25.0 and docker compose.
