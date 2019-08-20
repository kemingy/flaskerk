install:
	pip3 install -e .

test:
	py.test test -vv

doc:
	cd docs && make html

clean:
	rm -rf build/ dist/ *.egg-info .pytest_cache
	find . -name '*.pyc' -type f -exec rm -rf {} +
	find . -name '__pycache__' -exec rm -rf {} +

package: clean
	python3 setup.py sdist bdist_wheel

publish: package
	twine upload dist/*

.PHONY: test doc