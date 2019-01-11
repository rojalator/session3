RST2HTML := rst2html5.py --initial-header-level=2 --footnote-references=superscript --smart-quotes=yes -g -d -t 
PDOC := pdoc --html --overwrite  --all-submodules --html-dir 
PYCCO := pycco --generate_index --paths -s --directory 


all: setup

setup: build
	python3 setup.py install

build:
	python3 setup.py build

release: documentation distribution

distribution:
	python3 setup.py sdist bdist_wheel

documentation:
	$(RST2HTML) README.rst README.html
	$(RST2HTML) test/README.rst test/README.html
	$(PDOC) docs session3
	$(PYCCO) docs/literate ./**/**/*.py ./session3/*.py ./test/*.py

