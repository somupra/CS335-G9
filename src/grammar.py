import sys
import ply.yacc as yacc
from lexrules import tokens

class Node:
    def __init__(self, type, children=None, leaf=None):
        self.type = type
        if children:
            self.children = children
        else:
            self.children = [ ]
        self.leaf = leaf

start = 'translation_unit'

def p_primary_expression(p):
	'''
	primary_expression : ID
						| CHAR_CONST
						| NUMBER
						| OP expression CP
	'''
	if p[1]=='(':
	  p[0] = Node("primary_expression", [p[2]], None)
	else:
	  p[0] = Node("primary_expression", None, p[1])
	
def p_postfix_expression(p):
	'''
	postfix_expression : primary_expression
						| postfix_expression OSP expression CSP
						| postfix_expression OP CP
						| postfix_expression OP argument_expression_list CP
						| postfix_expression DOT ID
						| postfix_expression ARROW ID
						| postfix_expression INCREMENT
						| postfix_expression DECREMENT
	'''
	if p[2]=='[':
		p[0] = Node("postfix_expression", [p[1],p[3]], None)
	elif p[2]=='++':
		p[0] = Node("postfix_expression", [p[1]], p[2])
	elif p[2]=='--':
		p[0] = Node("postfix_expression", [p[1]], p[2])
	elif p[2]=='.':
		p[0] = Node("postfix_dot_exp", [p[1]], p[3])
	elif p[2]=='->':
		p[0] = Node("postfix_arrow_exp", [p[1]], p[3])
	elif p[3]==')':
		p[0] = Node("postfix_expression", [p[1]], None)
	elif p[2]=='(':
		p[0] = Node("postfix_expression", [p[1],p[3]], None)
	else:
		p[0] = Node("postfix_expression", [p[1]], None)

def p_argument_expression_list(p):
	'''
	argument_expression_list : assignment_expression
							| argument_expression_list COMMA assignment_expression
	'''
	if len(p)==1:
		p[0] = Node("argument_expression_list", [p[1]], None)
	else:
		p[0] = Node("primary_expression", [p[1],p[3]], p[2])

def p_unary_expression(p):
	'''
	unary_expression : postfix_expression
						| INCREMENT unary_expression
						| DECREMENT unary_expression
						| unary_operator cast_expression
						| SIZEOF unary_expression
						| SIZEOF OP type_name CP
	'''
	if len(p)==1:
		p[0] = Node("unary_expression", [p[1]], None)#1
	elif p[1]=='++':
		p[0] = Node("unary_expression", [p[2]], p[1])#2
	elif p[1]=='--':
		p[0] = Node("unary_expression", [p[2]], p[1])#3
	elif p[2]=='(':
		p[0] = Node("unary_expression", [p[3]], p[1])#6 #??
	elif p[1]=='sizeof':
		p[0] = Node("unary_expression", [p[2]], p[1])#5
	else:
		p[0] = Node("unary_expression", [p[1],p[2]], None)#4

def p_unary_operator(p):
	'''
	unary_operator : B_AND
				| MULTIPLY
					| ADD
					| SUBTRACT
					| B_NOT
					| NOT
	'''
	p[0] = Node("unary_operator", None, p[1])

def p_cast_expression(p):
	'''
	cast_expression : unary_expression
					| OP type_name CP cast_expression
	'''
	p[0] = Node("cast_expression", [p[-1]], None)

def p_multiplicative_expression(p):
	'''
	multiplicative_expression : cast_expression
							| multiplicative_expression MULTIPLY cast_expression
							| multiplicative_expression DIVIDE cast_expression
							| multiplicative_expression MOD cast_expression
	'''
	if len(p)==1:
		p[0] = Node("unary_expression", [p[1]], None)
	else:
		p[0] = Node("unary_expression", [p[1],p[3]], p[2])

def p_additive_expression(p):
	'''
	additive_expression : multiplicative_expression 
						| additive_expression ADD multiplicative_expression
						| additive_expression SUBTRACT multiplicative_expression
	'''
	if len(p)==1:
		p[0] = Node("additive_expression", [p[1]], None)
	else:
		p[0] = Node("additive_expression", [p[1],p[3]], p[2])

