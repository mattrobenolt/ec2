bootstrap:
	pip install -r dev_requirements.txt
	pip install -e .

publish:
	python setup.py sdist bdist_wheel upload

clean:
	rm -rf build dist *.egg-info

test: lint
	py.test

lint:
	flake8 ec2

.PHONY: bootstrap publish clean test lint
