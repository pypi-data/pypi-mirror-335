#!/usr/bin/env bash

# Copyright (c) 2021-2024 Datalayer, Inc.
#
# Datalayer License

echo
echo -e "\x1b[34m\x1b[43mDeploying Distribution to AWS S3 - Version $DATALAYER_VERSION\x1b[0m"
echo

aws s3 rm \
  s3://${S3_BUCKET_NAME} \
  --recursive \
  --profile datalayer

aws s3 cp \
  $DATALAYER_HOME/src/landings/datalayer/ui/dist \
  s3://${S3_BUCKET_NAME} \
  --recursive \
  --profile datalayer
: '
aws s3 cp \
  $DATALAYER_HOME/src/landings/datalayer/ui/dist/index.html \
  s3://${S3_BUCKET_NAME}/index.html \
  --profile datalayer
'
aws cloudfront create-invalidation \
  --distribution-id ${CLOUDFRONT_DISTRIBUTION_ID} \
  --paths "/*" \
  --profile datalayer

aws s3 ls \
  s3://${S3_BUCKET_NAME} \
  --profile datalayer
