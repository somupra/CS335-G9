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
import codegen.asm_cmds as asm_cmds
from codegen.regs import mov_reg_to_var_location, move_reg_to_memory, reg_map, get_empty_reg, get_reg_for, move_from_mem_to_reg, move_val_to_reg, assign_reg_to_var, reg_spill, mov_const_to_memory, mov_reg_to_var_location
# to keep the track of the regs, if None then reg is free and can
# be allocated. Otherwise, free the reg to the memspot on the stack
reg_track = {}
for reg_list in reg_map.values():
    for reg in reg_list:
        if reg != "": reg_track[reg] = None

def process(lines, var_info, asm, strlit_map, labels):
    ops = ['return', 'param', 'if', 'call', 'goto']
    param_num = 0
    for line in lines:
        lno = line[0]
        # this is a labeled line someone might goto here
        if str(lno) in labels.keys(): asm.add(asm_cmds.Label(labels[str(lno)]))

        cmd_toks = line[1].split()

        # expressions
        if cmd_toks[0] not in ops:
            if len(cmd_toks) == 3 and cmd_toks[1] == '=': # assignment
                asm.add(asm_cmds.Comment("Assignment Code"))
                lval = cmd_toks[0]
                rval = cmd_toks[2]
                if rval not in var_info.keys():
                    mov_const_to_memory(rval, lval, var_info, asm)
                    continue
                
                asm.add(asm_cmds.Comment(f"Getting reg for rval {rval}"))
                rreg = get_reg_for(rval, var_info, asm, reg_track, pref="ecx")
                asm.add(asm_cmds.Comment(f"mov from reg to mem {lval}"))
                mov_reg_to_var_location(rreg, lval, var_info, asm)
            
            if len(cmd_toks) == 5 and cmd_toks[1] == '=': # binary operation
                asm.add(asm_cmds.Comment("Binary Operation Code"))
                op1 = cmd_toks[2]
                op2 = cmd_toks[4]
                
                # check divison first
                if cmd_toks[3] == "/": # divison
                    asm.add(asm_cmds.Comment("Divison Code"))
                    
                    asm.add(asm_cmds.Comment("Fetch and spill rax"))
                    for reg in reg_map["rax"]:
                        if reg_track[reg]:
                            move_from_mem_to_reg(reg, reg_track[reg], var_info, asm, reg_track)
                            reg_spill(reg, var_info, asm, reg_track)

                    asm.add(asm_cmds.Comment("Fetch and spill rdx"))
                    for reg in reg_map["rdx"]:
                        if reg_track[reg]:
                            move_from_mem_to_reg(reg, reg_track[reg], var_info, asm, reg_track)
                            reg_spill(reg, var_info, asm, reg_track)

                    asm.add(asm_cmds.Comment(f"allocate eax to op1: {op1}"))
                    op1_reg = get_empty_reg(op1, var_info, asm, "eax", reg_track)
                    move_from_mem_to_reg(op1_reg, op1, var_info, asm, reg_track)

                    asm.add(asm_cmds.Comment(f"allocate reg to op1: {op2}"))
                    op2_reg = get_empty_reg(op2, var_info, asm, "ebx", reg_track)
                    move_from_mem_to_reg(op2_reg, op2, var_info, asm, reg_track)
                    
                    asm.add(asm_cmds.Comment(f"CDQ then iDiv"))
                    asm.add(asm_cmds.Cdq(None, None, None))
                    asm.add(asm_cmds.Idiv(op2_reg, None, None))

                    mov_reg_to_var_location("eax", cmd_toks[0], var_info, asm)
                    continue

                if cmd_toks[0] == op1:
                    op1_reg = get_reg_for(op1, var_info, asm, reg_track, pref="edx")
                    
                else:
                    # create a temp reg we will always take edx and mov op1 to it
                    op1_reg = get_empty_reg(cmd_toks[0], var_info, asm, "edx", reg_track)
                    move_from_mem_to_reg(op1_reg, op1, var_info, asm, reg_track)

                # get reg for op2 and move op2 to it
                op2_reg = get_empty_reg(op2, var_info, asm, "esi", reg_track)
                move_from_mem_to_reg(op2_reg, op2, var_info, asm, reg_track)

                if cmd_toks[3] == "+": # addition
                    asm.add(asm_cmds.Comment("Addition Code"))
                    asm.add(asm_cmds.Add(op1_reg, op2_reg, 8))
                
                if cmd_toks[3] == "-": # subtraction
                    asm.add(asm_cmds.Comment("Subtraction Code"))
                    asm.add(asm_cmds.Sub(op1_reg, op2_reg, 8))
                
                if cmd_toks[3] == "*": # multiplication
                    asm.add(asm_cmds.Comment("Multiplication Code"))
                    asm.add(asm_cmds.Imul(op1_reg, op2_reg, 8))
                
                # move op1_reg to memory now
                move_reg_to_memory(op1_reg, var_info, asm, reg_track)
                       
        if cmd_toks[0] == 'return':
            ret_val = cmd_toks[1]
            asm.add(asm_cmds.Comment(f"RETURN {ret_val}"))

            # before spilling read from memory, then spill, this prevents a dirty spill
            if reg_track["eax"]:
                move_from_mem_to_reg("eax", reg_track["eax"], var_info, asm, reg_track)
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
                    asm.add(asm_cmds.Comment("Address of var to arg register"))
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
                    move_from_mem_to_reg(arg_reg, param_val, var_info, asm, reg_track)
                    # move_val_to_reg(arg_reg, param_val, var_info, asm, reg_track)

        if cmd_toks[0] == "call":
            param_num = 0 # reset param_num variable

            fname = cmd_toks[1][: -1]
            asm.add(asm_cmds.Comment(f"Function call for: {fname}"))

            for reg in reg_map["rax"]:
                if reg_track[reg]:
                    move_from_mem_to_reg(reg, reg_track[reg], var_info, asm, reg_track)
                    reg_spill(reg, var_info, asm, reg_track)

            asm.add(asm_cmds.Lea("rax", f"[{fname}]"))
            asm.add(asm_cmds.Call("rax", None, 8))
            print("after calling printf reg state: ", reg_track["eax"])
            for reg, v in reg_track.items():
                if v == "b":
                    print("b is here: ", reg)

        if cmd_toks[0] == "if":
            asm.add(asm_cmds.Comment("Comparison"))
            cond = line[1][4: line[1].find("}")]
            goto = line[1][line[1].rfind("{") + 1 : -1]

            # step 2: cmp cond, cond will always have two operands
            # cmp will always happen between esi and edi regs
            reg_spill("esi", var_info, asm, reg_track)
            reg_spill("edi", var_info, asm, reg_track)

            op1, comp, op2 = cond.split()[0], cond.split()[1], cond.split()[2]
            
            # in a loop, someone else might have clobbered the regs, so read directly from the memory
            op1_reg = move_from_mem_to_reg("esi", op1, var_info, asm, reg_track)
            op2_reg = move_from_mem_to_reg("edi", op2, var_info, asm, reg_track)

            asm.add(asm_cmds.Cmp("esi", "edi", 8))
            if comp == ">": asm.add(asm_cmds.Jg(labels[goto]))
            if comp == ">=": asm.add(asm_cmds.Jge(labels[goto]))
            if comp == "<": asm.add(asm_cmds.Jl(labels[goto]))
            if comp == "<=": asm.add(asm_cmds.Jle(labels[goto]))
            if comp == "==": asm.add(asm_cmds.Je(labels[goto]))
            if comp == "!=": asm.add(asm_cmds.Jne(labels[goto]))

        if cmd_toks[0] == "goto":
            goto = cmd_toks[1][1:-1]
            asm.add(asm_cmds.Comment("Jump to label"))
            asm.add(asm_cmds.Jmp(labels[goto]))


