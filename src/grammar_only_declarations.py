import sys
import ply.yacc as yacc
from lexrules import tokens
import functions



class Node:
	def __init__(self, typex, children=None, leaf=None):
		self.name = typex
		if children:
			self.children = children
		else:
			self.children = [ ]
		self.leaf = leaf
		self.type = typex
		self.variables = []
		self.types_of_var = []

start = 'translation_unit'

#CHECKK string added
#CHECKK definitions changed, one more level added
def p_primary_expression(p):
	'''
	primary_expression : id
						| char_const
						| string
						| number
						| OP expression CP
	'''
	if p[1]=='(':
	  p[0] = p[2]
	else:
		p[0] = Node("primary_expression", [p[1]])
		p[0].type = p[1].type

def p_id(p):
	'''
	id : ID
	'''
	p[0] = Node("ID", None,p[1])
	p[0].name = 'id'
	x = functions.check_in_var(p[1])
	if x==None:
		p[0].type = 'EMPTY'
		print("UNDECLARED VARIABLE ERROR")
	else:
		p[0].type = x['type']

def p_char_const(p):
	'''
	char_const : CHAR_CONST
	'''
	p[0] = Node("char_const", None,p[1])
	p[0].type="char"

def p_string(p):
	'''
	string : STRING
	'''
	p[0] = Node("string", None,p[1])
	p[0].type="string"
	
def p_number(p):
	'''
	number : NUMBER
	'''
	p[0] = Node("number", None,p[1])
	p[0].type="int"


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
	if len(p)==2:#1
		p[0] = p[1]
	elif p[2]=='[':
		p[0] = Node("postfix_expression", [p[3]], p[1]) #CHECKK
		#p[0] = Node("postfix_expression", [p[1],p[3]], None)#2
	elif p[2]=='++':
		p[0] = Node("postfix_expression", [p[1]], p[2])#7
	elif p[2]=='--':
		p[0] = Node("postfix_expression", [p[1]], p[2])#8
	elif p[2]=='.':
		p[0] = Node("postfix_dot_exp", [p[1]], p[3])#5
	elif p[2]=='->':
		p[0] = Node("postfix_arrow_exp", [p[1]], p[3])#6
	elif p[3]==')':#3
		p[0] = p[1]
	elif p[2]=='(':#4
		p[0] = Node("postfix_expression", [p[3]], p[1])#CHECKK
		#p[0] = Node("postfix_expression", [p[1],p[3]], None)

def p_argument_expression_list(p):
	'''
	argument_expression_list : assignment_expression
							| argument_expression_list COMMA assignment_expression
	'''
	if len(p)==2:
		p[0] = p[1]
	else:
		p[0] = Node("arg_expr_list", [p[1],p[3]], None) #CHECKK, Comma not taken in leaf, all members of list connected to same node

def p_unary_expression(p):
	'''
	unary_expression : postfix_expression
						| INCREMENT unary_expression
						| DECREMENT unary_expression
						| unary_operator cast_expression
						| SIZEOF unary_expression
						| SIZEOF OP type_name CP
	'''
	if len(p)==2:
		p[0] = p[1]
	elif p[1]=='++':
		p[0] = Node("unary_expression", [p[2]], p[1])#2
	elif p[1]=='--':
		p[0] = Node("unary_expression", [p[2]], p[1])#3
	elif p[2]=='(':
		p[0] = Node("unary_expression", [p[3]], p[1])#6 #??
	elif p[1]=='sizeof':
		p[0] = Node("unary_expression", [p[2]], p[1])#5
	else:
		p[0] = Node("unary_expression", [p[2]], p[1])#4

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
	if len(p)==2:
		p[0] = p[1]
	else:
		p[0] = p[4]

#CHECKK second, third rule, added OP, CP rule
def p_multiplicative_expression(p):
	'''
	multiplicative_expression : cast_expression
							| OP multiplicative_expression CP
							| OP additive_expression CP
							| multiplicative_expression MULTIPLY cast_expression
							| multiplicative_expression DIVIDE cast_expression
							| multiplicative_expression MOD cast_expression
	'''
	if len(p)==2:
		p[0] = p[1]
	elif p[1]=='(':
		p[0] = p[2]
	else:
		p[0] = Node("unary_expression", [p[1],p[3]], p[2])


