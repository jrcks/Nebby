#!/bin/bash

filters=("0-50-200-1 0-50-200-2 0-50-1000-1 0-50-1000-2 0-100-200-1 0-100-200-2 0-100-1000-1 0-100-1000-2")

folder=$1
echo "Checking folder $folder"

for filter in ${filters[@]}; do
    echo "Checking filter $filter"
    python3 final/check_cc_folder.py $folder $filter n "$filter.res"
done

if [ -z "$2" ]; then
    exit 0
fi

echo ""
echo "===================="
echo ""

for filter in ${filters[@]}; do
    echo "Filter: $filter"
    cat "$filter.res"
done