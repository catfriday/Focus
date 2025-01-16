#!/bin/bash

cd ../
mkdir $1
rsync -a --exclude .venv --exclude .git --exclude .pytest_cache --exclude .mypy_cache ./backend-engineer-interview/ ./$1/
zip "$1.zip" -r ./$1
rm -rf $1