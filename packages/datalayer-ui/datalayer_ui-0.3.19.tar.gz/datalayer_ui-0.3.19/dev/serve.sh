#!/usr/bin/env bash

# Copyright (c) 2021-2024 Datalayer, Inc.
#
# Datalayer License

echo
echo -e "\x1b[34m\x1b[43mServing dist - Version $DATALAYER_VERSION\x1b[0m"
echo
echo ✨ open http://localhost:3063
echo

# cd $DATALAYER_HOME/src/landings/datalayer/ui/dist && \
#   jupyterpool --port=3063 --base_url=/api/kernel

cd $DATALAYER_HOME/src/landings/datalayer/ui/dist && \
  python -m http.server 3063
