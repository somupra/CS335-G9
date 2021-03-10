import lexrules
import ply.lex as lex
from grammar import parser

def bfs(node):
    if node:
        if isinstance(node, str):
            print(node)
            return

        print(node.leaf)
        for c in node.children:
            bfs(c)
    return

if __name__ == '__main__':
    import ply.lex as lex
    lexer = lex.lex(module=lexrules)

    # Run a preprocessor
    import sys
    with open(sys.argv[1]) as f:
        input = f.read()

    obj = parser.parse(input=input, lexer=lexer)
    print(obj)
    bfs(obj)