def p_additive_expression(p):
	'''
	additive_expression : multiplicative_expression 
						| additive_expression ADD multiplicative_expression
						| additive_expression SUBTRACT multiplicative_expression
	'''
	if len(p)==2:
		p[0] = p[1]
	elif p[1]=='(':
		p[0] = p[2]
	else:
		p[0] = Node("additive_expression", [p[1],p[3]], p[2])

def p_shift_expression(p):
	'''
	shift_expression : additive_expression
					| shift_expression LSHIFT additive_expression
					| shift_expression RSHIFT additive_expression
	'''
	if len(p)==2:
		p[0] = p[1]
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
	if len(p)==2:
		p[0] = p[1]
	else:
		p[0] = Node("relational_expression", [p[1],p[3]], p[2])

def p_equality_expression(p):
	'''
	equality_expression : relational_expression
						| equality_expression EQUAL relational_expression
						| equality_expression NEQ relational_expression
	'''
	if len(p)==2:
		p[0] = p[1]
	else:
		p[0] = Node("equality_expression", [p[1],p[3]], p[2])

def p_and_expression(p):
	'''
	and_expression : equality_expression
					| and_expression B_AND equality_expression
	'''
	if len(p)==2:
		p[0] = p[1]
	else:
		p[0] = Node("and_expression", [p[1],p[3]], p[2])
	
def p_exclusive_or_expression(p):
	'''
	exclusive_or_expression : and_expression
							| exclusive_or_expression XOR and_expression
	'''
	if len(p)==2:
		p[0] = p[1]
	else:
		p[0] = Node("exclusive_or_expression", [p[1],p[3]], p[2])

def p_inclusive_or_expression(p):
	'''
	inclusive_or_expression : exclusive_or_expression
							| inclusive_or_expression B_OR exclusive_or_expression
	'''
	if len(p)==2:
		p[0] = p[1]
	else:
		p[0] = Node("inclusive_or_expression", [p[1],p[3]], p[2])

def p_logical_and_expression(p):
	'''
	logical_and_expression : inclusive_or_expression
						   | logical_and_expression AND inclusive_or_expression
	'''
	if len(p)==2:
		p[0] = p[1]
	else:
		p[0] = Node("logical_and_expression", [p[1],p[3]], p[2])

def p_logical_or_expression(p):
	'''
	logical_or_expression : logical_and_expression
						  | logical_or_expression OR logical_and_expression
	'''
	if len(p)==2:
		p[0] = p[1]
	else:
		p[0] = Node("logical_or_expression", [p[1],p[3]], p[2])

def p_conditional_expression(p):
	'''
	conditional_expression : logical_or_expression
						   | logical_or_expression TERNARYOP expression COLON conditional_expression
	'''
	if len(p)==2:
		p[0] = p[1]
	else:
		p[0] = Node("conditional_expression", [p[1],p[3],p[5]], '? :') #??

def p_assignment_expression(p):
	'''
	assignment_expression : conditional_expression
						  | unary_expression assignment_operator assignment_expression    
	'''

	if len(p)==2:
		p[0] = p[1]
	else:
		p[0] = Node("assignment_expression", [p[1],p[3]], p[2])

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
	if len(p)==2:
		p[0] = p[1]
	else:
		p[0] = Node("expression", [p[1],p[3]], None) #CHECKK Comma removed


def p_constant_expression(p):
	'''
	constant_expression : conditional_expression
	'''
	p[0] = p[1]

def p_declaration(p):
	'''
	declaration : declaration_specifiers SEMICOLON
				| declaration_specifiers init_declarator_list SEMICOLON
	'''
	if len(p)==3:
		p[0] = p[1]
	else:
		p[0] = Node("declaration", [p[1],p[2]], None)
		for i in range(0,len(p[2].variables)):
			# int x;
			if p[2].types_of_var[i] == 'empty':
				print("---",p[2].variables[i],p[2].types_of_var[i],p[1].type)
				functions.make_var_entry(p[2].variables[i],p[1].type)
				p[2].types_of_var[i] = p[1].type
			# int x = 5;
			elif p[1].type!=p[2].types_of_var[i]:
				print("TYPE ERROR IN DECLARATION")
				print("---",p[2].variables[i],p[2].types_of_var[i],p[1].type)
		p[0].type=p[1].type



