.PHONY: clean clean-test clean-pyc clean-build docs help pytest
.DEFAULT_GOAL := help
define BROWSER_PYSCRIPT
import os, webbrowser, sys
try:
	from urllib import pathname2url
except:
	from urllib.request import pathname2url

webbrowser.open("file://" + pathname2url(os.path.abspath(sys.argv[1])))
endef
export BROWSER_PYSCRIPT


# this is a helper python script which prints useful help
# messages when 'make help' or 'make' is called
define PRINT_HELP_PYSCRIPT
import re, sys
print("")
print("make options: (run make [option] to perform action):")

targets = sorted(
	[match.groups() for match in
		[re.match(r'^([a-zA-Z0-9_-]+):.*?## (.*)$$', line) for line in sys.stdin]
	if match], key=lambda x:x[0])

for target, help in targets:
	if len(help) > 0:
		print("")
		print("%s:" % target)

		ln = ""
		for word in help.split(" "):
			ln += word + " "
			if len(ln) > 60:
				print("    %s" % ln)
				ln = ""
		if len(ln) > 0:
			print("    %s" % ln)
print("")



for line in sys.stdin:
	match = re.match(r'^([a-zA-Z0-9_-]+):.*?## (.*)$$', line)
	if match:
		target, help = match.groups()

		if len(help) > 0:
			print("")
			print("%s:" % target)

			ln = ""
			for word in help.split(" "):
				ln += word + " "
				if len(ln) > 40:
					print("    %s" % ln)
					ln = ""
			if len(ln) > 0:
				print("    %s" % ln)
print("")

endef
export PRINT_HELP_PYSCRIPT
BROWSER := python -c "$$BROWSER_PYSCRIPT"

export PYTHONPATH:=$(shell pwd):$(PYTHONPATH)

help:
	@python -c "$$PRINT_HELP_PYSCRIPT" < $(MAKEFILE_LIST)

clean: clean-build clean-pyc clean-test ## Remove all build, test, coverage and Python artifacts.

clean-build: ## Remove build artifacts including build/ dist/ and .eggs/ folders.
	rm -fr build/
	rm -fr dist/
	rm -fr .eggs/
	find . -name '*.egg-info' -exec rm -fr {} +
	find . -name '*.egg' -exec rm -f {} +

clean-pyc: ## Remove Python file artifacts, e.g. pyc files.
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +

clean-test: ## Remove test and coverage artifacts.
	rm -rf .tox/
	rm -rf .coverage.*
	rm -rf .coverage
	rm -rf htmlcov/
	rm -fr report.html
	rm -fr report.xml
	rm -fr coverage.xml
	rm -fr .pytest_cache

lint: ## Check style and pep8 conformity using multiple pep8 and style checkers. For now, flake8, pycodestyle, pylint and pydocstyle are included, but their results ignored.
	-flake8 --exclude="*.ipynb,*.ipynb*" --max-line-length=120 sicor tests > ./tests/linting/flake8.log || \
		(cat ./tests/linting/flake8.log && exit 1)
	-pycodestyle sicor --exclude="*.ipynb,*.ipynb*" --max-line-length=120 > ./tests/linting/pycodestyle.log || \
		(cat ./tests/linting/pycodestyle.log && exit 1)
	-pylint --rcfile=tests/linting/pylint.rc sicor > tests/linting/pylint.log || \
		(cat ./tests/linting/pylint.log && exit 1)
	-pydocstyle sicor > ./tests/linting/pydocstyle.log || \
		(cat ./tests/linting/pydocstyle.log && exit 1)

urlcheck: ## check for dead URLs
	urlchecker check . \
		--file-types .py,.rst,.md,.json \
		--exclude-patterns www.enmap.org,S2_PDI_Level-1C_Tile_Metadata.xsd,S2_PDI_Level-2A_Tile_Metadata.xsd,https://git.gfz-potsdam.de/EnMAP/sicor/badges/main/coverage.svg,https://git.gfz-potsdam.de/EnMAP/sicor/pipelines,https://git.gfz-potsdam.de/EnMAP/sicor/badges/main/pipeline.svg

test_enmap: ## Run a single test quickly with the default Python and without coverage. This is useful for debugging errors and feel free to change the considered test case to your liking.
	echo  ########### ####### ${PYTHONPATH}
	python tests/test_sicor_enmap.py

test: lint download-tables ## Run tests quickly with the default Python interpreter and without coverage.
	python setup.py test

