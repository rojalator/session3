RST2HTML := rst2html5 --smart-quotes=yes -g -d -t
PDOC = pydoctor --make-html --docformat="restructuredtext" --disable-intersphinx-cache --html-output
PYCCO := pycco --generate_index --paths --skip-bad-files  --directory



all: setup

setup: build
	python3 setup.py install

build:
	python3 setup.py build

release: documentation distribution

distribution:
	python -m build
	rstcheck README.rst
	twine check dist/*
	# python3 setup.py sdist bdist_wheel

documentation:
	$(RST2HTML) README.rst README.html
	$(RST2HTML) test/README.rst test/README.html
	$(PDOC) docs session3
	$(PYCCO) docs/literate ./session3/*.py ./session3/store/*.py ./test/*.py

# Call 'make clean' to get rid of the documentation directory
# No directory or file will be called 'clean' so mark it as a phony
.PHONY: clean
clean:
	rm -rf docs/
