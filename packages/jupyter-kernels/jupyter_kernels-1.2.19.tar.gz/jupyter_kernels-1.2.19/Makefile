# Copyright (c) 2023-2024 Datalayer, Inc.
#
# Datalayer License

SHELL=/bin/bash

ENV_NAME=datalayer

VERSION=1.2.1

.DEFAULT_GOAL := default

.SILENT: init

.PHONY: port-forward storybook

help: ## display this help
	@awk 'BEGIN {FS = ":.*##"; printf "\nUsage:\n  make \033[36m<target>\033[0m\n"} /^[a-zA-Z_-]+:.*?##/ { printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2 } /^##@/ { printf "\n\033[1m%s\033[0m\n", substr($$0, 5) } ' $(MAKEFILE_LIST)

default: help ## default target is help

env: warning ## env
	micromamba env create -y -n ${ENV_NAME} -f environment.yml
	@exec echo "-------------------------------------------------------"
	@exec echo "micromamba activate ${ENV_NAME}"
	@exec echo "-------------------------------------------------------"

env-rm: warning ## env-rm
	micromamba deactivate && \
	micromamba remove -y --name ${ENV_NAME} --all || true

kill:
	./dev/utils/kill.sh

warning:
	echo "\x1b[34m\x1b[43mEnsure you have run \x1b[1;37m\x1b[41m conda deactivate \x1b[22m\x1b[34m\x1b[43m before invoking this.\x1b[0m"

server-login:
	python jupyter_kernels/login/__main__.py

server-jupyter:
	python jupyter_kernels/__main__.py

clean: ## clean
	yarn clean

build: ## build
	yarn build

build-prod: ## build-prod
	git clean -fdx
	python -m build

typedoc: ## generate typedoc
	rm -fr typedoc && \
	yarn typedoc --tsconfig ./tsconfig.json && \
	open typedoc/index.html

publish-typedoc: typedoc ## deploy typedoc
	aws s3 rm \
		s3://datalayer-typedoc/datalayer/jupyter-kernels/${VERSION}/ \
		--recursive \
		--profile datalayer
	aws s3 cp \
		typedoc \
		s3://datalayer-typedoc/datalayer/jupyter-kernels/${VERSION}/ \
		--recursive \
		--profile datalayer
	aws cloudfront create-invalidation \
		--distribution-id XXX \
		--paths /datalayer/jupyter-kernels/${VERSION}/ \
		--profile datalayer
	echo open ✨  https://typedoc.datalayer.tech/datalayer/jupyter-kernels/${VERSION}

publish-npm: clean build # publish the npm package
	npm publish --access public
	echo https://www.npmjs.com/package/@datalayer/jupyter-kernels?kernels=versions

publish-pypi: # publish the pypi package
	git clean -fdx && \
		python -m build
	@exec echo
	@exec echo twine upload ./dist/*-py3-none-any.whl
	@exec echo
	@exec echo https://pypi.org/project/jupyter-kernels/#history

publish-conda: # publish the conda package
	@exec echo
	cd conda-recipe; ./publish-conda.sh
	@exec echo
	@exec echo https://anaconda.org/datalayer/jupyter-kernels
	@exec echo conda install datalayer::jupyter-kernels
