#!/usr/bin/env bash

test () {
	python ./src/lexer.py tests/test$1.c 
}

echo "-------------------------------- TEST 1 ---------------------------------"
# tests
test 1 

# cleanup pycache 
[ -d ./src/__pycache__ ] && rm -rf ./src/__pycache__