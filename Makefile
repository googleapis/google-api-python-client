pep8:
	find googleapiclient samples -name "*.py" | xargs pep8 --ignore=E111,E202

APP_ENGINE_PATH=../google_appengine

test:
	tox

.PHONY: coverage
coverage:
	coverage erase
	find tests -name "test_*.py" | xargs --max-args=1 coverage run -a runtests.py
	coverage report
	coverage html

.PHONY: docs
docs:
	cd docs; ./build
	mkdir -p docs/dyn
	python describe.py

.PHONY: wiki
wiki:
	python samples-index.py > ../google-api-python-client.wiki/SampleApps.wiki

.PHONY: prerelease
prerelease:
	-rm -rf dist/
	-sudo rm -rf dist/
	-rm -rf snapshot/
	-sudo rm -rf snapshot/
	python expandsymlinks.py
	cd snapshot; python setup.py clean
	cd snapshot; python setup.py sdist --formats=gztar,zip bdist_wheel --universal
	cd snapshot; tar czf google-api-python-client-samples-$(shell python setup.py --version).tar.gz samples
	cd snapshot; zip -r google-api-python-client-samples-$(shell python setup.py --version).zip samples


.PHONY: release
release: prerelease
	@echo "This target will upload a new release to PyPi and code.google.com hosting."
	@echo "Are you sure you want to proceed? (yes/no)"
	@read yn; if [ yes -ne $(yn) ]; then exit 1; fi
	@echo "Here we go..."
	cd snapshot; python setup.py sdist --formats=gztar,zip bdist_wheel --universal
	cd snapshot; twine upload dist/*
