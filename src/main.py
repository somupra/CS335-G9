import pydot
from lexer import lexrules
from parser.grammar import parser
from utlis import bfs, dfs
import symbol_table as st 
from errors.error import messages
from parser.grammar import instr
from code import assembly

def main():
	import ply.lex as lex
	lexer = lex.lex(module=lexrules)

	# Run a preprocessor
	import sys
 
	filename = sys.argv[1]

	with open(sys.argv[1]) as f:
		input = f.read()

	obj = parser.parse(input=input, lexer=lexer, tracking=True)

	if not messages.ok:
		return

	# bfs(obj)
	#print(obj)
	graph = pydot.Dot('my_graph', graph_type='graph', bgcolor='yellow')
	graph.add_node(pydot.Node(0,label = obj.type, shape='circle'))
	for child in obj.children:
		dfs(child,0,graph)
	graph.write_raw('output_raw.dot')
	# I'm passing the parent to the dfs function call.
	st.give_out(filename)
	for i in range(len(instr)):
		print(instr[i])
	#assembly()

if __name__ == "__main__":
	main()
