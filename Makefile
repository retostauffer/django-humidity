


exe="venv/bin/python3"
APP_NAME="djangohumidity"

run:
	${exe} manage.py runserver

migrate:
	#make killdb
	-rm -rf ${APP_NAME}/migrations/*
	# Clearing db first
	${exe} manage.py makemigrations ${APP_NAME} && \
	${exe} manage.py migrate --fake ${APP_NAME} zero && \
	${exe} manage.py migrate


npm:
	(cd djangohumidity/static && npm install)

venv:
	virtualenv -p python3 venv
	#source venv/bin/activate
	venv/bin/pip3 install -r requirements.txt


.PHONY: populate
populate:
	bash cleardb.sh
	make migrate
	${exe} manage.py shell < populate.py


shell:
	${exe} manage.py shell
