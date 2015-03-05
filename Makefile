MAKE   = make
PYTHON = python
SETUP  = $(PYTHON) ./setup.py

.PHONY: clean distclean test sdist upload readme

clean:
	find . -type f -name \*.pyc -exec rm {} \;
	rm -rf *.egg-info .coverage

distclean: clean
	rm -rf dist docx-xslt-*

readme: README.md
	pandoc --from=markdown --to=plain README.md >README.txt

test:
	$(SETUP) test

sdist: readme
	$(SETUP) sdist

upload:
	$(SETUP) sdist upload
