#!/usr/bin/env bash

# install xcode
xcode-select --install

# install Homebrew
ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"

# install Python 2.7
brew install python

# install PyQt4
brew install cartr/qt4/pyqt
