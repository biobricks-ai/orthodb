#!/usr/bin/env bash

# Script to download files

# Get local path
localpath=$(pwd)
echo "Local path: $localpath"

# Create the list directory to save list of remote files and directories
listpath="$localpath/list"
echo "List path: $listpath"
mkdir -p $listpath
cd $listpath;

# Define the HTTP base address
export URL='https://data.orthodb.org/v12/download/'

# Retrieve the list of files to download from HTTP base address.
# If this changes, then the downloads need to change.
wget -P "$list" "$URL"

echo "Download done."
