#!/bin/bash

# Prompting the user for inputs
read -p "Enter the input file path (JSON schema): " input_file
read -p "Enter the output file path (Python file): " output_file
read -p "Enter the class name: " class_name

poetry run datamodel-codegen \
    --input "$input_file" \
    --input-file-type json \
    --output "$output_file" \
    --snake-case-field \
    --class-name "$class_name"
