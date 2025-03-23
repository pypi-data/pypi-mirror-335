#!/usr/bin/env bash

# Copyright (c) 2021-2024 Datalayer, Inc.
#
# Datalayer License

echo
echo -e "\x1b[34m\x1b[43mBuilding Distribution - Version $DATALAYER_VERSION\x1b[0m"
echo

# echo
# echo 🟡 Installing dependencies...
# echo
# cd $DATALAYER_HOME/src && \
#   make ui-install

# echo
# echo 🟡 Building the sources...
# echo
# cd $DATALAYER_HOME/src && \
#   make ui-build

echo
echo 🟡 Building the minified sources...
echo
export ENTRY="./src/IOApp"
cd $DATALAYER_HOME/src/landings/datalayer/ui && \
  yarn build:prod:webpack

# echo
# echo 🟡 Copying needed artifacts to the dist folder...
# echo
# library # http://localhost:3266 # datalayerLibrary.js # NA
# cp -r $DATALAYER_HOME/src/tech/jupyter/.../dist/* $DATALAYER_HOME/src/landings/datalayer/ui/dist

echo
echo 🟡 Seeding Javascript and HTML from the dist folder...
echo
sed -i.bu "s|\"iamServer\": \"http://localhost:9700|\"iamServer\": \"$DATALAYER_RUN_URL|g" $DATALAYER_HOME/src/landings/datalayer/ui/dist/*.html
sed -i.bu "s|\"libraryServer\": \"http://localhost:9800|\"libraryServer\": \"$DATALAYER_RUN_URL|g" $DATALAYER_HOME/src/landings/datalayer/ui/dist/*.html
sed -i.bu "s|\"jupyterServerUrl\": \"http://localhost:8888|\"jupyterServerUrl\": \"$DATALAYER_RUN_URL|g" $DATALAYER_HOME/src/landings/datalayer/ui/dist/*.html
sed -i.bu "s|http://localhost:8686|$DATALAYER_RUN_URL|g" $DATALAYER_HOME/src/landings/datalayer/ui/dist/*.html
sed -i.bu "s|minikube.local|$DATALAYER_RUN_HOST|g" $DATALAYER_HOME/src/landings/datalayer/ui/dist/*.html
sed -i.bu "s|prod1.datalayer.run|$DATALAYER_RUN_HOST|g" $DATALAYER_HOME/src/landings/datalayer/ui/dist/*.html
sed -i.bu "s|src=\"http://localhost:3063|src=\"$DATALAYER_CDN_URL|g" $DATALAYER_HOME/src/landings/datalayer/ui/dist/*.html
sed -i.bu "s|/static/datalayer_ui|$DATALAYER_CDN_URL|g" $DATALAYER_HOME/src/landings/datalayer/ui/dist/*.html
sed -i.bu "s|http://localhost:3063|$DATALAYER_CDN_URL|g" $DATALAYER_HOME/src/landings/datalayer/ui/dist/*.js
sed -i.bu "s|/static/datalayer_ui|$DATALAYER_CDN_URL|g" $DATALAYER_HOME/src/landings/datalayer/ui/dist/*.js

# echo
# echo 🟡 Updating the main javascript
# echo
# MAIN_JS=$(ls $DATALAYER_HOME/src/landings/datalayer/ui/dist/main.*datalayerLibrary.js)
# echo  👉 $MAIN_JS 👉 main.datalayerLibrary.js
# cp $MAIN_JS $DATALAYER_HOME/src/landings/datalayer/ui/dist/main.datalayerLibrary.js

echo
echo 🟡 Removing the backup files in the dist folder...
echo
rm $DATALAYER_HOME/src/landings/datalayer/ui/dist/*.bu

echo
echo -e "\x1b[34m\x1b[43mListing Distribution - Version $DATALAYER_VERSION\x1b[0m"
echo

echo
echo 🟡 Listing the dist folder...
echo
ls $DATALAYER_HOME/src/landings/datalayer/ui/dist

echo
echo 🟡 Showing index.html...
echo
cat $DATALAYER_HOME/src/landings/datalayer/ui/dist/index.html
echo