def p_declaration_specifiers(p):
	'''
	declaration_specifiers : storage_class_specifier
						   | storage_class_specifier declaration_specifiers
						   | type_specifier
						   | type_specifier declaration_specifiers
						   | type_qualifier
						   | type_qualifier declaration_specifiers
	'''
	if len(p)==2:
		p[0] = p[1]
	else:
		p[0] = Node("declaration_specifiers", [p[1],p[2]], None)

		
def p_init_declarator_list(p):
	'''
	init_declarator_list : init_declarator
						 | init_declarator_list COMMA init_declarator
	'''
	if (len(p)==4):
		p[0] = Node("init_declarator_list", [p[1],p[3]], None)
		p[0].variables=p[1].variables
		p[0].types_of_var=p[1].types_of_var
		p[0].variables+=p[3].variables
		p[0].types_of_var+=p[3].types_of_var
	else:
		p[0] = p[1]
		p[0].variables+=p[1].variables
		p[0].types_of_var+=p[1].types_of_var

def p_init_declarator(p):
	'''
	init_declarator : declarator
					| declarator ASSIGN initializer
	'''
	if (len(p)==4):
		p[0] = Node("init_declarator", [p[1],p[3]], p[2])
		p[1].type = p[3].type
		p[0].type = p[1].type #Inherited
		# Add the actual type of ID 
		functions.make_var_entry(p[1].variables[0],p[3].type)
		p[1].types_of_var[0] = p[3].type
		p[0].variables.append(p[1].variables[0])
		p[0].types_of_var.append(p[1].types_of_var[0])
	else:
		p[0] = p[1]
		p[1].type="empty"
		p[0].type=p[1].type
		p[0].variables.append(p[1].variables[0])
		p[0].types_of_var.append(p[1].types_of_var[0])

def p_storage_class_specifier(p):
	'''
	storage_class_specifier : TYPEDEF
							| EXTERN
							| STATIC
							| AUTO
							| REGISTER
	'''
	p[0] = None

	
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
	if isinstance(p[1],str):
		p[0] = Node('type_specifier')
		p[0].type = p[1]
	else:
		p[0] = p[1]

def p_struct_or_union_specifier(p):
	'''
	struct_or_union_specifier : struct_or_union ID ocp struct_declaration_list ccp
							  | struct_or_union OCP struct_declaration_list CCP
							  | struct_or_union ID
	'''
	if len(p)==3:
		p[0] = Node("struct_or_union_specifier", [p[1]], p[2])
	elif len(p)==5:
		p[0] = Node("struct_or_union_specifier", [p[1],p[3]], None)
	else:
		p[0] = Node("struct_or_union_specifier", [p[1],p[2],p[4]], 'struct/union')
		functions.make_struct_entry(p[2])


def p_struct_or_union(p):
	'''
	struct_or_union : STRUCT
					| UNION
	'''
	p[0] = None

def p_struct_declaration_list(p):
	'''
	struct_declaration_list : struct_declaration
							| struct_declaration_list struct_declaration
	'''
	if (len(p)==2):
		p[0] = p[1]
	else:
		p[0] = Node("struct_declaration_list", [p[1],p[2]], None)


def p_struct_declaration(p):
	'''
	struct_declaration : specifier_qualifier_list struct_declarator_list SEMICOLON
	'''
	p[0] = Node("struct_declaration", [p[1],p[2]], None)
	for x in p[2].variables:
		functions.make_var_entry(x,p[1].type)
	p[0].type=p[1].type

