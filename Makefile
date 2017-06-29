ci: test pylint

pylint:
	pylint3 woods lib test

.PHONY: test
test:
	python3 -m unittest discover -vp "*_test.py" test

clean:
	find -name __pycache__ -or -name '*.pyo' -or -name '*.pyc' -delete

example:
	echo todo
