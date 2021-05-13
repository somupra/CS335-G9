import sys 
import io
import os
import csv

allsymboltables = []
symtabtrack = []
curr_scope_labels = {}
goto_ref = {}
func_params = {}
offset = 0
size = {}
size['INT']=4
size['FLOAT']=4
size['CHAR']=1

list_of_strings = []

class SymbolTable:
    def __init__(self, parent):
        self.parent_idx = parent
        self.child_idx = []
        self.labels = {}
        # var_name : line_no
        self.variables = {}
        # var_name : {type : .. lineno : ..}
        self.structures = {}
        # struct name : [table_index, size_of_struct(in terms of padded offset)]
        self.functions = {}
        # Function name : (SymbolTableindex,no.of args,return_type)


# 0 is the index of global symbol table
table_just_made = 0
symtabtrack.append(0)
global_symtab = SymbolTable(None)# parent is none
allsymboltables.append(global_symtab)


def checkscope():
    return symtabtrack[-1]


def add_function_params(names,types):
    for i in range(0,len(names)):
        func_params[names[i]]=types[i]

def newscope():
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
def make_func_entry(names,types,ret_type):
    #print("TABLE JUST MADE", table_just_made)
    parent_idx = symtabtrack[-1] # Last index is the parent of this new one
    allsymboltables[parent_idx].functions[names[0]] = [table_just_made, len(names)-1,ret_type]# Changing the type of variable to function

    global offset
    for i in range(1,len(names)):
        allsymboltables[table_just_made].variables[names[i]] = {} # Changing the type of variable to function
        allsymboltables[table_just_made].variables[names[i]]["type"]=types[i]

        if isinstance(types[i],list):#IS AN ARRAY
            allsymboltables[table_just_made].variables[names[i]]["offset"]=offset
            x = 1
            # Assuming the size of array is known. Unknown size array not dealt with, eg arr[], arr[][5]
            for j in types[i][2]:
                x=x*j
            offset=offset + x*size[type[3]] + (x*size[type[3]])%8
        '''
        if types[i]=='strct_or_union':
            allsymboltables[table_just_made].variables[names[i]]["size"]=check_in_structures[1]
            allsymboltables[table_just_made].variables[names[i]]["offset"]=offset
            offset+=check_in_structures[1]
        '''
        if types[i]=='INT':
            allsymboltables[table_just_made].variables[names[i]]["offset"]=offset
            allsymboltables[table_just_made].variables[names[i]]["size"]=4
            offset+=4
        elif types[i]=='FLOAT':
            allsymboltables[table_just_made].variables[names[i]]["offset"]=offset
            allsymboltables[table_just_made].variables[names[i]]["size"]=4
            offset+=4
        elif types[i]=='CHAR':
            allsymboltables[table_just_made].variables[names[i]]["offset"]=offset
            allsymboltables[table_just_made].variables[names[i]]["size"]=1
            offset+=1
        elif types[i][:8]=='pointer_':
            allsymboltables[table_just_made].variables[names[i]]["offset"]=offset
            allsymboltables[table_just_made].variables[names[i]]["size"]=4
            offset+=4

    offset = 0
    global goto_ref
    global curr_scope_labels
    for i in goto_ref:
        if curr_scope_labels.get(i)==None:
            print("LABEL NOT DECLARED")
    for i in curr_scope_labels:
        allsymboltables[table_just_made].labels[i]=curr_scope_labels[i]
    goto_ref = {}
    curr_scope_labels = {}
    global func_params
    func_params = {}

def make_struct_entry(name):
    parent_idx = symtabtrack[-1] # Last index is the parent of this new one
    allsymboltables[parent_idx].structures[name] = [table_just_made] # Changing the type of variable to structure
    # Storing the offset information of the variables in a structure.
    # x is the space to be reserved for every occurance of the struct 
    keys = list(allsymboltables[table_just_made].variables)
    x = allsymboltables[table_just_made].variables[keys[-1]]['offset']+allsymboltables[table_just_made].variables[keys[-1]]['size']
    x = x+x%8
    allsymboltables[parent_idx].structures[name].append(x)