def p_specifier_qualifier_list(p):
	'''
	specifier_qualifier_list : type_specifier specifier_qualifier_list
							 | type_specifier
							 | type_qualifier specifier_qualifier_list
							 | type_qualifier
	'''
	if (len(p)==2):
		p[0] = p[1]
	else:
		p[0] = Node("specifier_qualifier_list", [p[1],p[2]], None)
	
def p_struct_declarator_list(p):
	'''
	struct_declarator_list : struct_declarator
						   | struct_declarator_list COMMA struct_declarator
	'''
	if (len(p)==4):
		p[0] = Node("struct_declarator_list", [p[1],p[3]], None)
		p[0].variables=p[1].variables
		p[0].types_of_var=p[1].types_of_var
		p[0].variables+=p[3].variables
		p[0].types_of_var+=p[3].types_of_var

	else:
		p[0] = p[1]

		
def p_struct_declarator(p):
	'''
	struct_declarator : declarator
					  | COLON constant_expression
					  | declarator COLON constant_expression
	'''
	if (len(p)==2):
		p[0] = p[1]
	elif (len(p)==3):
		p[0] = Node("struct_declarator", [p[2]], p[1])
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
		p[0] = p[3]
	else:
		p[0] = Node("enum_specifier", [p[4]], p[2])


def p_enumerator_list(p):
	'''
	enumerator_list : enumerator
					| enumerator_list COMMA enumerator
	'''
	if (len(p)==4):
		p[0] = Node("enumerator_list", [p[1],p[3]], None)
	else:
		p[0] = Node("enumerator_list", [p[1]], None)


def p_enumerator(p):
	'''
	enumerator : ID
			   | ID ASSIGN constant_expression
	'''
	if (len(p)==4):
		p[0] = Node("enumerator", [p[1],p[3]], p[2])
	else:
		p[0] = Node("enumerator", [p[1]], None)


def p_type_qualifier(p):
	'''
	type_qualifier : CONST
				   | VOLATILE
	'''
	p[0] = None
	
	
def p_declarator(p):
	'''
	declarator : pointer direct_declarator
			   | direct_declarator
	'''
	if len(p)==3:
		p[0] = Node("declarator", [p[1],p[2]], None)
	else:
		p[0] = p[1]

		
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
	if len(p)==2:
		p[0] = Node("direct_declarator", None, p[1])
		p[0].type = 'empty'
		p[0].variables.append(p[1])
		p[0].types_of_var.append("empty")
	elif p[1]=='(': 
		p[0] = p[2]
	elif len(p)==4:
		p[0] = p[1]
		if p[1]=='(':#Redundant
			p[0].variables=p[1].variables
			p[0].types_of_var=p[1].types_of_var
	elif len(p)==5:
		p[0] = Node("direct_declarator", [p[3]], p[1]) #CHECKK Direct decl made leaf so that param_type_list, id_list can attatch to that node
		if p[2]=='(': # Making function variable entry
			# Add all the info in the list. Make function and params/ids i.e args entry in symtab in p_func_def
			p[0].variables=p[1].variables
			p[0].types_of_var=p[1].types_of_var
			p[0].variables+=p[3].variables
			p[0].types_of_var+=p[3].types_of_var
		else:
			p[0].variables=p[1].variables
			p[0].types_of_var=p[1].types_of_var

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
		p[0] = Node("pointer", [p[2]], p[1])
	else:
		p[0] = Node("pointer", [p[2],p[3]], p[1])



def p_type_qualifier_list(p):
	'''
	type_qualifier_list : type_qualifier
						| type_qualifier_list type_qualifier
	'''
	if (len(p)==3):
		p[0] = Node("type_qualifier_list", [p[1],p[2]], None)
	else:
		p[0] = p[1]

def p_parameter_type_list(p):
	'''
	parameter_type_list : parameter_list
						| parameter_list COMMA ELLIPSIS
	'''
	if (len(p)==4):
		p[0] = Node("parameter_type_list", p[1],  p[3])
	else:
		p[0] = p[1]

