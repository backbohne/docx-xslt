MAKE   = make
PYTHON = python
SETUP  = $(PYTHON) ./setup.py

.PHONY: clean distclean test sdist upload

clean:
	find . -type f -name \*.pyc -exec rm {} \;
	rm -rf *.egg-info .coverage

distclean: clean
	rm -rf dist docx-xslt-*

test:
	$(SETUP) test

sdist:
	$(SETUP) sdist

upload:
	$(SETUP) sdist upload
