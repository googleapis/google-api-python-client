pep8:
	find apiclient samples -name "*.py" | xargs pep8 --ignore=E111,E202

APP_ENGINE_PATH=../google_appengine

test:
	./runtests.sh python2.6
	./runtests.sh python2.7


.PHONY: coverage
coverage:
	coverage erase
	find tests -name "test_*.py" | xargs --max-args=1 coverage run -a runtests.py
	coverage report
	coverage html

.PHONY: docs
docs:
	cd docs; ./build.sh
	python describe.py
	python samples-index.py ../google-api-python-client.wiki/SampleApps.wiki

.PHONY: wiki
wiki:
	python samples-index.py > ../google-api-python-client.wiki/SampleApps.wiki

.PHONY: prerelease
prerelease:
	./runtests.sh python2.6
	./runtests.sh python2.7
	-sudo rm -rf dist/
	-sudo rm -rf snapshot/
	python expand-symlinks.py
	cd snapshot; python setup.py clean
	cd snapshot; python setup.py sdist --formats=gztar,zip

.PHONY: release
release: prerelease
	@echo "This target will upload a new release to PyPi and code.google.com hosting."
	@echo "Are you sure you want to proceed? (yes/no)"
	@read yn; if [ yes -ne $(yn) ]; then exit 1; fi
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
	@read yn; if [ yes -ne $(yn) ]; then exit 1; fi
	@echo "Here we go..."
	cd snapshot; python setup.py sdist --formats=gztar,zip register upload
	wget "http://support.googlecode.com/svn/trunk/scripts/googlecode_upload.py" -O googlecode_upload.py
	python googlecode_upload.py --summary="oauth2client Version $(shell python setup.py --version)" --project=google-api-python-client snapshot/dist/*.tar.gz
	python googlecode_upload.py --summary="oauth2client Version $(shell python setup.py --version)" --project=google-api-python-client snapshot/dist/*.zip
