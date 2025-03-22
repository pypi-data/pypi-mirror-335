#!/bin/bash
#
# Simple script that tries to fetch the changes between two versions in a
# format that is used in the file bdsf/_changelog.py. The output may need
# some manual curation.

[[ $# -eq 2 ]] || { echo "Usage $0 <old-version> <new-version>"; exit 1; }

git log --pretty=format:"    %ad - %s%n" --date=format:"%Y/%m/%d" "$1".."$2"
