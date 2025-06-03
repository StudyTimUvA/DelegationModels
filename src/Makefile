.ONESHELL:
.PHONY: black

black:
	black --line-length 100 --target-version py310 ./

remove_pycache:
	find . -type d -name "__pycache__" -exec rm -rf {} \+