def assemble(code_3ac):
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

    # get all the labels (among all the functions)
    labels = {}
    for fn_code in code_3ac.values():
        for cmd in fn_code:
            cmd_toks = cmd[1].split()
            if cmd_toks[0] == 'goto':
                goto = cmd_toks[1][1:-1]
                labels[goto] = "__label__" + str(goto)
                continue
            if cmd_toks[0] == 'if':
                goto = cmd[1][cmd[1].rfind("{") + 1 : -1]
                labels[goto] = "__label__" + str(goto)

       

    # process the code_3ac lines
    for fname in code_3ac.keys():
        if fname == "@global": continue

        asm.add(asm_cmds.Label(fname))
        asm.add(asm_cmds.Push("rbp", None, 8)) # push rbp
        asm.add(asm_cmds.Mov("rbp", "rsp", 8)) # mov rbp, rsp
        
        # sub rsp, max_offset
        # to find max_offset add up all the offsets
        max_offset = st.get_max_fn_offset(fname)
        print(max_offset)
        asm.add(asm_cmds.Sub("rsp", max_offset, 8))

        # get variable info
        var_info = st.get_var_info(fname)

        # process lines
        process(code_3ac[fname], var_info, asm, strlit_map, labels)


        # register allocation
        # operations -- create functions corresponding to use cases
    
    return asm
    
    

    
    
