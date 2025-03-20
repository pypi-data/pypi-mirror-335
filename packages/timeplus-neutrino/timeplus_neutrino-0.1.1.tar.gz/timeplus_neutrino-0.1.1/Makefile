VERSION := $(shell python -c 'import setuptools_scm; print(setuptools_scm.get_version())')

version:
	echo "Version: $(VERSION)"

build:
	python3 -m pip install --upgrade build
	python3 -m build

install: build
	python3 -m pip install --upgrade dist/timeplus_neutrino-$(VERSION).tar.gz

lint:
	flake8 ./src --count --select=E9,F63,F7,F82 --ignore=E501 --show-source --statistics
	flake8 ./src --count --exit-zero --max-complexity=10 --ignore=E501,W503 --max-line-length=127 --statistics

format:
	black ./src

upload:
	twine upload  --config-file ./.pypirc  dist/*