#!/usr/bin/env bash

# Copyright (c) 2021-2024 Datalayer, Inc.
#
# Datalayer License

echo
echo -e "\x1b[34m\x1b[43mStripping source for $1\x1b[0m"
echo

TAR_GZ=$1
TMP_TAR_GZ="/tmp/tmp.tar.gz"
TMP_TAR="/tmp/tmp.tar"

cd /tmp
cp $TAR_GZ $TMP_TAR_GZ
gzip -d $TMP_TAR_GZ
tar -f $TMP_TAR --wildcards \
  --delete datalayer*/src \
  --delete datalayer*/style
#  --delete datalayer*/package.json \
#  --delete datalayer*/tsconfig.json \
#  --delete datalayer*/webpack*
gzip -9 $TMP_TAR
cp $TMP_TAR_GZ $TAR_GZ
