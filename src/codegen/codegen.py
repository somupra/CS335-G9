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
        code.append('push [ebp-'+str(8+offset)+']')


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
        elif x[:8]=='call':
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
                     8: "int",
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
import codegen.asm_cmds as asm_cmds

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
            "rbp": 	["rbp", "ebp", "", ""],
            "rsp": 	["rsp", "esp", "", ""]
        }
# to keep the track of the regs, if None then reg is free and can
# be allocated. Otherwise, free the reg to the memspot on the stack
reg_track = {}
for reg_list in reg_map.values():
    for reg in reg_list:
        if reg != "": reg_track[reg] = None

def reg_spill(rname, var_info, asm):
    rval = reg_track[rname]
    rval_offset = var_info[rval]["offset"] + var_info[rval]["size"]
    asm.add(asm_cmds.Mov(f"[ebp - {rval_offset}]", rname, 8))

def move_from_mem_to_reg(reg, var, var_info, asm):
    var_offset = var_info[var]["offset"] + var_info[var]["size"]
    asm.add(asm_cmds.Mov(reg, f"[ebp - {var_offset}]", 8))

def get_reg_for(val, var_info, asm):
    # if val is constant, return it
    if val not in var_info.keys(): return val

    global reg_track
    # check if a live register is there
    for k, v in reg_track.items():
        if v == val: return k 
    
    # no live reg for val, assign new reg if empty
    priority = ["eax", "ebx", "ecx", "edx", "esi", "edi"]
    for reg in priority:
        if not reg_track[reg]:
            reg_track[reg] = val
            return reg
    
    # all regs are filled, spill a reg and allocate it to val
    # we will spill eax always
    reg_spill("eax", var_info, asm)

    # allocate eax to val
    move_from_mem_to_reg("eax", val, var_info, asm)
    return "eax"

def get_empty_reg(var_info, asm, rname):
    global reg_track
    if reg_track[rname]: # spill it
        reg_spill(rname, var_info, asm)
    reg_track[rname] = "@op_temp"
    return rname

def move_val_to_reg(dreg, var, var_info, asm):
    # if val is const then mov
    if var not in var_info.keys(): 
        asm.add(asm_cmds.Mov(dreg, var, 8))
        return 

    # check if var has live reg, if yes then mov
    global reg_track
    for sreg, v in reg_track.items():
        if v == var: 
            asm.add(asm_cmds.Mov(dreg, sreg, 8))
            return 
    
    # if no live reg, move from memory
    move_from_mem_to_reg(dreg, var, var_info, asm)
    reg_track[dreg] = var
     
def assign_reg_to_var(sreg, var, var_info, asm):
    # check if var has live reg, if yes then mov
    global reg_track
    for dreg, v in reg_track.items():
        if v == var: 
            asm.add(asm_cmds.Mov(dreg, sreg, 8))
            return 
    
    # if no live reg, move to memory
    var_offset = var_info[var]["offset"] + var_info[var]["size"]
    asm.add(asm_cmds.Mov(f"[ebp - {var_offset}]", sreg, 8))

def process(lines, var_info, asm):
    ops = ['return', 'param', 'if']
    for line in lines:
        lno = line[0]
        cmd_toks = line[1].split()

        # expressions
        if cmd_toks[0] not in ops:
            if len(cmd_toks) == 3 and cmd_toks[1] == '=': # assignment
                lval = cmd_toks[0]
                rval = cmd_toks[2]
                lreg = get_reg_for(lval, var_info, asm)
                move_val_to_reg(lreg, rval, var_info, asm)
            
            if len(cmd_toks) == 5 and cmd_toks[1] == '=': # binary operation
                op1 = cmd_toks[2]
                op2 = cmd_toks[4]

                # create a temp reg we will always take edx and mov op1 to it
                op1_reg = get_empty_reg(var_info, asm, "edx")
                move_val_to_reg(op1_reg, op1, var_info, asm)

                # get reg for op2 and move op2 to it
                op2_reg = get_empty_reg(var_info, asm, "esi")
                move_val_to_reg(op2_reg, op2, var_info, asm)

                if cmd_toks[3] == "+": # addition
                    asm.add(asm_cmds.Add(op1_reg, op2_reg, 8))
                
                assign_reg_to_var(op1_reg, cmd_toks[0], var_info, asm)

            
def assemble(code_3ac):
    print("\n", code_3ac)
    asm = AsmCode()
    
    # add global functions
    for fname in code_3ac.keys():
        if fname != "@global": asm.add_global(fname)

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
        strlit_map[strlit] = "__strlit__" + str(strlit_cnt)
        strlit_ascii = list(strlit.encode('ascii'))
        asm.add_string_literal(strlit_map[strlit], strlit_ascii)
       

    # process the code_3ac lines
    for fname in code_3ac.keys():
        if fname == "@global": continue

        asm.add(asm_cmds.Label(fname))
        asm.add(asm_cmds.Push("rbp", None, 8)) # push rbp
        asm.add(asm_cmds.Mov("rbp", "rsp", 8)) # mov rbp, rsp
        
        # sub rsp, max_offset
        # to find max_offset add up all the offsets
        max_offset = st.get_max_fn_offset(fname)
        asm.add(asm_cmds.Sub("rsp", max_offset, 8))

        # get variable info
        var_info = st.get_var_info(fname)

        # process lines
        process(code_3ac[fname], var_info, asm)


        # register allocation
        # operations -- create functions corresponding to use cases
    
    return asm
    
    

    
    
