publish:
	python setup.py sdist upload

clean:
	rm -rf build dist *.egg-info

test:
	nosetests

.PHONY: publish clean test
