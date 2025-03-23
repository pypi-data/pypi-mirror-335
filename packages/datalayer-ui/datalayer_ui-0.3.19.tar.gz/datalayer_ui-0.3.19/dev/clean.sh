#!/usr/bin/env bash

# Copyright (c) 2021-2024 Datalayer, Inc.
#
# Datalayer License

echo
echo -e "\x1b[34m\x1b[43mCleaning Distribution - Version $DATALAYER_VERSION\x1b[0m"
echo

echo
echo 🟡 Cleaning...
echo

# cd $DATALAYER_HOME/src && \
#	find . -name lib | xargs rm -fr {} || true && \
#	find . -name build | xargs rm -fr {} || true && \
#	find . -name dist | xargs rm -fr {} || true && \
rm -fr $DATALAYER_HOME/src/landings/datalayer/ui/dist
mkdir $DATALAYER_HOME/src/landings/datalayer/ui/dist
