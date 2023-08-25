.DEFAULT_GOAL := all

INSTALL_STAMP := .install.stamp
POETRY := $(shell command -v poetry 2> /dev/null)

.PHONY: all
all: install format lint

.PHONY: help
help:
	@echo "\033[1;34mPlease use 'make <target>', where <target> is one of\033[0m"
	@echo ""
	@echo "  \033[1;32minstall\033[0m     checks if poetry is installed & installs the packages"
	@echo "  \033[1;32mformat\033[0m      run the code formatters - black & isort"
	@echo "  \033[1;32mlint\033[0m        runs linters - mypy & ruff"
	@echo "  \033[1;32mall\033[0m         install, lint, and test the project"
	@echo "  \033[1;32mclean\033[0m       remove all temporary files/folders like __pycache__, etc."
	@echo ""
	@echo "\033[1;34mCheck the Makefile to know exactly what each target is doing.\033[0m"

install: $(INSTALL_STAMP)
$(INSTALL_STAMP): pyproject.toml
	@if [ -z $(POETRY) ]; then echo "\033[1;31mPoetry could not be found. See https://python-poetry.org/docs/\033[0m"; exit 2; fi
	$(POETRY) run pip install --upgrade pip
	$(POETRY) install
	@touch $(INSTALL_STAMP)
	@echo "\033[1;32mInstallation completed successfully.\033[0m"
	@echo ""

.PHONY: format
format: $(INSTALL_STAMP)
	@echo "\033[1;34mRunning isort...\033[0m"; $(POETRY) run isort .
	@echo "\033[1;34mCompleted isort...\033[0m";
	@echo ""
	@echo "\033[1;34mRunning black...\033[0m"; $(POETRY) run black .
	@echo "\033[1;34mCompleted black...\033[0m";
	@echo ""

.PHONY: lint
lint: $(INSTALL_STAMP)
	@echo "\033[1;34mRunning mypy...\033[0m"; $(POETRY) run mypy .
	@echo "\033[1;34mCompleted mypy...\033[0m";
	@echo ""
	@echo "\033[1;34mRunning ruff...\033[0m"; $(POETRY) run ruff .
	@echo "\033[1;34mCompleted ruff...\033[0m";

.PHONY: mypy
mypy:
	@echo "\033[1;34mRunning mypy...\033[0m"; $(POETRY) run mypy .
	@echo "\033[1;34mCompleted mypy...\033[0m";
	@echo ""

.PHONY: clean
clean:
	@echo "\033[1;34mCleaning temporary files...\033[0m"
	@rm -rf `find . -name __pycache__`
	@rm -f `find . -type f -name '*.py[co]' `
	@rm -f `find . -type f -name '*~' `
	@rm -f `find . -type f -name '.*~' `
	@rm -rf .cache
	@rm -rf .pytest_cache
	@rm -rf .mypy_cache
	@rm -rf .ruff_cache
	@rm -rf htmlcov
	@rm -rf *.egg-info
	@rm -f .coverage
	@rm -f .coverage.*
	@rm -rf build
	@rm -rf `find . -name .ipynb_checkpoints`
	@if [ -f $(INSTALL_STAMP) ]; then rm $(INSTALL_STAMP); fi
	@echo "\033[1;32mCleaning completed successfully.\033[0m"
	@if [ "$(filter venv,$(MAKECMDGOALS))" = "venv" ]; then $(MAKE) clean-venv; fi

.PHONY: clean-venv
clean-venv:
	@if [ -d ".venv" ]; then echo "Virtual environment found. Deleting..."; rm -rf .venv; fi
	@echo "\033[1;32mVirtual environment cleaning completed successfully.\033[0m"

.PHONY: venv
venv: ;
