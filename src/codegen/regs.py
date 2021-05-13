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
        
size_map = {
    1: "BYTE PTR ",
    2: "WORD PTR ",
    4: "DWORD PTR ",
    8: "QWORD PTR "
}

def move_reg_to_memory(rname, var_info, asm, reg_track):
    rval = reg_track[rname]
    rsize = var_info[rval]["size"]
    rval_offset = var_info[rval]["offset"] + rsize
    asm.add(asm_cmds.Comment(f"Move reg data to mem: {rname} -> mem {rval}"))
    asm.add(asm_cmds.Mov(f"{size_map[rsize]}[rbp - {rval_offset}]", rname, 8))

def reg_spill(rname, var_info, asm, reg_track):
    # if reg is already empty then do nothing
    if reg_track[rname] == None: return

    rval = reg_track[rname]
    if rval not in var_info.keys(): 
        reg_track[rname] = None
        return

    rsize = var_info[rval]["size"]
    rval_offset = var_info[rval]["offset"] + rsize

    asm.add(asm_cmds.Comment("Register spill"))
    asm.add(asm_cmds.Mov(f"{size_map[rsize]}[rbp - {rval_offset}]", rname, 8))
    
    # set the reg_track to None
    reg_track[rname] = None

def move_from_mem_to_reg(reg, var, var_info, asm, reg_track):
    asm.add(asm_cmds.Comment(f"Load reg from mem {var}"))
    if var not in var_info.keys(): 
        asm.add(asm_cmds.Mov(reg, var, 8))
        return
    var_size = var_info[var]["size"]
    var_offset = var_info[var]["offset"] + var_size
    asm.add(asm_cmds.Mov(reg, f"{size_map[var_size]}[rbp - {var_offset}]", 8))

def get_reg_for(val, var_info, asm, reg_track, pref):
    # if val is constant, return it
    if val not in var_info.keys(): return val

    # check if a live register is there
    for reg, v in reg_track.items():
        if v == val: 
            move_from_mem_to_reg(reg, val, var_info, asm, reg_track)
            return reg
    
    # no live reg for val, assign new reg if empty
    priority = ["eax", "ebx", "ecx", "edx", "esi", "edi"]
    for reg in priority:
        if reg_track[reg] == None:
            reg_track[reg] = val
            move_from_mem_to_reg(reg, val, var_info, asm, reg_track)
            return reg
    
    # all regs are filled, spill a reg and allocate it to val
    # we will spill acc to pref
    reg = get_empty_reg(val, var_info, asm, pref, reg_track)
    move_from_mem_to_reg(pref, val, var_info, asm, reg_track)
    return pref

def get_empty_reg(var, var_info, asm, rname, reg_track):
    if reg_track[rname] == var: return rname
    reg_spill(rname, var_info, asm, reg_track)
    reg_track[rname] = var
    return rname

def move_val_to_reg(dreg, var, var_info, asm, reg_track):
    # if val is const then mov
    if var not in var_info.keys(): 
        asm.add(asm_cmds.Comment(f"Move const value to reg: {var}"))
        asm.add(asm_cmds.Mov(dreg, var, 8))
        return 

    # check if var has live reg, if yes then mov
    for sreg, v in reg_track.items():
        if v == var: 
            asm.add(asm_cmds.Mov(dreg, sreg, 8))
            return 
    
    # if no live reg, move from memory
    move_from_mem_to_reg(dreg, var, var_info, asm, reg_track)
     
def assign_reg_to_var(sreg, var, var_info, asm, reg_track):
    # check if var has live reg, if yes then mov
    for dreg, v in reg_track.items():
        if v == var: 
            asm.add(asm_cmds.Comment(f"Assign reg to variable in reg: {var}"))
            asm.add(asm_cmds.Mov(dreg, sreg, 8))
            return 
    
    # if no live reg, move to memory
    var_size = var_info[var]["size"]
    var_offset = var_info[var]["offset"] + var_size
    asm.add(asm_cmds.Comment(f"Assign reg to variable: {var}"))
    asm.add(asm_cmds.Mov(f"{size_map[var_size]}[rbp - {var_offset}]", sreg, 8))

def mov_reg_to_var_location(sreg, var, var_info, asm):
    var_size = var_info[var]["size"]
    var_offset = var_info[var]["offset"] + var_size
    asm.add(asm_cmds.Comment(f"Assign reg to variable: {var}"))
    asm.add(asm_cmds.Mov(f"{size_map[var_size]}[rbp - {var_offset}]", sreg, 8))

def mov_const_to_memory(const, var, var_info, asm):
    var_size = var_info[var]["size"]
    var_offset = var_info[var]["offset"] + var_size
    asm.add(asm_cmds.Mov(f"{size_map[var_size]}[rbp - {var_offset}]", const, 8))