def p_shift_expression(p):
	'''
	shift_expression : additive_expression
					| shift_expression LSHIFT additive_expression
					| shift_expression RSHIFT additive_expression
	'''
	if len(p)==1:
		p[0] = Node("shift_expression", [p[1]], None)
	else:
		p[0] = Node("shift_expression", [p[1],p[3]], p[2])

def p_relational_expression(p):
	'''
	relational_expression : shift_expression
							| relational_expression LT shift_expression
							| relational_expression GT shift_expression
							| relational_expression LEQ shift_expression
							| relational_expression GEQ shift_expression
	'''
	if len(p)==1:
		p[0] = Node("relational_expression", [p[1]], None)
	else:
		p[0] = Node("relational_expression", [p[1],p[3]], p[2])

def p_equality_expression(p):
	'''
	equality_expression : relational_expression
						| equality_expression EQUAL relational_expression
						| equality_expression NEQ relational_expression
	'''
	if len(p)==1:
		p[0] = Node("equality_expression", [p[1]], None)
	else:
		p[0] = Node("equality_expression", [p[1],p[3]], p[2])

def p_and_expression(p):
	'''
	and_expression : equality_expression
					| and_expression B_AND equality_expression
	'''
	if len(p)==1:
		p[0] = Node("and_expression", [p[1]], None)
	else:
		p[0] = Node("and_expression", [p[1],p[3]], p[2])
	
def p_exclusive_or_expression(p):
	'''
	exclusive_or_expression : and_expression
							| exclusive_or_expression XOR and_expression
	'''
	if len(p)==1:
		p[0] = Node("exclusive_or_expression", [p[1]], None)
	else:
		p[0] = Node("exclusive_or_expression", [p[1],p[3]], p[2])

def p_inclusive_or_expression(p):
	'''
	inclusive_or_expression : exclusive_or_expression
							| inclusive_or_expression B_OR exclusive_or_expression
	'''
	if len(p)==1:
		p[0] = Node("inclusive_or_expression", [p[1]], None)
	else:
		p[0] = Node("inclusive_or_expression", [p[1],p[3]], p[2])

def p_logical_and_expression(p):
	'''
	logical_and_expression : inclusive_or_expression
						   | logical_and_expression AND inclusive_or_expression
	'''
	if len(p)==1:
		p[0] = Node("logical_and_expression", [p[1]], None)
	else:
		p[0] = Node("logical_and_expression", [p[1],p[3]], p[2])

def p_logical_or_expression(p):
	'''
	logical_or_expression : logical_and_expression
						  | logical_or_expression OR logical_and_expression
	'''
	if len(p)==1:
		p[0] = Node("logical_or_expression", [p[1]], None)
	else:
		p[0] = Node("logical_or_expression", [p[1],p[3]], p[2])

def p_conditional_expression(p):
	'''
	conditional_expression : logical_or_expression
						   | logical_or_expression TERNARYOP expression COLON conditional_expression
	'''
	if len(p)==1:
		p[0] = Node("conditional_expression", [p[1]], None)
	else:
		p[0] = Node("conditional_expression", [p[1],p[3],p[5]], None) #??

def p_assignment_expression(p):
	'''
	assignment_expression : conditional_expression
						  | unary_expression assignment_operator assignment_expression    
	'''
	if len(p)==1:
		p[0] = Node("assignment_expression", [p[1]], None)
	else:
		p[0] = Node("assignment_expression", [p[1],p[2],p[3]], None)

def p_assignment_operator(p):
	'''
	assignment_operator : ASSIGN
						| MULASSIGN
						| DIVASSIGN
						| MODASSIGN
						| PLUSASSIGN
						| MINUSASSIGN
						| LSASSIGN
						| RSASSIGN
						| ANDASSIGN
						| XORASSIGN
						| ORASSIGN
	'''
	p[0] = Node("assignment_operator", None, p[1])


def p_expression(p):
	'''
	expression : assignment_expression
			   | expression COMMA assignment_expression
	'''
	if len(p)==1:
		p[0] = Node("expression", [p[1]], None)
	else:
		p[0] = Node("expression", [p[1],p[3]], p[2])


def p_constant_expression(p):
	'''
	constant_expression : conditional_expression
	'''
	p[0] = Node("constant_expression", [p[1]], None)

