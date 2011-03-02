pep8:
	find apiclient samples -name "*.py" | xargs pep8 --ignore=E111,E202

test:
	python runtests.py tests

.PHONY: docs
docs:
	cd docs; ./build.sh
	python describe.py

.PHONY: prerelease
prerelease:
	-rm dist/*
	python setup.py clean
	python setup.py sdist

.PHONY: release
release: prerelease
	python setup.py sdist register upload
	wget "http://support.googlecode.com/svn/trunk/scripts/googlecode_upload.py" -O googlecode_upload.py
	python googlecode_upload.py --summary="Version $(shell python setup.py --version)" --project=google-api-python-client dist/*.tar.gz

