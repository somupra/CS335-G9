import lexrules
import ply.lex as lex
from grammar import parser
import pydot

def bfs(node):
    if node:
        if isinstance(node, str):
            print(node)
            return

        print(node.leaf)
        for c in node.children:
            bfs(c)
    return


class Node:
    def __init__(self, type, children=None, leaf=None):
        self.type = type
        if children:
            self.children = children
        else:
            self.children = [ ]
        self.leaf = leaf
        
i=0
def dfs(node,i):
    graph = pydot.Dot('my_graph', graph_type='graph', bgcolor='yellow')
    graph.add_node(pydot.Node(i,label = node.type, shape='circle'))
    parent = i
    i+=1
    
    
    if node.children:
        for child in node.children:
            if child is None:
                continue
            if isinstance(child,str):
                graph.add_node(pydot.Node(i,label = child, shape='circle'))
            else:
                graph.add_node(pydot.Node(i,label = child.type, shape='circle'))
            graph.add_edge(pydot.Edge(parent, i))
            i+=1
            if isinstance(child,str):
                continue
            dfs(child,i)
            
    else:
        if node.leaf:
            for child in node.leaf:
                if child is None:
                    continue
                if isinstance(child,str):
                    graph.add_node(pydot.Node(i,label = child, shape='circle'))
                else:
                    graph.add_node(pydot.Node(i,label = child.type, shape='circle'))
                graph.add_edge(pydot.Edge(parent, i))
                i+=1
    graph.write_raw('output_raw.dot')



if __name__ == '__main__':
    import ply.lex as lex
    lexer = lex.lex(module=lexrules)

    # Run a preprocessor
    import sys
    with open(sys.argv[1]) as f:
        input = f.read()

    obj = parser.parse(input=input, lexer=lexer)
    print(obj)
    dfs(obj,0)
    
