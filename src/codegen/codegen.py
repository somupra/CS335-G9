import symbol_table
from parser.grammar import instr

current_function = 'main'
code = []
regs = ['RBX','RCX','RDX','RSI','RDI']

def param(x):
    # x can be int, float, char or tmp@
    if '@' in x:
        # temporary var : To be completed
        code.append('')
    elif x[0]=='\'':
        # char : push 'a'
        code.append('push '+x[:x.find(',scope')])
    elif x[:x.find(',scope')].isnumeric() or x[0]=='0':
        # int : push 10 / push 0x10
        code.append('push '+x[:x.find(',scope')])
    else:
        # Normal variable, get scope, get offset, use stack address to get value
        var_name = x[:x.find(',scope')]
        sym_tab = int(x[x.find(',scope')+6:])
        # finding the variable from current scope till global
        while sym_tab!= None and symbol_table.allsymboltables[sym_tab].variables.get(var_name)==None :
            sym_tab = symbol_table.allsymboltables[sym_tab].parent_idx
        
        offset = symbol_table.allsymboltables[sym_tab].variables[var_name]['offset']
        code.append('push [ebp-'+str(4+offset)+']')


def call_begin(x):
    #Fulfills both caller and callee partially.
    name = x[:x.find(',')]
    # CALLER PART
    code.append('push rax')
    code.append('push rbx')
    code.append('push rcx')
    code.append('push rdx')
    code.append('push rsi')
    code.append('push rdi')
    code.append('call '+name)# is this the right instr? call func? func is the label here before the function code, similar to goto labels.
    # CALL END, CALLER PART :
    code.append('pop rdi')
    code.append('pop rsi')
    code.append('pop rdx')
    code.append('pop rcx')
    code.append('pop rbx')
    code.append('pop rax')
    # assuming call be value and each param of size 8Bytes
    func_details = symbol_table.check_in_fs(name)
    # func_details - 0 is table id and 1 is no of params
    space_for_params = func_details[1]*8
    code.append('add rsp, byte '+str(space_for_params))


def returnn(ret_val):
    # Assuming 8Bytes and that ret_val is the memory address that has the return value
    code.append('mov rax, '+str(ret_val))
    if current_function == 'main':
        return
    code.append('mov rsp, rbp') # move ebp into esp  
    code.append('pop rbp')
    code.append('ret')


def print_call():
    code.append('push rax')
    code.append('push rsi')
    code.append('push rdi')
    code.append('push rdx')
    code.append('mov rax,1')
    code.append('mov rsi,msg')
    code.append('mov rdi,1')
    code.append('mov rdx,10')
    code.append('syscall')
    code.append('pop rdx')
    code.append('pop rdi')
    code.append('pop rsi')
    code.append('pop rax')


def func_begin(name):
    code.append(name)# name consists : too. so label done
    # CALLEE PART
    name = name[:-1]
    global current_function
    current_function = name
    if name == 'main':
        return
    code.append('push rbp')
    code.append('mov  rbp, rsp')
    # Getting the symtab entry details of function using the function name.
    func_details = symbol_table.check_in_fs(name)
    symtab_id = func_details[0]
    no_of_params = func_details[1]
    variables = symbol_table.allsymboltables[symtab_id].variables
    no_of_vars = len(variables)
    i=0
    space_for_variables = 0
    for x in variables:
        if i== (no_of_vars - no_of_params):
            space_for_variables = variables[x]['offset']
            break
        i+=1
    # Allocate space for local variables
    code.append('sub rsp, byte '+str(space_for_variables))


def assembly():
    code.append('global main')
    code.append('section .text')
    for y in instr:
        if(isinstance(y, tuple)):
            x = y[1]
        else : 
            x = y
        if x=='printcall':
            print_call()
        elif x.find(':')!=-1:
            # A function declaration
            func_begin(x)
        elif x[:5]=='param':
            # param being declared
            param(x[6:])
        elif x[:4]=='call':
            call_begin(x[5:])
        elif x[:6]=='return':
            returnn(x[7:])

    f = open("./src/assembly.asm", "w")
    for x in code:
        f.write(x)
        f.write('\n')
    f.close()

