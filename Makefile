export DJANGO_SETTINGS_MODULE=tests.settings
export PYTHONPATH=.

.PHONY: test

lint:
	flake8 avatar --ignore=E124,E501,E127,E128,E722
	black --check .

test:
	coverage run --source=avatar `which django-admin` test tests
	coverage report

publish: clean
	python setup.py sdist
	twine upload dist/*

clean:
	rm -vrf ./build ./dist ./*.egg-info
	find . -name '*.pyc' -delete
	find . -name '*.tgz' -delete
