import pydot
from lexer import lexrules
from parser.grammar import parser
from utlis import bfs, dfs
import symbol_table as st 
from errors.error import messages
from parser.grammar import instr
from codegen.codegen import assembly

def main():
	import ply.lex as lex
	lexer = lex.lex(module=lexrules)

	# Run a preprocessor
	import sys
 
	filename = sys.argv[1]

	with open(sys.argv[1]) as f:
		input = f.read()

	lexer.input(input)

	while(1):
		tok = lexer.token()
		if not tok:
			break
		if tok.type=='STRING':
			st.list_of_strings.append(tok.value[1:-1])
		
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

	to_asm = []
	cnt = 0
	for i in range(len(instr)):
		temp_str = instr[i]
		if(temp_str[len(temp_str)-1] == ':'):
			to_asm.append(("label", instr[i]))
			print(instr[i])
			cnt = cnt+1
			

		else: 
			to_asm.append(("command", instr[i]))
			print("\t", [cnt, instr[i]])
			cnt = cnt+1

	from codegen.codegen import assemble
	assemble(to_asm)

if __name__ == "__main__":
	main()
