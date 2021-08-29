



run:
	python manage.py runserver

migrate:
	python manage.py migrate

npm:
	(cd djangohumidity && npm install)

venv:
	virtualenv -p python3 venv
	source venv/bin/activate
	pip install -r requirements.txt:


.PHONY: populate
populate:
	-rm -r djangohumidity/migrations
	-rm djangohumidity/db.sqlite3
	python manage.py makemigrations djangohumidity
	make migrate
	venv/bin/python manage.py shell < populate.py
	sqlite3 djangohumidity/db.sqlite3 '.tables'
	sqlite3 djangohumidity/db.sqlite3 --header 'SELECT * FROM djangohumidity_sensor'
	sqlite3 djangohumidity/db.sqlite3 --header 'SELECT * FROM djangohumidity_parameter'
	sqlite3 djangohumidity/db.sqlite3 --header 'SELECT * FROM djangohumidity_data'


shell:
	python manage.py shell
