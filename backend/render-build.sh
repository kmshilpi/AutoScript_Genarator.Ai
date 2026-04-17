#!/usr/bin/env bash
# exit on error
set -o errexit

# Store the root path of the project
PROJECT_ROOT=$(pwd)
STORAGE_DIR=/opt/render/project/.render

if [[ ! -d $STORAGE_DIR/chrome ]]; then
  echo "...Downloading Chrome"
  rm -rf $STORAGE_DIR/chrome
  mkdir -p $STORAGE_DIR/chrome
  cd $STORAGE_DIR/chrome
  wget -q -P ./ https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
  dpkg -x ./google-chrome-stable_current_amd64.deb $STORAGE_DIR/chrome
  rm ./google-chrome-stable_current_amd64.deb
  
  echo "...Downloading matching ChromeDriver"
  DRIVER_URL=$(curl -s https://googlechromelabs.github.io/chrome-for-testing/last-known-good-versions-with-downloads.json | grep -o 'https://storage.googleapis.com/chrome-for-testing-public/[^"]*linux64/chromedriver-linux64.zip' | head -n 1)
  wget -q -O chromedriver.zip "$DRIVER_URL"
  unzip -q chromedriver.zip
  mv chromedriver-linux64/chromedriver ./
  chmod +x ./chromedriver
  rm -rf chromedriver-linux64 chromedriver.zip
  echo "...Downloaded Chrome and ChromeDriver"
else
  echo "...Using Chrome from cache"
fi

# Return to project root before installing requirements
cd $PROJECT_ROOT

# Install python dependencies as usual
pip install -r requirements.txt
