# EXTERNAL_VENV_PATH := /home/thib/testouille/.venv
EXTERNAL_VENV_PATH := /goinfre/tvivier/.venv
export UV_PROJECT_ENVIRONMENT = $(EXTERNAL_VENV_PATH)
NAME = call_me_maybe
ENTRYPOINT = main.py
PROJECT = ./src/call_me_maybe
PYTHON = $(ENV)/bin/python3
PIP = $(ENV)/bin/pip3

.PHONY: all install run sync debug clean lint lint-strict

all: run

sync:
	uv sync

run:	sync
	uv run $(ENTRYPOINT)

debug:
	python3 -m pdb $(ENTRYPOINT)

lint:
	flake8 $(PROJECT)
	mypy $(PROJECT) --warn-return-any --warn-unused-ignores \
		--ignore-missing-imports --disallow-untyped-defs \
		--check-untyped-defs

lint-strict:
	flake8 $(PROJECT)
	mypy $(PROJECT) --strict

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
