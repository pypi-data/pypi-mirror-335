#!/bin/bash
set -e

# if [[ "$OSTYPE" == "msys" ]]; then
#     powershell -Command "& '.\download-lib.bat'"
#     exit
# fi

cd ${0%/*}
SCRIPT_DIR=$(pwd)

# url settings
LIB_VERSION="v0.0.4"
URL="https://app.brainco.cn/universal/treadmill/libs/${LIB_VERSION}"

# colorful echo functions
function echo_y() { echo -e "\033[1;33m$@\033[0m"; } # yellow
function echo_r() { echo -e "\033[0;31m$@\033[0m"; } # red

# 1. check version from VERSION file
if [ -f VERSION ] && grep --fixed-strings --quiet ${LIB_VERSION} VERSION; then
  echo_y "[treadmill-sdk] (${LIB_VERSION}) is already installed"
  cat VERSION
  exit
fi

# clean files
rm -rf libs

# download library
LIB_NAME="libs"
platform=$(uname)
if [ "$platform" == "Linux" ]; then
  LIB_NAME="linux"
elif [ "$platform" == "Darwin" ]; then
  LIB_NAME="mac"
elif [[ "$OSTYPE" == "msys" ]]; then
  LIB_NAME="win"
else
  echo_r "This script does not support your platform ($platform)"
  exit 1
fi

echo_y "[treadmill-sdk] download (${LIB_VERSION}) ..."

ZIP_NAME="$LIB_NAME.zip"
wget ${URL}/$ZIP_NAME?$RANDOM -O $ZIP_NAME
unzip -o $ZIP_NAME -d .
rm $ZIP_NAME
rm -rf __MACOSX

# 4. create VERSION file
echo "[treadmill-sdk] Version: ${LIB_VERSION}" >VERSION
echo "Update Time: $(date)" >>VERSION

echo_y "[treadmill-sdk] (${LIB_VERSION}) is downloaded"
