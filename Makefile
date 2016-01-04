test: venv/bin/py.test
	venv/bin/python setup.py develop
	venv/bin/py.test tests

venv/bin/py.test: venv
	venv/bin/pip install pytest

venv:
	virtualenv venv
