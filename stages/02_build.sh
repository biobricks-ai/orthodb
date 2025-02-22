#!/usr/bin/env bash

# Script to process unzipped files and build parquet files

# Get local path
localpath=$(pwd)
echo "Local path: $localpath"

# Create brick directory
export brickpath="$localpath/brick"
mkdir -p $brickpath
echo "Brick path: $brickpath"

find download/ \
  -type f -name '*.tab.gz' \
  | parallel '
      python3 stages/csv2parquet.py  {} brick/{/.}.parquet
'

