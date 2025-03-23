#!/usr/bin/env bash

# Copyright (c) 2021-2024 Datalayer, Inc.
#
# Datalayer License

export CUR_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Deploy the static assets (JavaScript, CSS, Images...).

${CUR_DIR}/clean.sh
${CUR_DIR}/build.sh
${CUR_DIR}/copy.sh
${CUR_DIR}/echo.sh