# Checks from current scope table till global
def check_in_var(name):
    curr_table = allsymboltables[symtabtrack[-1]]
    while(1):
        if curr_table.variables.get(name)!=None:
            return curr_table.variables.get(name)
        if curr_table.parent_idx==None:
            break
        curr_table = allsymboltables[curr_table.parent_idx]

    if func_params.get(name)!=None:
        return func_params.get(name)

    if allsymboltables[0].functions.get(name)!=None:
        return allsymboltables[0].functions.get(name)[2]
    return None # Not found

def var_curr_scope_exists(name):
    curr_table = allsymboltables[symtabtrack[-1]]
    if curr_table.variables.get(name)!=None:
        return True#Name already exists
    else:
        return False#Name doesnt exist

def func_exists(name):
    curr_table = allsymboltables[0]# Will always be global scope
    if curr_table.functions.get(name)!=None:
        return True#Name already exists
    else:
        return False#Name doesnt exist 

def struct_union_exists(name):
    curr_table = allsymboltables[symtabtrack[-1]]
    if curr_table.structures.get(name)!=None:
        return True#Name already exists
    else:
        return False#Name doesnt exist



def check_in_fs(name):

    curr_table = allsymboltables[symtabtrack[-1]]
    while(1): # Returning the index of local symtab of the particular func name
        if curr_table.functions.get(name)!=None:
            return curr_table.functions.get(name)
        if curr_table.structures.get(name)!=None:
            return curr_table.structures.get(name)
        if curr_table.parent_idx==None:
            break
        curr_table = allsymboltables[curr_table.parent_idx]
    return None # Not found

def get_max_fn_offset(fname):
    fn_symtab = allsymboltables[check_in_fs(fname)[0]]
    offsets = [var for var in fn_symtab.variables.values()]
    max_offset = offsets[-1]["offset"] + offsets[-1]["size"]
    if max_offset % 16 != 0:
            max_offset += 16 - max_offset % 16
    return max_offset

def traverse(sym_tab, vars):
    vars = {**vars, **(sym_tab.variables)}
    for child in sym_tab.child_idx:
        vars = {**vars, **(allsymboltables[child].variables)}
        traverse(allsymboltables[child], vars)
    return vars


def get_var_info(fname):
    fn_symtab = allsymboltables[check_in_fs(fname)[0]]
    vars = traverse(fn_symtab, {})
    return vars

def check_in_structures(name):
    curr_table = allsymboltables[symtabtrack[-1]]
    while(1): # Returning the index of local symtab of the particular func name
        if curr_table.structures.get(name)!=None:
            return curr_table.structures.get(name)
        if curr_table.parent_idx==None:
            break
        curr_table = allsymboltables[curr_table.parent_idx]

    return None # Not found


def make_var_entry(name,type,init,value):
    allsymboltables[symtabtrack[-1]].variables[name]={}
    allsymboltables[symtabtrack[-1]].variables[name]["type"]=type
    allsymboltables[symtabtrack[-1]].variables[name]["init"]=init
    allsymboltables[symtabtrack[-1]].variables[name]["value"]=value
    
    global offset
    if isinstance(type,list):
        allsymboltables[symtabtrack[-1]].variables[name]["offset"]=offset
        x = 1
        # Assuming the size of array is known. Unknown size array not dealt with, eg arr[], arr[][5]
        for j in type[2]:
            x=x*j
        offset=offset + x*size[type[3]] + (x*size[type[3]])%8
    '''
    if type=='struct_or_union':
        allsymboltables[symtabtrack[-1]].variables[name]["size"]=check_in_structures()[1]
        allsymboltables[symtabtrack[-1]].variables[name]["offset"]=offset
        offset+=check_in_structures[1]
    '''
    if type=='INT':
        allsymboltables[symtabtrack[-1]].variables[name]["size"]=4
        allsymboltables[symtabtrack[-1]].variables[name]["offset"]=offset
        offset+=4
    if type=='CHAR':
        allsymboltables[symtabtrack[-1]].variables[name]["size"]=1
        allsymboltables[symtabtrack[-1]].variables[name]["offset"]=offset
        offset+=1
    if type=='FLOAT':
        allsymboltables[symtabtrack[-1]].variables[name]["size"]=4
        allsymboltables[symtabtrack[-1]].variables[name]["offset"]=offset
        offset+=4
    if type[:8]=='pointer_':
        allsymboltables[symtabtrack[-1]].variables[name]["size"]=4
        allsymboltables[symtabtrack[-1]].variables[name]["offset"]=offset
        offset+=4


