"""
This module defines and implements classes representing assembly commands.

The _ASMCommand object is the base class for most ASM commands. Some commands
inherit from _ASMCommandMultiSize or _JumpCommand instead.

"""


class _ASMCommand:
    """
    Base class for a standard ASMCommand, like `add` or `imul`.

    This class is used for ASM commands which take arguments of the same
    size.
    """
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

    name = None
    dest = None 
    source = None 
    size = None 

    def __init__(self, dest=None, source=None, size=None):
        size_map = {
            1: 3,
            2: 2,
            4: 1,
            8: 0
        }
        if dest and dest not in self.reg_map.keys(): self.dest = str(dest)
        elif dest: self.dest = self.reg_map[dest][size_map[size]]
        if source and source not in self.reg_map.keys(): self.source = str(source)
        elif source: self.source = self.reg_map[source][size_map[size]]
        self.size = size

    def __str__(self):
        s = "\t" + self.name
        if self.dest:
            s += " " + self.dest
        if self.source:
            s += ", " + self.source
        return s


class _ASMCommandMultiSize:
    """
    Base class for an ASMCommand which takes arguments of different sizes.

    For example, `movsx` and `movzx`.
    """

    name = None

    def __init__(self, dest, source, source_size, dest_size):
        self.dest = dest.asm_str(source_size)
        self.source = source.asm_str(dest_size)
        self.source_size = source_size
        self.dest_size = dest_size

    def __str__(self):
        s = "\t" + self.name
        if self.dest:
            s += " " + self.dest
        if self.source:
            s += ", " + self.source
        return s


class _JumpCommand:
    """Base class for jump commands."""

    name = None

    def __init__(self, target):
        self.target = target

    def __str__(self):
        s = "\t" + self.name + " " + self.target
        return s


class Comment:
    """Class for comments."""

    def __init__(self, msg):  
        self.msg = msg

    def __str__(self):  
        return "\t// " + self.msg


class Label:
    """Class for label."""

    def __init__(self, label):  
        self.label = label

    def __str__(self):  
        return self.label + ":"


class Lea:
    """Class for lea command."""

    name = "lea"

    def __init__(self, dest, source):  
        self.dest = dest
        self.source = source

    def __str__(self):  
        return ("\t" + self.name + " " + self.dest.asm_str(8) + ", "
                "" + self.source.asm_str(0))


class Je(_JumpCommand): name = "je"  


class Jne(_JumpCommand): name = "jne"  


class Jg(_JumpCommand): name = "jg"  


class Jge(_JumpCommand): name = "jge"  


class Jl(_JumpCommand): name = "jl"  


class Jle(_JumpCommand): name = "jle"  


class Ja(_JumpCommand): name = "ja"  


class Jae(_JumpCommand): name = "jae"  


class Jb(_JumpCommand): name = "jb"  


class Jbe(_JumpCommand): name = "jbe"  


class Jmp(_JumpCommand): name = "jmp"  


class Movsx(_ASMCommandMultiSize): name = "movsx"  


class Movzx(_ASMCommandMultiSize): name = "movzx"  


class Mov(_ASMCommand): name = "mov"  


class Add(_ASMCommand): name = "add"  


class Sub(_ASMCommand): name = "sub"  


class Neg(_ASMCommand): name = "neg"  


class Not(_ASMCommand): name = "not"  


class Div(_ASMCommand): name = "div"  


class Imul(_ASMCommand): name = "imul"  


class Idiv(_ASMCommand): name = "idiv"  


class Cdq(_ASMCommand): name = "cdq"  


class Cqo(_ASMCommand): name = "cqo"  


class Xor(_ASMCommand): name = "xor"  


class Cmp(_ASMCommand): name = "cmp"  


class Pop(_ASMCommand): name = "pop"  


class Push(_ASMCommand): name = "push"  


class Call(_ASMCommand): name = "call"  


class Ret(_ASMCommand): name = "ret"  


class Sar(_ASMCommandMultiSize): name = "sar"  


class Sal(_ASMCommandMultiSize): name = "sal"  
