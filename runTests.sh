#!/usr/bin/env bash

test () {
	printf "\n\nTEST $1 RESULTS \n"
	python ./src/lexer.py tests/test$1.c 
}

# tests
# test 1 
# test 2
# test 3
# test 4
test 5

# cleanup pycache 
[ -d ./src/__pycache__ ] && rm -rf ./src/__pycache__