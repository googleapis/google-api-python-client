pep8:
	find apiclient samples -name "*.py" | xargs pep8 --ignore=E111,E202

APP_ENGINE_PATH=../google_appengine

test:
	python runtests.py tests/test_discovery.py
	python runtests.py tests/test_errors.py
	python runtests.py tests/test_http.py
	python runtests.py tests/test_json_model.py
	python runtests.py tests/test_mocks.py
	python runtests.py tests/test_model.py
	python runtests.py tests/test_oauth2client_clientsecrets.py
	python runtests.py tests/test_oauth2client_django_orm.py
	python runtests.py tests/test_oauth2client_file.py
	python runtests.py tests/test_oauth2client_jwt.py
	python runtests.py tests/test_oauth2client.py
	python runtests.py tests/test_oauth.py
	python runtests.py tests/test_protobuf_model.py
	python runtests.py tests/test_oauth2client_appengine.py

.PHONY: docs
docs:
	cd docs; ./build.sh
	python describe.py

.PHONY: prerelease
prerelease:
	python2.6 runtests.py tests --exit_on_failure
	python2.7 runtests.py tests --exit_on_failure
	-sudo rm -rf dist/
	-sudo rm -rf snapshot/
	python expand-symlinks.py
	cd snapshot; python setup.py clean
	cd snapshot; python setup.py sdist --formats=gztar,zip

.PHONY: release
release: prerelease
	@echo "This target will upload a new release to PyPi and code.google.com hosting."
	@echo "Are you sure you want to proceed? (yes/no)"
	@read yn; [ "yes" == $$yn ]
	@echo "Here we go..."
	cd snapshot; python setup.py sdist --formats=gztar,zip register upload
	wget "http://support.googlecode.com/svn/trunk/scripts/googlecode_upload.py" -O googlecode_upload.py
	python googlecode_upload.py --summary="google-api-python-client Version $(shell python setup.py --version)" --project=google-api-python-client snapshot/dist/*.tar.gz
	python googlecode_upload.py --summary="google-api-python-client Version $(shell python setup.py --version)" --project=google-api-python-client snapshot/dist/*.zip


.PHONY: oauth2_prerelease
oauth2_prerelease:
	-sudo rm -rf dist/
	-sudo rm -rf snapshot/
	mkdir snapshot
	python expand-symlinks.py --source=oauth2client --dest=snapshot/oauth2client
	python expand-symlinks.py --source=samples/dailymotion --dest=snapshot/samples/dailymotion
	python expand-symlinks.py --source=samples/appengine --dest=snapshot/samples/appengine
	python expand-symlinks.py --source=samples/django_sample --dest=snapshot/django_sample
	cp setup_oauth2client.py snapshot/setup.py
	cp MANIFEST_oauth2client.in snapshot/MANIFEST.in
	cp README_oauth2client snapshot/README
	cd snapshot; python setup.py clean
	cd snapshot; python setup.py sdist --formats=gztar,zip

.PHONY: oauth2_release
oauth2_release: oauth2_prerelease
	@echo "This target will upload a new release to PyPi and code.google.com hosting."
	@echo "Are you sure you want to proceed? (yes/no)"
	@read yn; [ "yes" == $$yn ]
	@echo "Here we go..."
	cd snapshot; python setup.py sdist --formats=gztar,zip register upload
	wget "http://support.googlecode.com/svn/trunk/scripts/googlecode_upload.py" -O googlecode_upload.py
	python googlecode_upload.py --summary="oauth2client Version $(shell python setup.py --version)" --project=google-api-python-client snapshot/dist/*.tar.gz
	python googlecode_upload.py --summary="oauth2client Version $(shell python setup.py --version)" --project=google-api-python-client snapshot/dist/*.zip
