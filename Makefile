pep8:
				find apiclient samples -name "*.py" | xargs pep8 --ignore=E111,E202

test:
				python runtests.py tests

.PHONY: docs
docs:
	cd docs; ./build.sh
	python describe.py