def p_declaration(p):
    '''
    declaration : declaration_specifiers SEMICOLON
                | declaration_specifiers init_declarator_list SEMICOLON
    '''
    if (len(p)==3):
        p[0] = Node("declaration", p[1], p[2])
    else:
        p[0] = Node("declaration", [p[1],p[2]], p[3])


def p_declaration_specifiers(p):
    '''
    declaration_specifiers : storage_class_specifier
                           | storage_class_specifier declaration_specifiers
                           | type_specifier
                           | type_specifier declaration_specifiers
                           | type_qualifier
                           | type_qualifier declaration_specifiers
    '''
    if (len(p)==2):
        p[0] = Node("declaration_specifiers", p[1], None)
    else:
        p[0] = Node("declaration_specifiers", [p[1],p[2]], None)

        
def p_init_declarator_list(p):
    '''
    init_declarator_list : init_declarator
                         | init_declarator_list COMMA init_declarator
    '''
    if (len(p)==4):
        p[0] = Node("init_declarator_list", [p[1],p[3]], p[2])
    else:
        p[0] = Node("init_declarator_list", p[1], None)
        

def p_init_declarator(p):
    '''
    init_declarator : declarator
                    | declarator ASSIGN initializer
    '''
    if (len(p)==4):
        p[0] = Node("init_declarator", [p[1],p[3]], p[2])
    else:
        p[0] = Node("init_declarator", p[1], None)


def p_storage_class_specifier(p):
    '''
    storage_class_specifier : TYPEDEF
                            | EXTERN
                            | STATIC
                            | AUTO
                            | REGISTER
    '''
    p[0] = Node("storage_class_specifier", None, None)

    
def p_type_specifier(p):
    '''
    type_specifier : VOID
                   | CHAR
                   | SHORT
                   | INT
                   | LONG
                   | FLOAT
                   | DOUBLE
                   | SIGNED
                   | UNSIGNED
                   | struct_or_union_specifier
                   | enum_specifier
                   | TYPE_NAME
    '''
    p[0] = Node("type_specifier", None, None)

def p_struct_or_union_specifier(p):
    '''
    struct_or_union_specifier : struct_or_union ID OCP struct_declaration_list CCP
                              | struct_or_union OCP struct_declaration_list CCP
                              | struct_or_union ID
    '''
    if (len(p)==3):
        p[0] = Node("struct_or_union_specifier", p[1], p[2])
    elif (len(p)==5):
        p[0] = Node("struct_or_union_specifier", [p[1],p[3]], [p[2],p[4]])
    else:
        p[0] = Node("struct_or_union_specifier", [p[1],p[4]], [p[2],p[3],p[5]])


def p_struct_or_union(p):
    '''
    struct_or_union : STRUCT
                    | UNION
    '''
    p[0] = Node("struct_or_union", None, None)

def p_struct_declaration_list(p):
    '''
    struct_declaration_list : struct_declaration
                            | struct_declaration_list struct_declaration
    '''
    if (len(p)==2):
        p[0] = Node("struct_declaration_list", p[1], None)
    else:
        p[0] = Node("struct_declaration_list", [p[1],p[2]], None)


def p_struct_declaration(p):
    '''
    struct_declaration : specifier_qualifier_list struct_declarator_list SEMICOLON
    '''
    p[0] = Node("struct_declaration", [p[1],p[2]], p[3])


def p_specifier_qualifier_list(p):
    '''
    specifier_qualifier_list : type_specifier specifier_qualifier_list
                             | type_specifier
                             | type_qualifier specifier_qualifier_list
                             | type_qualifier
    '''
    if (len(p)==2):
        p[0] = Node("specifier_qualifier_list", p[1], None)
    else:
        p[0] = Node("specifier_qualifier_list", [p[1],p[2]], None)
    
def p_struct_declarator_list(p):
    '''
    struct_declarator_list : struct_declarator
                           | struct_declarator_list COMMA struct_declarator
    '''
    if (len(p)==4):
        p[0] = Node("struct_declarator_list", [p[1],p[3]], p[2])
    else:
        p[0] = Node("struct_declarator_list", p[1], None)

        
