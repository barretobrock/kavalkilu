#!/usr/bin/env bash
# Creates necessary directories if they don't already exist

# Array of directories to make
dirs=( "logs" "data" "keys" )

cd

# Loop through array
for d in "${dirs[@]}"
do
    if [[ ! -e ${d} ]]; then
        # If directory doesn't exist, make it
        mkdir ${d}
        echo "Making directory: ${d}"
    fi
done