def p_parameter_list(p):
	'''
	parameter_list : parameter_declaration
				   | parameter_list COMMA parameter_declaration
	'''
	if (len(p)==4):
		p[0] = Node("parameter_list", [p[1], p[3]], None)
		p[0].variables=p[1].variables
		p[0].types_of_var=p[1].types_of_var
		p[0].variables+=p[3].variables
		p[0].types_of_var+=p[3].types_of_var
	else:
		p[0] = p[1]
		p[0].variables+=p[1].variables
		p[0].types_of_var+=p[1].types_of_var

def p_parameter_declaration(p):
	'''
	parameter_declaration : declaration_specifiers declarator
						  | declaration_specifiers abstract_declarator
						  | declaration_specifiers
	'''
	if (len(p)==3):
		p[0] = Node("parameter_declaration", [p[1], p[2]], None)
		p[2].types_of_var[0]=p[1].type
		p[0].type=p[1].type
		p[0].variables=p[2].variables
		p[0].types_of_var=p[2].types_of_var
	else:
		p[0] = p[1]

def p_identifier_list(p):
	'''
	identifier_list : ID
					| identifier_list COMMA ID
	'''
	if (len(p)==4):
		p[0] = Node("identifier_list", [p[1],p[3]],  None)
		p[0].variables=p[1].variables
		p[0].types_of_var=p[1].types_of_var
		p[0].variables.append(p[3])
		p[0].types_of_var.append('empty')
	else:
		p[0] = Node("identifier_list", None, p[1])
		p[0].variables.append(p[1])
		p[0].types_of_var.append('empty')

def p_type_name(p):
	'''
	type_name : specifier_qualifier_list
			  | specifier_qualifier_list abstract_declarator
	'''
	if (len(p)==3):
		p[0] = Node("type_name", [p[1],p[2]], None)
	else:
		p[0] = p[1]

def p_abstract_declarator(p):
	'''
	abstract_declarator : pointer
						| direct_abstract_declarator
						| pointer direct_abstract_declarator
	'''
	if (len(p)==3):
		p[0] = Node("type_name", [p[1],p[2]], None)
	else:
		p[0] = p[1]

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
	if (len(p)==3):
		p[0] = None
	elif (len(p)==5):
		p[0] = Node("type_name", [p[3]], p[1]) #CHECKK p[1] made child coz of list
	elif (p[1]=='(' or p[1]=='['):
		p[0] = p[2]
	else:
		p[0] = p[1]

def p_initializer(p):
	'''
	initializer : assignment_expression
				| OCP initializer_list CCP
				| OCP initializer_list COMMA CSP
	'''
	if len(p)==5:
		p[0] = Node('initializer', [p[2]],p[3])
	elif len(p)==4:
		p[0] = p[2]
	else:
		p[0] = p[1]

def p_initializer_list(p):
	'''
	initializer_list : initializer
					 | initializer_list COMMA initializer
	'''
	if len(p)==2:
		p[0] = p[1]
	else:
		p[0] = Node('initializer_list',[p[1],p[3]],None)

def p_statement(p):
	'''
	statement : labeled_statement
			  | compound_statement
			  | expression_statement
			  | selection_statement
			  | iteration_statement
			  | jump_statement
	'''
	p[0] = p[1]

def p_labeled_statement(p):
	'''
	labeled_statement : ID COLON statement
					  | CASE constant_expression COLON statement
					  | DEFAULT COLON statement
	'''
	if len(p) == 4:
		if p[1] == 'default':
			p[0] = Node('labeled-stmt-default', [p[3]])
		else:
			p[0] = Node('labeled-stmt-normal', [p[1], p[3]])

	elif len(p) == 5:
		p[0] = Node('labeled-stmt-case', [p[2], p[4]])

def p_compound_statement(p):
	'''
	compound_statement : OCP CCP
					   | ocp statement_list ccp
					   | ocp declaration_list ccp
					   | ocp declaration_list statement_list ccp
	'''
	if len(p)==4:
		p[0] = Node('compound_statement',[p[2]],'{}')
	elif len(p)==5:
		p[0] = Node('compound_statement',[p[2],p[3]],'{}')
	else:
		p[0]=None		

def p_ocp(p):
	'''
	ocp : OCP
	'''
	functions.newscope()