def p_struct_declarator(p):
    '''
    struct_declarator : declarator
                      | COLON constant_expression
                      | declarator COLON constant_expression
    '''
    if (len(p)==2):
        p[0] = Node("struct_declarator", p[1], None)
    elif (len(p)==3):
        p[0] = Node("struct_declarator", p[2], p[1])
    elif (len(p)==4):
        p[0] = Node("struct_declarator", [p[1],p[3]], p[2])

def p_enum_specifier(p):
    '''
    enum_specifier : ENUM OCP enumerator_list CCP
                   | ENUM ID OCP enumerator_list CCP
                   | ENUM ID
    '''
    if (len(p)==3):
        p[0] = Node("enum_specifier", None, p[2])
    elif (len(p)==5):
        p[0] = Node("enum_specifier", p[3], [p[2],p[4]])
    else:
        p[0] = Node("enum_specifier", p[4], [p[2],p[3],p[5]])


def p_enumerator_list(p):
    '''
    enumerator_list : enumerator
                    | enumerator_list COMMA enumerator
    '''
    if (len(p)==4):
        p[0] = Node("enumerator_list", [p[1],p[3]], p[2])
    else:
        p[0] = Node("enumerator_list", p[1], None)


def p_enumerator(p):
    '''
    enumerator : ID
               | ID ASSIGN constant_expression
    '''
    if (len(p)==4):
        p[0] = Node("enumerator", [p[1],p[3]], p[2])
    else:
        p[0] = Node("enumerator", p[1], None)


def p_type_qualifier(p):
    '''
    type_qualifier : CONST
                   | VOLATILE
    '''
    p[0] = Node("type_qualifier", None, None)
    
	
def p_declarator(p):
    '''
    declarator : pointer direct_declarator
               | direct_declarator
    '''
    if (len(p)==3):
        p[0] = Node("declarator", [p[1],p[2]], None)
    else:
        p[0] = Node("declarator", p[1], None)

        
def p_direct_declarator(p):
    '''
    direct_declarator : ID
                      | OP declarator CP
                      | direct_declarator OSP constant_expression CSP
                      | direct_declarator OSP CSP
                      | direct_declarator OP parameter_type_list CP
                      | direct_declarator OP identifier_list CP
                      | direct_declarator OP CP
    '''
    if (len(p)==2):
        p[0] = Node("direct_declarator", None, p[1])
    elif p[1]=='(':
        p[0] = Node("direct_declarator", p[2], [p[1],p[3]])
    elif (len(p)==4):
        p[0] = Node("direct_declarator", [p[1]], [p[2],p[3]])
    elif (len(p)==5):
        p[0] = Node("direct_declarator", [p[1],p[3]], [p[2],p[4]])
        
        

def p_pointer(p):
    '''
    pointer : MULTIPLY
            | MULTIPLY type_qualifier_list
            | MULTIPLY pointer
            | MULTIPLY type_qualifier_list pointer
    '''
    if (len(p)==2):
        p[0] = Node("pointer", None, p[1])
    elif (len(p)==3):
        p[0] = Node("pointer", p[2], p[1])
    else:
        p[0] = Node("pointer", [p[2],p[3]], p[1])



def p_type_qualifier_list(p):
    '''
    type_qualifier_list : type_qualifier
                        | type_qualifier_list type_qualifier
    '''
    p[0] = Node('asdf', [p[1]])

def p_parameter_type_list(p):
    '''
    parameter_type_list : parameter_list
                        | parameter_list COMMA ELLIPSIS
    '''
    p[0] = Node('asdf', [p[1]])

def p_parameter_list(p):
    '''
    parameter_list : parameter_declaration
                   | parameter_list COMMA parameter_declaration
    '''
    p[0] = Node('asdf', [p[1]])

def p_parameter_declaration(p):
    '''
    parameter_declaration : declaration_specifiers declarator
                          | declaration_specifiers abstract_declarator
                          | declaration_specifiers
    '''
    p[0] = Node('asdf', [p[1]])

def p_identifier_list(p):
    '''
    identifier_list : ID
                    | identifier_list COMMA ID
    '''
    p[0] = Node('asdf', [p[1]])

