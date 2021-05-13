#!/usr/bin/env bash
test () {
	printf "\n\nFINAL TEST $1 RESULTS \n"
	python ./src/main.py tests/final/test$1.c >> dump.txt
	./out
}

# tests
test 1
test 2
test 3
test 4

# cleanup pycache and out files
[ -d ./src/__pycache__ ] && rm -rf ./src/__pycache__
[ -f ./*.out ] && rm *.out
[ -f ./*.o ] && rm *.o
