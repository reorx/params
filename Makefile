.PHONY: build test

all: build

clean:
	rm -rf build dist *.egg-info

build:
	python setup.py build

build-dist:
	python setup.py sdist bdist_wheel

publish: build-dist
	python -m twine upload --skip-existing $(shell ls -t dist/*.whl | head -1)

test:
	PYTHONPATH=. pytest -v test

test-coverage:
	PYTHONPATH=. pytest -v \
		--cov=params --cov-config=tox.ini --cov-report=html \
		test
