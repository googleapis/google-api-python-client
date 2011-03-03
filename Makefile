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
	python runtests.py --exit_on_failure tests
	-rm dist/*
	python setup.py clean
	python setup.py sdist

.PHONY: release
release: prerelease
	@echo "This target will upload a new release to PyPi and code.google.com hosting."
	@echo "Are you sure you want to proceed? (yes/no)"
	@read yn; [ "yes" == $$yn ]
	@echo "Here we go..."
	python setup.py sdist register upload
	wget "http://support.googlecode.com/svn/trunk/scripts/googlecode_upload.py" -O googlecode_upload.py
	python googlecode_upload.py --summary="Version $(shell python setup.py --version)" --project=google-api-python-client dist/*.tar.gz

