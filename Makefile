pep8:
	find apiclient samples -name "*.py" | xargs pep8 --ignore=E111,E202

test:
	python runtests.py

skeletons:
	python discovery_extras.py tests/data/buzz.json tests/data/latitude.json tests/data/moderator.json
