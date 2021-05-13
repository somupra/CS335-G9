from sys import argv
import pydot
import subprocess
import pathlib
from lexer import lexrules
from parser.grammar import parser
from utlis import bfs, dfs
import symbol_table as st 
from errors.error import messages
from parser.grammar import instr

def main():
    import ply.lex as lex
    lexer = lex.lex(module=lexrules)

    # Run a preprocessor
    import sys
 
    filename = sys.argv[1]
    show_asm = sys.argv[2] if len(sys.argv) == 3 else None

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

    

    print("\n\n\n ------------------ 3AC CODE --------------------")
    curr_func = "@global"
    to_asm = {curr_func: []}
    cnt = 0
    for i in range(len(instr)):
        temp_str = instr[i]
        if(temp_str[len(temp_str)-1] == ':'):
            curr_func = instr[i][0: -1]
            to_asm[curr_func] = []
            print(instr[i])
            cnt = cnt+1
            

        else: 
            to_asm[curr_func].append([cnt, instr[i]])
            print("\t", [cnt, instr[i]])
            cnt = cnt+1

    if not show_asm: return 0
    
    from codegen.codegen import assemble
    asm = assemble(to_asm)

    # print to asm file
    asm_lines = asm.full_code()
    asm_fname = filename[: -1] + "s"
    obj_fname = filename[: -1] + "o"
    with open(asm_fname, "w") as asm_file:
        for line in asm_lines:
            asm_file.write(line)

    from linker import assemble_to_obj, link

    assemble_to_obj(asm_fname, obj_fname)

    if not link("out", [obj_fname]):
        print("linker returned non-zero status")
        return 1
    return 0




if __name__ == "__main__":
    main()
