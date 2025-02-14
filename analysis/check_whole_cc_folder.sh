#!/bin/bash

filters=("0-50-200-1 0-50-200-2 0-50-1000-1 0-50-1000-2 0-100-200-1 0-100-200-2 0-100-1000-1 0-100-1000-2 0-100-200-4 0-100-200-8 0-100-200-12 0-100-200-16")

folder=$1
echo "Checking folder $folder"

plot=$2

for filter in ${filters[@]}; do
    echo "Checking filter $filter"
    python3 final/check_cc_folder.py $folder $filter $2 "$filter.res"
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