pytest_enmap: clean-test ## Runs pytest with coverage and creates coverage and test report
	## - generates cobertura 'coverage.xml' (needed to show coverage in GitLab MR changes)
	## - generates 'report.html' based on pytest-reporter-html1
	## - generates JUnit 'report.xml' to show the test report as a new tab in a GitLab MR
	## NOTE: additional options pytest and coverage (plugin pytest-cov) are defined in .pytest.ini and .coveragerc
	pytest tests \
		--verbosity=3 \
		--color=yes \
		--tb=short \
		--cov=sicor \
		--cov-report html:htmlcov \
    	--cov-report term-missing \
    	--cov-report xml:coverage.xml \
    	--ignore=tests/test_sicor_enmap_add.py \
    	--ignore=tests/test_sicor_s2.py \
    	--ignore=tests/test_sicor_s2l8.py \
    	--template=html1/index.html --report=report.html \
    	--junitxml report.xml

pytest_s2: clean-test ## Runs pytest with coverage and creates coverage and test report
	## - generates cobertura 'coverage.xml' (needed to show coverage in GitLab MR changes)
	## - generates 'report.html' based on pytest-reporter-html1
	## - generates JUnit 'report.xml' to show the test report as a new tab in a GitLab MR
	## NOTE: additional options pytest and coverage (plugin pytest-cov) are defined in .pytest.ini and .coveragerc
	pytest tests \
		--verbosity=3 \
		--color=yes \
		--tb=short \
		--cov=sicor \
		--cov-report html:htmlcov \
    	--cov-report term-missing \
    	--cov-report xml:coverage.xml \
    	--ignore=tests/test_sicor_enmap.py \
    	--ignore=tests/test_sicor_enmap_add.py \
    	--ignore=tests/test_sicor_s2l8.py \
    	--template=html1/index.html --report=report.html \
    	--junitxml report.xml

download-tables: ## Download tables for atmospheric correction and scene classification from google drive if not found locally (anywhere in $PATH). Gdrive might be unreliable and fail. Just try aggain later. Files are checked for their hash before continuing here.
	python -c 'from sicor.tables import get_tables; get_tables(sensor="s2"); get_tables(sensor="l8"); get_tables(sensor="enmap", optional_downloads=("ch4",))'

download-tables-all: ## Download ALL tables for atmospheric correction and scene classification. This includes additional data, e.g. for methane retrievals or further development.
	python -c 'from sicor.tables import get_tables; get_tables(\
optional_downloads=("ch4","hyperspectral_sample","s2_manual_classification"))'

coverage: download-tables ## Use coverage to run tests and to produce a coverage report.
		coverage run --source="sicor,bin" --rcfile="tests/env/coveragerc" --parallel setup.py test
		coverage combine .coverage*
		coverage report -m --rcfile=tests/env/coveragerc
		coverage html --rcfile=tests/env/coveragerc

coverage_view: coverage ## Open default browser to check coverage report.
		$(BROWSER) htmlcov/index.html

docs: ## Generate HTML documentation using SPHINX. If example jupyer notebooks in should be updated, run the target 'convert_examples_to_doc' first.
	rm -f docs/sicor.rst
	rm -f docs/modules.rst
	sphinx-apidoc sicor -o docs/ --private --doc-project 'API Reference'
	$(MAKE) -C docs clean
	$(MAKE) -C docs html
	#$(MAKE) -C docs latex
	#$(MAKE) -C docs latexpdf
	$(BROWSER) docs/_build/html/index.html

requirements: #### Install requirements as defined in requirements.txt using pip.
	pip install -r requirements.txt

install: clean requirements download-tables ## Install the package to the active Python's site-packages.
	pip install . --no-cache-dir

gitlab_CI_docker: install ## Build a docker image for CI use within gitlab. This is based on docker an required sudo access to docker. Multiple images are build, the 'sicor:latest' includes a working environment for sicor and is used to run the tests. Sicor is not included in this image and is clones and installed for each test run.
	cd ./tests/CI_docker/; bash ./build_sicor_testsuite_image.sh

examples_notebooks:  ## Start a jupyter notebook server in the examples directory and open browser.
	cd examples; jupyter notebook

convert_examples_to_doc:  ## Use nbconvert to convert jupyter notebooks in examples to doc/examples. Links to internal images are adjusted such that SPINX documentation can be build.
	python examples/convert_examples_to_doc.py
