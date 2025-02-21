#!/usr/bin/env bash

# Script to download files

# Get local path
localpath=$(pwd)
echo "Local path: $localpath"

# Define the HTTP base address
export URL='https://data.orthodb.org/v12/download/'

# Create the download directory
export downloadpath="$localpath/download"
echo "Download path: $downloadpath"
mkdir -p "$downloadpath"
cd $downloadpath;

# Retrieve the list of files to download from FTP base address
# NOTE: Not downloading the larger FASTA files for now.
wget -P "$downloadpath" \
  --mirror -np \
  -A '*.tab.gz,*.txt' \
  --no-host-directories \
  --cut-dirs=2 \
  "$URL"

echo "Download done."
