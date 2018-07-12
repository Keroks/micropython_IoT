#!/bin/bash

# Upload all mpy files
for f in *.mpy
do
    if [[ ${f} != "main.mpy" ]]; then
        echo "Will upload $f file..."
        bash ampy --port /dev/ttyUSB0 put ${f}
    fi
done

echo "Will upload main.py..."
bash ampy --port /dev/ttyUSB0 put "main.py"