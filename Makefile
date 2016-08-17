.PHONY: clean build test

clean:
	rm -rf build dist *.egg-info

build:
	@python setup.py build

test-coverage:
	PYTHONPATH=. nosetests -v --with-coverage --cover-package=params test

test:
	PYTHONPATH=. nosetests -v test

publish:
	python setup.py sdist bdist_wheel upload
