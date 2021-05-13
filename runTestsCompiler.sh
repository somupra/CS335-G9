#!/usr/bin/env bash

test () {
	printf "\n\nPARSER TEST $1 RESULTS \n"
	python ./src/main.py tests/codegen/test$1.c 
}

# tests
test 7
dot -Tps output_raw.dot -o tree_result1.ps
#test 2
#dot -Tps output_raw.dot -o tree_result2.ps
#test 3
#dot -Tps output_raw.dot -o tree_result3.ps
#test 4
#dot -Tps output_raw.dot -o tree_result4.ps
#test 5
#dot -Tps output_raw.dot -o tree_result5.ps

# cleanup pycache and out files
[ -d ./src/__pycache__ ] && rm -rf ./src/__pycache__
[ -f ./*.out ] && rm *.out
[ -f ./*.o ] && rm *.o
