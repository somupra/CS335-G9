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
from codegen.regs import reg_map, get_empty_reg, get_reg_for, move_from_mem_to_reg, move_val_to_reg, assign_reg_to_var, reg_spill

# to keep the track of the regs, if None then reg is free and can
# be allocated. Otherwise, free the reg to the memspot on the stack
reg_track = {}
for reg_list in reg_map.values():
    for reg in reg_list:
        if reg != "": reg_track[reg] = None

def process(lines, var_info, asm, strlit_map):
    ops = ['return', 'param', 'if']
    param_num = 0
    for line in lines:
        lno = line[0]
        cmd_toks = line[1].split()

        # expressions
        if cmd_toks[0] not in ops:
            if len(cmd_toks) == 3 and cmd_toks[1] == '=': # assignment
                asm.add(asm_cmds.Comment("Assignment Code"))
                lval = cmd_toks[0]
                rval = cmd_toks[2]
                lreg = get_reg_for(lval, var_info, asm, reg_track)
                move_val_to_reg(lreg, rval, var_info, asm, reg_track)
                # import pprint
                # pp = pprint.PrettyPrinter(indent=4)
                # pp.pprint(reg_track)
            
            if len(cmd_toks) == 5 and cmd_toks[1] == '=': # binary operation
                asm.add(asm_cmds.Comment("Binary Operation Code"))
                op1 = cmd_toks[2]
                op2 = cmd_toks[4]

                # create a temp reg we will always take edx and mov op1 to it
                op1_reg = get_empty_reg(cmd_toks[0], var_info, asm, "edx", reg_track)
                move_val_to_reg(op1_reg, op1, var_info, asm, reg_track)

                # get reg for op2 and move op2 to it
                op2_reg = get_empty_reg(op2, var_info, asm, "esi", reg_track)

                move_val_to_reg(op2_reg, op2, var_info, asm, reg_track)

                if cmd_toks[3] == "+": # addition
                    asm.add(asm_cmds.Comment("Addition Code"))
                    asm.add(asm_cmds.Add(op1_reg, op2_reg, 8))
                
                if cmd_toks[3] == "-": # subtraction
                    asm.add(asm_cmds.Comment("Subtraction Code"))
                    asm.add(asm_cmds.Sub(op1_reg, op2_reg, 8))
        
        if cmd_toks[0] == 'return':
            ret_val = cmd_toks[1]
            asm.add(asm_cmds.Comment(f"RETURN {ret_val}"))
            reg_spill("eax", var_info, asm, reg_track)
            move_val_to_reg("eax", ret_val, var_info, asm, reg_track)
            asm.add(asm_cmds.Mov("rsp", "rbp", 8)) # mov rsp, rbp
            asm.add(asm_cmds.Pop("rbp", None, 8)) # pop rbp
            asm.add(asm_cmds.Ret(None, None, None))

        if cmd_toks[0] == 'param':
            param_num += 1
            # check if param to std function
            i = lno
            while lines[i][1].split()[0] != "call":
                i += 1
            
            reg_pref = ["rdi", "rsi", "rdx", "rcx", "r8", "r9"]
            callee = lines[i][1].split()[1]

            if callee not in st.allsymboltables[0].functions.keys():
                arg_reg = reg_pref[param_num - 1]
                param_val = line[1][6: line[1].rfind(",")]
                if param_val[0] == '\"': param_val = param_val[1:-1]

                if param_val in strlit_map.keys():
                    # empty the arg register
                    reg_spill(arg_reg, var_info, asm, reg_track)
                    asm.add(asm_cmds.Comment("Address of symbol to arg register"))
                    asm.add(asm_cmds.Lea(arg_reg, f'[{strlit_map[param_val]}]'))
                else:
                    scope = line[1][line[1].rfind("e")+1 : ]
                    # empty the arg register
                    asm.add(asm_cmds.Comment("Copy argument to arg register"))
                    size_map = {
                        1: 3,
                        2: 2,
                        4: 1,
                        8: 0
                    }
                    param_size = var_info[param_val]["size"]
                    arg_reg = reg_map[arg_reg][size_map[param_size]]
                    reg_spill(arg_reg, var_info, asm, reg_track)
                    move_val_to_reg(arg_reg, param_val, var_info, asm, reg_track)

        if cmd_toks[0] == "call":
            fname = cmd_toks[1][: -1]
            asm.add(asm_cmds.Comment(f"Function call for: {fname}"))
            reg_spill("rax", var_info, asm, reg_track)
            asm.add(asm_cmds.Lea("rax", f"[{fname}]"))
            asm.add(asm_cmds.Call("rax", None, 8))

                    



            

            
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

        if strlit_ascii[-1] == 110 and strlit_ascii[-2] == 92:
            strlit_ascii = strlit_ascii[ : -2]
            strlit_ascii.append(10)
        strlit_ascii.append(0)

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
        process(code_3ac[fname], var_info, asm, strlit_map)


        # register allocation
        # operations -- create functions corresponding to use cases
    
    return asm
    
    

    
    
