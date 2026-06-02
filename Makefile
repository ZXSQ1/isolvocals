

build:
	uv build .

install-dev:
	uv tool install . --editable

install:
	uv tool install .
