default: gen-init gen-schema lint

build:
    pyproject-build
    check-wheel-contents dist/*.whl
    twine check --strict dist/*

gen-init:
    ./scripts/gen-init.sh

gen-schema:
    python scripts/gen-schema.py
    prettier --write docs/schema/

lint: lint-python lint-toml

lint-python:
    ruff check --fix

lint-toml:
    sort-toml .ruff.toml pyproject.toml
