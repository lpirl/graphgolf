PY3_INTERPRETER?=pypy/bin/pypy3

ci: test pylint

pylint:
	pylint3 woods lib test

.PHONY: test
test:
	$(PY3_INTERPRETER) -m unittest discover -vp "*_test.py" test

clean:
	find -name __pycache__ -or -name '*.pyo' -or -name '*.pyc' -delete

example:
	$(PY3_INTERPRETER) woods 32 5

profile:
	$(PY3_INTERPRETER) -OO -m cProfile  -s calls woods 100 10
