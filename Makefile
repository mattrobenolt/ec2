publish:
	python setup.py sdist upload

test:
	nosetests

.PHONY: publish test
