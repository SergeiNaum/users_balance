docker_build:
	docker build -t users_balanse .

docker_start:
	docker run -d --env-file ./docker/env/.env -p 8000:8000 --rm --name users_balanse sergeynaum/users_balanse

docker_stop:
	docker stop users_balanse

dev:
	./manage.py runserver