#Check for redeclaration error of labels here
def add_label(name,lineno):
    if(curr_scope_labels.get(name)!=None):
        print("DUPLICATE LABEL : redeclaration\n")
    else:
        curr_scope_labels[name]=lineno
def add_goto_ref(name,lineno):
    goto_ref[name]=lineno


def print_prefix(level):
    """Print a prefix level deep for pretty printing."""
    dash = "\x1B[33m"
    bold = "\033[1m"
    reset = "\x1B[0m"
    for _ in range(level):
        print("  ", end=" ")
    print(f"{bold}{dash}| - {reset}", end=" ")

def print_out (node_idx, level):
    dash = "\x1B[33m"
    bold = "\033[1m"
    reset = "\x1B[0m"
    print_prefix(level)
    print("TABLE    : ", node_idx)
    print_prefix(level)
    print("CHILDREN : ", allsymboltables[node_idx].child_idx)
    print_prefix(level)
    print("VARS     : ", allsymboltables[node_idx].variables)
    print_prefix(level)
    print("FUNCS    : ", allsymboltables[node_idx].functions)
    print_prefix(level)
    print("STRUCTS  : ", allsymboltables[node_idx].structures)
    print_prefix(level)
    print("LABELS   : ", allsymboltables[node_idx].labels)
    print_prefix(level)
    print(f"{bold}{dash}---------------------------------------------------{reset}")

    for x in allsymboltables[node_idx].child_idx:
        print_out(x, level+1)

def print_to_csv(i,filename):
    old_stdout = sys.stdout
    new_stdout = io.StringIO()
    sys.stdout = new_stdout
    
    print(i,',',end='') #TABLE NUMBER
    print(allsymboltables[i].child_idx,',',end='') #CHILDREN
    #VARS
    for x in allsymboltables[i].variables:
        print(x,allsymboltables[i].variables[x],end=' ')
    print(',',end='')
    #FUNCS
    for x in allsymboltables[i].functions:
        print(x,allsymboltables[i].functions[x],end=' ')
    print(',',end='')
    #STRUCTS 
    for x in allsymboltables[i].structures:
        print(x,allsymboltables[i].structures[x],end=' ')
    print(',',end='')
    #LABELS
    for x in allsymboltables[i].labels:
        print(x,end=' ')
    print('\n')
    
    output = new_stdout.getvalue()
    sys.stdout = old_stdout

    if os.path.isfile(filename):
        with open(filename,'a',newline='') as file:
            file.write(output)
    else:
        with open(filename, 'w', newline='') as file:
            fieldnames = ['TABLE NUMBER ', 'CHILDREN ', 'VARS ', 'FUNCS ', 'STRUCTS ', 'LABELS']
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            file.write(output)

def give_out(filename):
    base_dir = "tests/parser/output/"
    important = "\x1b[36m"
    bold = "\033[1m"
    reset = "\x1B[0m"
    success = "\x1b[32m"
    print(f"\n\n{bold}{important} SYMBOL TABLE {reset}\n\n")
    print_out(0, 0)

    slash = str(filename).rfind("/")
    filename = filename[slash+1 : ]
    op_filename = base_dir + "output_"+filename[:-2]+".txt"
    print_to_csv(0, op_filename)
