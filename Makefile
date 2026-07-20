EXTERNAL_VENV_PATH := /home/thib/testouille/.venv
# EXTERNAL_VENV_PATH := /goinfre/$(USER)/.venv
export UV_PROJECT_ENVIRONMENT = $(EXTERNAL_VENV_PATH)
NAME = call_me_maybe
ENTRYPOINT = src
PROJECT = ./src
DATA_OUTPUT_DIR = ./data/output

.PHONY: all install sync debug clean lint lint-strict

$(NAME): all

all: run

install:
	uv sync
	cp ./llm_sdk/__init__.py  $(PROJECT)/wrapper.py 
	if ! [ -d $(DATA_OUTPUT_DIR) ]; then mkdir $(DATA_OUTPUT_DIR); fi
	# mkdir $(DATA_OUTPUT_DIR)

run:	install
	uv run python -m $(ENTRYPOINT)

debug:
	python3 -m pdb $(PROJECT)/__main__.py

lint:	clean
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

moulinette: install
	uv run python -m moulinette/moulinette prepare_exercises --set private
	uv run python -m moulinette/moulinette grade_student_answers --set private --student_answer_path $(DATA_OUTPUT_DIR)/function_calling_results.json
