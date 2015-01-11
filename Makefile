RST2HTML := rst2html.py --initial-header-level=2

all: setup docs

setup: build
	python setup.py install

build:
	python setup.py build

docs:
	$(RST2HTML) README.txt README.html
	$(RST2HTML) test/README.txt test/README.html
