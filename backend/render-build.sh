#!/usr/bin/env bash
# exit on error
set -o errexit

# Store the root path of the project
PROJECT_ROOT=$(pwd)
STORAGE_DIR=/opt/render/project/.render

if [[ ! -d $STORAGE_DIR/chrome ]]; then
  echo "...Downloading Chrome"
  mkdir -p $STORAGE_DIR/chrome
  cd $STORAGE_DIR/chrome
  wget -P ./ https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
  dpkg -x ./google-chrome-stable_current_amd64.deb $STORAGE_DIR/chrome
  rm ./google-chrome-stable_current_amd64.deb
  echo "...Downloaded Chrome"
else
  echo "...Using Chrome from cache"
fi

# Return to project root before installing requirements
cd $PROJECT_ROOT

# Install python dependencies as usual
pip install -r requirements.txt
