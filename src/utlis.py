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
	leaf_present = False
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

				  
node_nu = 0

def parse_tree(node,parent,graph):
	global node_nu
	if node.leaf:
		child = node.leaf
		#print("###########", child)
		node_nu = node_nu + 1
		if isinstance(child,str):
			#print("LEAF NODE IS",node_num,node.type)
			#print("+++++++++++++++", child)
			graph.add_node(pydot.Node(node_nu,label = child, shape='circle'))  
			graph.add_edge(pydot.Edge(parent, node_nu))
			parent = node_nu
		else:
			#print("LEAF NODE IS",node_num,node.type)
			#print("+++++++++++++++", child)
			graph.add_node(pydot.Node(node_nu,label = child.name, shape='circle'))  
			graph.add_edge(pydot.Edge(parent, node_nu))
			parent = node_nu
			#print("\n ADDING leaf from ANOTHER DFS CALL\n")
			parse_tree(child,parent,graph)
			parent = node_nu #CHECKK ****


	
	if node.children:
		for child in node.children:
			if child is None:
				continue
			if isinstance(child,str):
				node_nu = node_nu + 1
				#print("-----------------leaf and child added simultaneously-------------------")
				graph.add_node(pydot.Node(node_nu,label = child, shape='circle'))
				graph.add_edge(pydot.Edge(parent, node_nu))
			else:
				node_nu = node_nu + 1
				#print("LEAF NODE IS",node_num,node.type)
				#print("+++++++++++++++", child)
				graph.add_node(pydot.Node(node_nu,label = child.name, shape='circle'))  
				graph.add_edge(pydot.Edge(parent, node_nu))
				old_parent = parent
				parent = node_nu
				#print(node.leaf,"  111  ",node.type)
				parse_tree(child,parent,graph)
				parent = old_parent