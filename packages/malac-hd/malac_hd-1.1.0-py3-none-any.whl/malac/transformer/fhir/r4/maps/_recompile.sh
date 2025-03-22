#!/bin/bash

# Compile all FML maps in this folder to the parent folder (except helper)
curr_dir=$(dirname "$0")
parent_dir=$(dirname ${curr_dir})
for dir in ${curr_dir}/*
do
    rel_path=${dir%*/}
    full_name=${rel_path%.*}
    base_name=$(basename ${full_name})
    if [ "$base_name" != "helper" ]; then
        malac-hd -m ${rel_path} -co ${parent_dir}/${base_name}.py -s
    fi
done