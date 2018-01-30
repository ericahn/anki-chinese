#!/bin/bash

# builds zip file for Ankiweb

echo "Finding latest Anki 2.1 addon release"
latestTag=$(git describe --match "addon21.v*" --abbrev=0)
retVal=$?
if [ ! $retVal -eq 0 ]; then
    echo "Error, exiting without building"
    exit $retVal
fi
pyuic5 -o addon21/pinyin/gui/forms/ruby.py Ruby.ui
outFile="builds/anki-chinese-$latestTag.zip"
echo "Found, building $outFile"
git archive --format zip --output "$outFile" "$latestTag":addon21

