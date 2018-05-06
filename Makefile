SHELL = /bin/sh

lint:
	pipenv run flake8
	pipenv run black --check .

black:
	pipenv run black .
