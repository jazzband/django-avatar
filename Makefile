export DJANGO_SETTINGS_MODULE=tests.settings
export PYTHONPATH=.

.PHONY: test

test:
	flake8 avatar --ignore=E124,E501,E127,E128
	coverage run --branch --source=avatar `which django-admin.py` test tests
	coverage report
