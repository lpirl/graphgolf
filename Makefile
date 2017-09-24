PYPY3?=pypy/bin/pypy3

ci: test pylint

pylint:
	pylint3 graphgolf lib test

.PHONY: test
test:
	# no -O here!
	$(PYPY3) -m unittest discover -vp "*_test.py" test

clean:
	find -name __pycache__ -or -name '*.pyo' -or -name '*.pyc' -delete

example:
	$(PYPY3) graphgolf 32 5

profile:
	$(PYPY3) -OO -m cProfile  -s calls graphgolf 256 18

pylint:
	pylint3 graphgolf lib
