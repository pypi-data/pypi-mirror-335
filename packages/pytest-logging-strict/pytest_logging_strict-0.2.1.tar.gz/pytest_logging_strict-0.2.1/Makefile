.ONESHELL:
.DEFAULT_GOAL := help
SHELL := /bin/bash

# underscore separated; aka sdist and whl names
# https://blogs.gentoo.org/mgorny/2023/02/09/the-inconsistencies-around-python-package-naming-and-the-new-policy/
APP_NAME := pytest_logging_strict

define NORMALIZE_APP_NAME
try:
    from importlib import metadata
except ImportError:
    v = '$(APP_NAME)'.replace('_', "-").replace('.', "-")
    print(v)
else:
    print(metadata.metadata('$(APP_NAME)')['Name']))
endef

#virtual environment. If 0 issue warning
#Not activated:0
#activated: 1
ifeq ($(VIRTUAL_ENV),)
$(warning virtualenv not activated)
is_venv =
else
is_venv = 1
VENV_BIN := $(VIRTUAL_ENV)/bin
VENV_BIN_PYTHON := python3
PY_X_Y := $(shell $(VENV_BIN_PYTHON) -c 'import platform; t_ver = platform.python_version_tuple(); print(".".join(t_ver[:2]));')
endif

ifeq ($(is_venv),1)
  # Package name is hyphen delimited
  PACKAGE_NAME ?= $(shell $(VENV_BIN_PYTHON) -c "$(NORMALIZE_APP_NAME)")
  VENV_PACKAGES ?= $(shell $(VENV_BIN_PYTHON) -m pip list --disable-pip-version-check --no-python-version-warning --no-input | /bin/awk '{print $$1}')
  IS_PACKAGE ?= $(findstring $(1),$(VENV_PACKAGES))

  is_wheel ?= $(call IS_PACKAGE,wheel)
  is_piptools ?= $(call IS_PACKAGE,pip-tools)

  find_whl = $(shell [[ -z "$(3)" ]] && extension=".whl" || extension="$(3)"; [[ -z "$(2)" ]] && srcdir="dist" || srcdir="$(2)/dist"; [[ -z "$(1)" ]] && whl=$$(ls $$srcdir/$(APP_NAME)*.whl  --format="single-column") || whl=$$(ls $$srcdir/$(1)*.whl --format="single-column"); echo $${whl##*/})
endif

##@ Helpers

# Original
# https://www.thapaliya.com/en/writings/well-documented-makefiles/
# coverage adaptation (https://github.com/nedbat/coveragepy/commits?author=nedbat)
# https://github.com/nedbat/coveragepy/blob/5124586e92da3e69429002b2266ce41898b953a1/Makefile
#@awk 'BEGIN {FS = ":.*##"; printf "\nUsage:\n  make \033[36m<target>\033[0m\n"} /^[a-zA-Z_-]+:.*?##/ { printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2 } /^##@/ { printf "\n\033[1m%s\033[0m\n", substr($$0, 5) } ' $(MAKEFILE_LIST)
.PHONY: help
help:					## (Default) Display this help -- Always up to date
	@awk -F ':.*##' '/^[^: ]+:.*##/{printf "  \033[1m%-20s\033[m %s\n",$$1,$$2} /^##@/{printf "\n%s\n",substr($$0,5)}' $(MAKEFILE_LIST)


##@ Testing

#run all pre-commit checks
.PHONY: pre-commit
pre-commit:				## Run checks found in .pre-commit-config.yaml
ifeq ($(is_venv),1)
	@pre-commit run --all-files
endif


##@ GNU Make standard targets

# --cov-report=xml
# Dependencies: pytest, pytest-cov, pytest-regressions
# make [v=1] check
# $(VENV_BIN)/pytest --showlocals --cov=pytest_logging_strict --cov-report=term-missing --cov-config=pyproject.toml $(verbose_text) tests
.PHONY: check
check: private verbose_text = $(if $(v),"--verbose")
check:					## Run tests, generate coverage reports -- make [v=1] check
ifeq ($(is_venv),1)
	-@$(VENV_BIN_PYTHON) -m coverage erase
	$(VENV_BIN_PYTHON) -m coverage run --parallel -m pytest --showlocals $(verbose_text) tests
	$(VENV_BIN_PYTHON) -m coverage combine
	$(VENV_BIN_PYTHON) -m coverage report --fail-under=68
endif
