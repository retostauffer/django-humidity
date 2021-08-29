


exe="venv/bin/python3"

run:
	${exe} manage.py runserver

migrate:
	${exe} manage.py migrate

npm:
	(cd djangohumidity/static && npm install)

venv:
	virtualenv -p python3 venv
	#source venv/bin/activate
	venv/bin/pip3 install -r requirements.txt:


.PHONY: populate
populate:
	-rm -r djangohumidity/migrations
	-rm djangohumidity/db.sqlite3
	${exe} manage.py makemigrations djangohumidity
	make migrate
	${exe} manage.py shell < populate.py
	sqlite3 djangohumidity/db.sqlite3 '.tables'
	sqlite3 djangohumidity/db.sqlite3 --header 'SELECT * FROM djangohumidity_sensor'
	sqlite3 djangohumidity/db.sqlite3 --header 'SELECT * FROM djangohumidity_parameter'
	sqlite3 djangohumidity/db.sqlite3 --header 'SELECT * FROM djangohumidity_data limit 10'


shell:
	python manage.py shell
