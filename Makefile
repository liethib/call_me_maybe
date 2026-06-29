NAME = call_me_maybe
ENV = /goinfre/tvivier/.venv
PYTHON = $(ENV)/bin/python3
PIP = $(ENV)/bin/pip3

.PHONY: all install run debug clean lint lint-strict

all: run

$(ENV):
	python3 -m venv $(ENV)

install: 
	$(PIP) install -r requirements.txt

run:	install
	$(PYTHON) main.py

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
