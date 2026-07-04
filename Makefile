# EXTERNAL_VENV_PATH := /home/thib/testouille/.venv
EXTERNAL_VENV_PATH := /goinfre/tvivier/.venv
export UV_PROJECT_ENVIRONMENT = $(EXTERNAL_VENV_PATH)
NAME = call_me_maybe
ENTRYPOINT = main.py
PYTHON = $(ENV)/bin/python3
PIP = $(ENV)/bin/pip3

.PHONY: all install run sync debug clean lint lint-strict

all: run_home

custom_env:
	python3 -m venv cmm_env

$(ENV):
	python3 -m venv $(ENV)

install: $(ENV)
	$(PIP) install -r requirements.txt

sync:
	uv sync

install_pc: custom_env
	cmm_env/bin/pip3 install -r requirements.txt

run:	install
	$(PYTHON) src/main.py

run_home:	sync
	uv run $(ENTRYPOINT)

debug:
	$(PYTHON) -m pdb $(PACMAN_MAIN) $(CONFIG)

lint:
	flake8 .
	mypy . --warn-return-any --warn-unused-ignores \
		--ignore-missing-imports --disallow-untyped-defs \
		--check-untyped-defs

lint-strict:
	flake8 .
	mypy . --strict

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
