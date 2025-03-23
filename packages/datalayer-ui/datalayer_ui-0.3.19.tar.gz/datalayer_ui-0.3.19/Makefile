# Copyright (c) 2021-2024 Datalayer, Inc.
#
# Datalayer License

.PHONY: clean build dist

default: all ## Default target is all.

help: ## display this help.
	@awk 'BEGIN {FS = ":.*##"; printf "\nUsage:\n  make \033[36m<target>\033[0m\n"} /^[a-zA-Z_-]+:.*?##/ { printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2 } /^##@/ { printf "\n\033[1m%s\033[0m\n", substr($$0, 5) } ' $(MAKEFILE_LIST)

all: clean install build dist ## Clean Install and Build

clean:
	yarn clean

build:
	yarn build

build-tsc:
	yarn build:tsc

deploy-io: ## deploy-io
	export S3_BUCKET_NAME=datalayer-io && \
		export CLOUDFRONT_DISTRIBUTION_ID=E37RU7E3SQ7LVT && \
		export DATALAYER_RUN_URL=https://prod1.datalayer.run && \
		export DATALAYER_CDN_URL=https://datalayer.io && \
		${DATALAYER_HOME}/src/landings/datalayer/ui/dev/deploy.sh

deploy-run: ## deploy-run
	export S3_BUCKET_NAME=datalayer-run && \
		export CLOUDFRONT_DISTRIBUTION_ID=E16AM7OFL9HYZI && \
		export DATALAYER_RUN_URL=https://prod1.datalayer.run && \
		export DATALAYER_CDN_URL=https://datalayer.run && \
		${DATALAYER_HOME}/src/landings/datalayer/ui/dev/deploy.sh

deploy-dev: ## deploy-dev
	export S3_BUCKET_NAME=datalayer-io-dev1 && \
		export CLOUDFRONT_DISTRIBUTION_ID=EB47GYKBX4PSR && \
		export DATALAYER_RUN_URL=https://dev2.datalayer.run && \
		export DATALAYER_CDN_URL=https://dev1.datalayer.io && \
		${DATALAYER_HOME}/src/landings/datalayer/ui/dev/deploy.sh

build-storybook: ## build-storybook
	yarn build:storybook

start-storybook: ## start-storybook
	yarn storybook

deploy-storybook: build-storybook ## publish-storybook to s3
	aws s3 rm \
		s3://datalayer-tech-storybook/ \
		--recursive \
		--profile datalayer && \
	aws s3 cp \
		./storybook-static \
		s3://datalayer-tech-storybook/ \
		--recursive \
		--profile datalayer && \
	 aws cloudfront create-invalidation \
		--distribution-id E3CYF4GDN3UVT \
		--paths "/*" \
		--profile datalayer && \
	echo open ✨ https://storybook.datalayer.tech

publish-npm: clean build-tsc ## publish
	npm publish --access public
	echo open https://www.npmjs.com/package/@datalayer/ui

publish-pypi: # publish the pypi package
	git clean -fdx && \
		python -m build
	@exec echo
	@exec echo twine upload ./dist/*-py3-none-any.whl
	@exec echo
	@exec echo https://pypi.org/project/datalayer-ui/#history

publish-conda: # publish the conda package
	@exec echo
	cd ./conda-recipe; ./publish-conda.sh
	@exec echo
	@exec echo https://anaconda.org/datalayer/datalayer-core
	@exec echo conda install datalayer::datalayer-ui
