clean:
	@find . -name "*.pyc" -delete

deps:
	@pip install -r requirements.txt

flake8:
	@flake8 . --ignore=E124,E128

test:
	@coverage erase
	@coverage run  --source=easydojo test.py
	@coverage html

help:
	@grep '^[^#[:space:]].*:' Makefile | awk -F ":" '{print $$1}'
