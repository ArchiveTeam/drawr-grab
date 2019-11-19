#!/bin/sh -e

if ! sudo pip3 freeze | grep -q py3amf
then
  echo "Installing py3amf"
  if ! sudo pip3 install py3amf
  then
    exit 1
  fi
fi