def p_type_name(p):
    '''
    type_name : specifier_qualifier_list
              | specifier_qualifier_list abstract_declarator
    '''
    p[0] = Node('asdf', [p[1]])

def p_abstract_declarator(p):
    '''
    abstract_declarator : pointer
                        | direct_abstract_declarator
                        | pointer direct_abstract_declarator
    '''
    p[0] = Node('asdf', [p[1]])

def p_direct_abstract_declarator(p):
    '''
    direct_abstract_declarator : OP abstract_declarator CP
                               | OSP CSP
                               | OSP constant_expression CSP
                               | direct_abstract_declarator OSP CSP
                               | direct_abstract_declarator OSP constant_expression CSP
                               | OP CP
                               | OP parameter_type_list CP
                               | direct_abstract_declarator OP CP
                               | direct_abstract_declarator OP parameter_type_list CP
    '''
    p[0] = Node('asdf', [p[1]])

def p_initializer(p):
    '''
    initializer : assignment_expression
                | OCP initializer_list CCP
                | OCP initializer_list COMMA CSP
    '''
    p[0] = Node('asdf', [p[1]])

def p_initializer_list(p):
    '''
    initializer_list : initializer
                     | initializer_list COMMA initializer
    '''
    p[0] = Node('asdf', [p[1]])

def p_statement(p):
    '''
    statement : labeled_statement
              | compound_statement
              | expression_statement
              | selection_statement
              | iteration_statement
              | jump_statement
    '''
    p[0] = Node('asdf', [p[1]])

def p_labeled_statement(p):
    '''
    labeled_statement : ID COLON statement
                      | CASE constant_expression COLON statement
                      | DEFAULT COLON statement
    '''
    p[0] = Node('asdf', [p[1]])

def p_compound_statement(p):
    '''
    compound_statement : OCP CCP
                       | OCP statement_list CCP
                       | OCP declaration_list CCP
                       | OCP declaration_list statement_list CCP
    '''
    p[0] = Node('asdf', [p[1]])

def p_declaration_list(p):
    '''
    declaration_list : declaration
                     | declaration_list declaration
    '''
    p[0] = Node('asdf', [p[1]])

def p_statement_list(p):
    '''
    statement_list : statement
                   | statement_list statement
    '''
    p[0] = Node('asdf', [p[1]])

def p_expression_statement(p):
    '''
    expression_statement : SEMICOLON
                         | expression SEMICOLON
    '''
    p[0] = Node('asdf', [p[1]])

def p_selection_statement(p):
    '''
    selection_statement : IF OP expression CP statement
                        | IF OP expression CP statement ELSE statement
                        | SWITCH OP expression CP statement
    '''
    if(len(p) == 6): p[0] = Node('if-then', [p[3], p[5]], None)
    elif(len(p) == 8): p[0] = Node('if-then-else', [p[3], p[5], p[7]], None)
	
def p_iteration_statement(p):
    '''
    iteration_statement : WHILE OP expression CP statement
                        | DO statement WHILE OP expression CP SEMICOLON
                        | FOR OP expression_statement expression_statement CP statement
                        | FOR OP expression_statement expression_statement expression CP statement
    '''
    p[0] = Node('asdf', [p[1]])

def p_jump_statement(p):
    '''
    jump_statement : GOTO ID SEMICOLON
                   | CONTINUE SEMICOLON
                   | BREAK SEMICOLON
                   | RETURN SEMICOLON
                   | RETURN expression SEMICOLON
    '''
    p[0] = Node('asdf', [p[1]])

def p_translation_unit(p):
    '''
    translation_unit : external_declaration
                     | translation_unit external_declaration
    '''
    p[0] = Node('asdf', [p[1]])

def p_external_declaration(p):
    '''
    external_declaration : function_definition
                         | declaration
    '''
    p[0] = Node('asdf', [p[1]])

def p_function_definition(p):
    '''
    function_definition : declaration_specifiers declarator declaration_list compound_statement
                        | declaration_specifiers declarator compound_statement
                        | declarator declaration_list compound_statement
                        | declarator compound_statement
    '''
    p[0] = Node('asdf', [p[1]])

def p_error(p):
    print("error for ", p)
    print("Syntax Error found at ", p.lineno)
    

parser = yacc.yacc(debug=1)
