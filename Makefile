pep8:
				find apiclient samples -name "*.py" | xargs pep8 --ignore=E111,E202

test:
				python runtests.py
