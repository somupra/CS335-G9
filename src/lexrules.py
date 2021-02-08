reserved = {
    'if': 'IF',
    'auto': 'AUTO',
    'break': 'BREAK',
    'case': 'CASE',
    'const': 'CONST',
    'continue': 'CONTINUE',
    'default': 'DEFAULT',
    'do': 'DO',
    'double': 'DOUBLE',
    'else': 'ELSE',
    'enum': 'ENUM',
    'extern': 'EXTERN',
    'float': 'FLOAT',
    'for': 'FOR',
    'goto': 'GOTO',
    'int': 'INT',
    'long': 'LONG',
    'register': 'REGISTER',
    'return': 'RETURN',
    'short': 'SHORT',
    'signed': 'SIGNED',
    'sizeof': 'SIZEOF',
    'static': 'STATIC',
    'struct': 'STRUCT',
    'switch': 'SWITCH',
    'typedef': 'TYPEDEF',
    'union': 'UNION',
    'unsigned': 'UNSIGNED',
    'void': 'VOID',
    'volatile': 'VOLATILE',
    'while': 'WHILE',
    'main': 'MAIN',
    'include': 'INCLUDE',
    'char': 'CHAR'
}

tokens = ['NUMBER', 'STRING', 'CHAR_CONST',
          'ADD', 'SUBTRACT', 'MULTIPLY', 'DIVIDE', 'EQUAL', 'ASSIGN', 'EXPONENT', 'MOD', 'XOR',
          'LSASSIGN', 'RSASSIGN', 'MULASSIGN', 'DIVASSIGN', 'PLUSASSIGN', 'MINUSASSIGN',
          'MODASSIGN', 'XORASSIGN', 'ORASSIGN', 'ANDASSIGN', 'ELLIPSIS', 'LSHIFT', 'RSHIFT',
          'INCREMENT', 'DECREMENT',
          'AND', 'OR', 'NOT', 'GT', 'LT', 'GEQ', 'LEQ', 'NEQ',
          'B_AND', 'B_OR', 'B_NOT', 'B_XOR',
          'DOT', 'COMMA', 'ARROW', 'COLON', 'SEMICOLON', 'TERNARYOP',
          'OP', 'CP', 'OCP', 'CCP', 'OSP', 'CSP',
          'NEWLINE', 'COMMENT','ID'] + list(reserved.values())

t_ignore = ' \t\x0c'

#mathematical operations
t_EQUAL = r'\=\='
t_ASSIGN = r'\='
t_ADD = r'\+'
t_SUBTRACT = r'\-'
t_MULTIPLY = r'\*'
t_DIVIDE = r'\/'
t_MOD = r'\%'
t_LSHIFT = r'\<\<'
t_RSHIFT = r'\>\>'
t_PLUSASSIGN = r'\+\='
t_MINUSASSIGN = r'\-\='
t_MULASSIGN = r'\*\='
t_DIVASSIGN = r'\/\='
t_MODASSIGN = r'\%\='
t_ANDASSIGN = r'\&\='
t_ORASSIGN = r'\|\='
t_XORASSIGN = r'\^\='
t_LSASSIGN = r'\<\<\='
t_RSASSIGN = r'\>\>\='
t_INCREMENT = r'\+\+'
t_DECREMENT = r'\-\-'
t_GT = r'\>'
t_LT = r'\<'
t_GEQ = r'\>\='
t_LEQ = r'\<\='
t_NEQ = r'\!\='

#logical operations
t_AND = r'\&\&'
t_OR = r'\|\|'
t_NOT = r'\!'

#Bitwise operators
t_B_AND = r'\&'
t_B_OR = r'\|'
t_B_NOT = r'\~'
t_XOR = r'\^'

t_DOT = r'\.'
t_COMMA = r'\,'
t_COLON = r'\:'
t_SEMICOLON = r'\;'
t_TERNARYOP = r'\?'
t_ELLIPSIS = r'\.\.\.'
t_ARROW = r'\-\>'

#parenthesis
t_OP = r'\('
t_CP = r'\)'
t_OCP = r'\{'
t_CCP = r'\}'
t_OSP = r'\['
t_CSP = r'\]'

def t_CHAR_CONST(t) :
    r'[UuL]?\'([^\\\n]|(\\(.|\n)))*?\''
    return t

def t_STRING(t) :
    r'[UuL]?\"([^\\\n]|(\\(.|\n)))*?\"'
    return t

digit               = r'([0-9])'
nondigit            = r'([_A-Za-z])'
identifier          = r'(' + nondigit + r'(' + digit + r'|' + nondigit + r')*)' 

from ply.lex import TOKEN

@TOKEN(identifier)
def t_ID(t):
    t.type = reserved.get(t.value, "ID")
    return t

def t_NEWLINE(t) :
	r'\n'
	t.lexer.lineno += 1

def t_COMMENT(t) :
	r"\/\/.*|\/\*(.|\n)*\*\/"
	t.lexer.lineno += t.value.count('\n')


hex         = r'[a-fA-F0-9]'
exp         = r'[Ee][+-]?' + digit + r'+'
fs          = r'(f|F|l|L)'
ls          = r'(u|U|l|L)*'

number  =   r'(0[xX](' + hex + r')+\.p[+-]?(' + digit + r')+([LlfF])?)'                +\
            r'|(0[xX](' + hex + r')+(' + ls + r')?)'                                   +\
            r'|(' + digit + r'*\.(' + digit + r')*((' + exp + r')?' + fs + r'?))'      +\
            r'|(' + digit + r'+(' + exp + r')(' + fs + r')?)'                          +\
            r'|((0)*(' + digit + r')+(' + ls + r')?)'                                  +\
            r'|((' + digit + r')+(' + ls + r')?)'                                      +\
            r'|' + digit


@TOKEN(number)
def t_NUMBER(t) :
    return t

def t_error(t) :
    print('ERROR at (val, line, position from start) :: {} {} {}'.format(t.value[0], t.lineno, t.lexpos))
    t.lexer.skip(1)
