publish:
	python setup.py sdist bdist_wheel upload

clean:
	rm -rf build dist *.egg-info

test:
	python setup.py test

.PHONY: publish clean test
