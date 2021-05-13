#!/usr/bin/env bash

test () {
	printf "\n\nPARSER TEST $1 RESULTS \n"
	python ./src/main.py tests/codegen/test$1.c 
}

# tests
test 1
test 2
test 3
test 4
test 5
test 6
test 7

[ -d ./src/__pycache__ ] && rm -rf ./src/__pycache__
[ -f ./*.out ] && rm *.out
[ -f ./*.o ] && rm *.o
