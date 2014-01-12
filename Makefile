publish:
	python setup.py sdist upload

clean:
	rm -rf build dist *.egg-info

test:
	python setup.py test

.PHONY: publish clean test
