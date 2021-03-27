import lexrules
import ply.lex as lex
from grammar import parser
import pydot

def bfs(node):
    if node:
        if isinstance(node, str):
            #print("***",node)
            return

        if node.leaf!=None : print(node.leaf,node.type)
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

node_num = 0
def dfs(node,parent,graph):
    #print("PARENT IS", parent)
    leaf_present=False
    if node.leaf:
        child = node.leaf
        #print("###########", child)
        if isinstance(child,str):
            global node_num
            node_num = node_num + 1
            #print("LEAF NODE IS",node_num,node.type)
            #print("+++++++++++++++", child)
            graph.add_node(pydot.Node(node_num,label = child, shape='circle'))  
            graph.add_edge(pydot.Edge(parent, node_num))
            parent = node_num
        else:
            #print("\n ADDING leaf from ANOTHER DFS CALL\n")
            dfs(child,parent,graph)
            parent = node_num #CHECKK ****


    
    if node.children:
        for child in node.children:
            if child is None:
                continue
            if isinstance(child,str):
                node_num+=1 # Increment the node number just before adding a node.
                #print("-----------------leaf and child added simultaneously-------------------")
                graph.add_node(pydot.Node(node_num,label = child, shape='circle'))
                graph.add_edge(pydot.Edge(parent, node_num))
            else:
                #print(node.leaf,"  111  ",node.type)
                dfs(child,parent,graph)

                  

    





if __name__ == '__main__':
    import ply.lex as lex
    lexer = lex.lex(module=lexrules)

    # Run a preprocessor
    import sys
    with open(sys.argv[1]) as f:
        input = f.read()

    obj = parser.parse(input=input, lexer=lexer)
    bfs(obj)
    #print(obj)
    graph = pydot.Dot('my_graph', graph_type='graph', bgcolor='yellow')
    graph.add_node(pydot.Node(0,label = obj.type, shape='circle'))
    for child in obj.children:
        dfs(child,0,graph)
    graph.write_raw('output_raw.dot')
    # I'm passing the parent to the dfs function call.
