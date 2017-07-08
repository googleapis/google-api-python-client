pip: 
	@pip install -r requirements.txt


syncdb:
	@python manage.py syncdb


run: 
	@python manage.py runserver 0.0.0.0:8000


setup: pip syncdb run


shell: 
	@python manage.py shell


test:
	@python manage.py test
