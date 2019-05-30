.PHONY: clean build test

all: build

clean:
	rm -rf build dist *.egg-info

build:
	@python setup.py build

test:
	PYTHONPATH=. pytest -v test

test-coverage:
	PYTHONPATH=. pytest -v \
		--cov=params --cov-config=tox.ini --cov-report=html \
		test

publish:
	python setup.py sdist bdist_wheel upload