# New code
class AsmCode:
    def __init__(self):
        """Init AsmCode"""
        self.lines = []
        self.comm = []
        self.globals = []
        self.data = []
        self.string_literals = []
    
    def add(self, cmd):
        """Add a command to the code."""
        self.lines.append(cmd)
    
    def add_global(self, name):
        """Add a name to the code as global.

        name (str) - The name to add.

        """
        self.globals.append(f"\t.global {name}")
    
    def add_data(self, name, size, init):
        """Add static data to the code.

        init - the value to initialize `name` to
        """
        self.data.append(f"{name}:")
        size_strs = {1: "byte",
                     2: "word",
                     4: "int",
                     8: "quad"}

        if init:
            self.data.append(f"\t.{size_strs[size]} {init}")
        else:
            self.data.append(f"\t.zero {size}")

    def add_comm(self, name, size, local=None):
        """Add a common symbol to the code."""
        if local:
            self.comm.append(f"\t.local {name}")
        self.comm.append(f"\t.comm {name} {size}")

    def add_string_literal(self, name, chars):
        """Add a string literal to the ASM code."""
        self.string_literals.append(f"{name}:")
        data = ",".join(str(char) for char in chars)
        self.string_literals.append(f"\t.byte {data}")

    def full_code(self): 
        """Produce the full assembly code.

        return (str) - The assembly code, ready for saving to disk and
        assembling.

        """
        header = ["\t.intel_syntax noprefix"]
        header += self.comm
        if self.string_literals or self.data:
            header += ["\t.section .data"]
            header += self.data
            header += self.string_literals
            header += [""]

        header += ["\t.section .text"] + self.globals
        header += [str(line) for line in self.lines]

        return "\n".join(header + ["\t.att_syntax noprefix", ""])
    

import symbol_table as st

# based on the size of the arg, suitable reg will be allocated
reg_map = {
            "rax": 	["rax", "eax", "ax", "al"],
            "rbx": 	["rbx", "ebx", "bx", "bl"],
            "rcx": 	["rcx", "ecx", "cx", "cl"],
            "rdx": 	["rdx", "edx", "dx", "dl"],
            "rsi": 	["rsi", "esi", "si", "sil"],
            "rdi": 	["rdi", "edi", "di", "dil"],
            "r8": 	["r8", "r8d", "r8w", "r8b"],
            "r9": 	["r9", "r9d", "r9w", "r9b"],
            "r10": 	["r10", "r10d", "r10w", "r10b"],
            "r11": 	["r11", "r11d", "r11w", "r11b"],
            "rbp": 	["rbp", "", "", ""],
            "rsp": 	["rsp", "", "", ""]
        }
# to keep the track of the regs, if None then reg is free and can
# be allocated. Otherwise, free the reg to the memspot on the stack
reg_track = {}
for reg_list in reg_map.values():
    for reg in reg_list:
        if reg != "": reg_track[reg] = None


def assemble(code_3ac):
    print(code_3ac)
    asm = AsmCode()
    
    # add initialized globals
    init_globals = []
    for sym in code_3ac["@global"]:
        gvar = sym[1].split()[0]
        gval = sym[1].split()[-1]
        gsize = st.allsymboltables[0].variables[gvar]["size"]
        gtype = st.allsymboltables[0].variables[gvar]["type"]
        if gtype == 'CHAR':
            gval = ord(gval[1])

        asm.add_global(gvar)
        asm.add_data(gvar, gsize, gval)
        init_globals.append(gvar)

    # add uninit globals
    for gvar in st.allsymboltables[0].variables.keys():
        if gvar not in init_globals:
            asm.add_comm(gvar, st.allsymboltables[0].variables[gvar]["size"])

    strlit_cnt = 0
    strlit_map = {}
    # fill in string literals
    for strlit in st.list_of_strings:
        strlit_cnt += 1
        strlit_map[strlit] = "@strlit__" + str(strlit_cnt)
        strlit_ascii = list(strlit.encode('ascii'))
        asm.add_string_literal(strlit_map[strlit], strlit_ascii)
       

    # process the code_3ac lines
        # register allocation
        # operations -- create functions corresponding to use cases
    
    # print to asm file
    asm_lines = asm.full_code()
    with open("src/assembly.s", "w") as asm_file:
        for line in asm_lines:
            asm_file.write(line)
    
    

    
    
