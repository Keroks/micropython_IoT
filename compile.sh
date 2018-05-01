#!/usr/bin/env bash

# Compile all files to .mpy format
for f in *.py
do
    echo "Will compile $f file..."
    ~/micropython/mpy-cross/mpy-cross -v ${f}
done
#