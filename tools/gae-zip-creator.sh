#!/bin/bash
#
# Copyright 2014 Google Inc. All Rights Reserved.
#
# Generates a zip of the google api python client and dependencies.
#
# Author: afshar@google.com (Ali Afshar)

# Exit on failure.
set -e

# Where to build the zip.
ROOT_PATH=$(pwd)/build/gae
BUILD_PATH=${ROOT_PATH}/build
LIB_PATH=${ROOT_PATH}/lib
ENV_PATH=${ROOT_PATH}/ve
LOG_PATH=${ROOT_PATH}/gae_zip_build.log

# The api client version
APICLIENT_VERSION=$(python -c "import apiclient; print apiclient.__version__")

# Where to create the zip.
DIST_PATH=$(pwd)/dist/gae
ZIP_NAME=google-api-python-client-gae-${APICLIENT_VERSION}.zip
ZIP_PATH=${DIST_PATH}/${ZIP_NAME}

# Make sure we are all clean.
echo "Cleaning build env"
rm -rf ${ROOT_PATH}
mkdir -p ${ROOT_PATH}

# We must not use the system pip, since that exposes a bug uninstalling httplib2
# instead, install the dev version of pip.
echo "Creating virtualenv and installing pip==dev"
virtualenv --no-site-packages ${ENV_PATH} >> ${LOG_PATH}
${ENV_PATH}/bin/pip install --upgrade pip==dev >> ${LOG_PATH}

# Install the library with dependencies.
echo "Building google-api-python client"
${ENV_PATH}/bin/pip install -b ${BUILD_PATH} -t ${LIB_PATH} . >> ${LOG_PATH}

# Prune the things we don't want.
echo "Pruning target library"
find ${LIB_PATH} -name "*.pyc" -exec rm {} \; >> ${LOG_PATH}
rm -rf ${LIB_PATH}/*.egg-info >> ${LOG_PATH}

# Create the zip.
echo "Creating zip"
mkdir -p ${DIST_PATH}
pushd ${LIB_PATH} >> ${LOG_PATH}
zip -r ${ZIP_PATH} * >> ${LOG_PATH}
popd >> ${LOG_PATH}

# We are done.
echo "Built zip in ${ZIP_PATH}"

# Sanity test the zip.
# TODO (afshar): Run the complete test suite.
echo "Sanity testing the zip:"
export SANITY_MODS="httplib2 apiclient uritemplate oauth2client"
export SANITY_ZIP=${ZIP_PATH}
export PYTHONPATH=${ZIP_PATH}
${ENV_PATH}/bin/python -c "import sys, os
sys.path.pop(0) # remove the pwd
for name in os.getenv('SANITY_MODS').split():
  mod = __import__(name)
  assert os.getenv('SANITY_ZIP') in mod.__file__
  print ' ', os.path.relpath(mod.__file__)"
