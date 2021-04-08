
allsymboltables = []
symtabtrack = []
curr_scope_labels = {}
goto_ref = {}

class SymbolTable:
    def __init__(self, parent):
        self.parent_idx = parent
        self.child_idx = []
        self.labels = {}
        # var_name : line_no
        self.variables = {}
        # var_name : {type : .. lineno : ..}
        self.structures = {}
        # struct name : SymbolTableindex
        self.functions = {}
        # Function name : (SymbolTableindex,no.of args)
        self.ret_type = None # In case the symbol table is that of a function, we can store its return type.
        self.num_args = 0 #NUmber of args info for a function


# 0 is the index of global symbol table
table_just_made = 0
def newscope():
    if (len(allsymboltables)==0):
        globalsymtab = SymbolTable(None)
        allsymboltables.append(globalsymtab)
        symtabtrack.append(0)
    # Made global symtab in first call
    new_index = len(allsymboltables)
    parent_idx = symtabtrack[-1] # Last index is the parent of this new one
    new_symtab = SymbolTable(parent_idx)
    allsymboltables.append(new_symtab)
    allsymboltables[parent_idx].child_idx.append(new_index) # Adding new symbol table as the child.
    symtabtrack.append(new_index) # This structure is the new scope
    #print("IN NEW SCOPE, NEW INDEX IS", new_index)


def endscope():
    global table_just_made
    table_just_made = symtabtrack[-1]
    symtabtrack.pop()


# Make the entries of function in parent and arguments iof func in func table
def make_func_entry(names,types):
    #print("TABLE JUST MADE", table_just_made)
    parent_idx = symtabtrack[-1] # Last index is the parent of this new one
    allsymboltables[parent_idx].functions[names[0]] = [table_just_made, len(names)-1]# Changing the type of variable to function
    for i in range(1,len(names)):
        allsymboltables[table_just_made].variables[names[i]] = {} # Changing the type of variable to function
        allsymboltables[table_just_made].variables[names[i]]["type"]=types[i]
    global goto_ref
    global curr_scope_labels
    for i in goto_ref:
        if curr_scope_labels.get(i)==None:
            print("LABEL NOT DECLARED")
    for i in curr_scope_labels:
        allsymboltables[table_just_made].labels[i]=curr_scope_labels[i]
    goto_ref = {}
    curr_scope_labels = {}

def make_struct_entry(name):
    parent_idx = symtabtrack[-1] # Last index is the parent of this new one
    allsymboltables[parent_idx].structures[name] = table_just_made # Changing the type of variable to structure

# Checks from current scope table till global
def check_in_var(name):
    curr_table = allsymboltables[symtabtrack[-1]]
    while(1):
        if curr_table.variables.get(name)!=None:
            return curr_table.variables.get(name)
        if curr_table.parent_idx==None:
            break
        curr_table = allsymboltables[curr_table.parent_idx]
    return None # Not found


def check_in_fs(name):
    curr_table = allsymboltables[symtabtrack[-1]]
    while(1): # Returning the index of local symtab of the particular func name
        if curr_table.functions.get(name)!=None:
            return curr_table.functions.get(name[0])
        if curr_table.structures.get(name)!=None:
            return curr_table.structures.get(name)
        if curr_table.parent_idx==None:
            break
        curr_table = allsymboltables[curr_table.parent_idx]
    return None # Not found


def make_var_entry(name,type):
    allsymboltables[symtabtrack[-1]].variables[name]={}
    allsymboltables[symtabtrack[-1]].variables[name]["type"]=type


#Check for redeclaration error of labels here
def add_label(name,lineno):
    if(curr_scope_labels.get(name)!=None):
        print("DUPLICATE LABEL : redeclaration\n")
    else:
        curr_scope_labels[name]=lineno
def add_goto_ref(name,lineno):
    goto_ref[name]=lineno


def print_out(i):
    print("TABLE NUMBER ",i)
    print("CHILDREN",allsymboltables[i].child_idx,"\n")
    print("VARS :")
    for x in allsymboltables[i].variables:
        print(x,allsymboltables[i].variables[x])
    print("FUNCS :")
    for x in allsymboltables[i].functions:
        print(x,allsymboltables[i].functions[x])
    print("STRUCTS :")
    for x in allsymboltables[i].structures:
        print(x,allsymboltables[i].structures[x])
    
    print("LABELS :")
    for x in allsymboltables[i].labels:
        print(x)
    print("-----------------------------------------")
    for x in allsymboltables[i].child_idx:
        print_out(x)

def give_out():
    print_out(0)