def p_ccp(p):
	'''
	ccp : CCP
	'''
	functions.endscope()


def p_declaration_list(p):
	'''
	declaration_list : declaration
					 | declaration_list declaration
	'''
	if len(p) == 2:
		p[0] = p[1]
	else:
		p[0] = Node('decl-list', [p[1], p[2]])


def p_statement_list(p):
	'''
	statement_list : statement
				   | statement_list statement
	'''
	if len(p) == 2:
		p[0] = Node('stmt', [p[1]])
	else:
		p[0] = Node('stmt-list', [p[1], p[2]])

def p_expression_statement(p):
	'''
	expression_statement : SEMICOLON
						 | expression SEMICOLON
	'''
	if len(p) == 3:
		p[0] = Node('expr-stmt', [p[1]], None)

def p_selection_statement(p):
	'''
	selection_statement : IF OP expression CP statement
						| IF OP expression CP statement ELSE statement
						| SWITCH OP expression CP statement
	'''
	if len(p) == 6: 
		if p[1] == 'if' : p[0] = Node('if-then', [p[3], p[5]], "if")
		else: p[0] = Node('switch', [p[3], p[5]], 'switch')

	elif len(p) == 8: p[0] = Node('if-then-else', [p[3], p[5], p[7]], "if-then-else")
	
def p_iteration_statement(p):
	'''
	iteration_statement : WHILE OP expression CP statement 
						| DO statement WHILE OP expression CP SEMICOLON
						| FOR OP expression_statement expression_statement CP statement
						| FOR OP expression_statement expression_statement expression CP statement
	'''
	if len(p) == 6:
		p[0] = Node('while', [p[3], p[5]], 'while')

	elif len(p) == 8:
		if p[1] == 'for': p[0] = Node('for-with-update', [p[3], p[4], p[5],p[7]], 'for-with-update')
		else: p[0] = Node('do-while', [p[2], p[5]], 'do-while')

	elif len(p) == 7:
		p[0] = Node('for-no-update', [p[3], p[4],p[6]], 'for-no-update')

def p_jump_statement(p):
	'''
	jump_statement : GOTO ID SEMICOLON
				   | CONTINUE SEMICOLON
				   | BREAK SEMICOLON
				   | RETURN SEMICOLON
				   | RETURN expression SEMICOLON
	'''
	if len(p) == 4:
		if p[1] == 'goto': p[0] = Node('goto', p[2], "goto") #CHECKK
		else: p[0] = Node('return', [p[2]], "return");
	else:
		if p[1] == 'continue': p[0] = Node('continue', None, 'continue')
		if p[1] == 'break': p[0] = Node('break', None, 'break')
		if p[1] == 'return': p[0] = Node('return', None, 'return')


def p_translation_unit(p):
	'''
	translation_unit : external_declaration
					 | translation_unit external_declaration
	'''
	if len(p) == 2:
		p[0] = Node('start_state', [p[1]], None)
	else:
		p[0]= Node('start_state_1', [p[1], p[2]], None)

def p_external_declaration(p):
	'''
	external_declaration : function_definition
						 | declaration
	'''
	p[0] = p[1]

def p_function_definition(p):
	'''
	function_definition : declaration_specifiers declarator declaration_list compound_statement
						| declaration_specifiers declarator compound_statement
						| declarator declaration_list compound_statement
						| declarator compound_statement
	'''
	if len(p)==3:
		print("func_defn_1")
		p[0] = Node('func_defn_1',[p[1],p[2]],None)
	elif len(p)==4:
		print("func_defn_2")
		p[0] = Node('func_defn_2',[p[1],p[2],p[3]],None)
		p[2].type=p[1].type
		p[0].type = p[1].type
		# Make all the entries : func name in parent symtab and all args in 
		functions.make_func_entry(p[2].variables,p[2].types_of_var)
	elif len(p)==5:
		print("func_defn_3")
		p[0] = Node('func_defn_3',[p[1],p[2],p[3],p[4]],None)

def p_error(p):
	print("error for ", p)
	print("Syntax Error found at ", p.lineno)
	

parser = yacc.yacc(debug=1)
