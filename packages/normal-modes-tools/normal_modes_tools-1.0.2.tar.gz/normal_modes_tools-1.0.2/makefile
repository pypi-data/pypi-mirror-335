publish:
	# rm dist/*
	python -m build
	python -m pip install --upgrade twine
	python -m twine upload --repository pypi dist/*
