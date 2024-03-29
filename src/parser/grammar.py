import sys
import ply.yacc as yacc
from lexer.lexrules import tokens
import symbol_table as st
from errors.error import messages 

instr = [] 
counter = 0
func_name = ""
func_type_list = []

class Node:
	def __init__(self, typex, children=None, leaf=None):
		self.name = typex
		if children:
			self.children = children
		else:
			self.children = [ ]

		self.leaf = leaf
		self.type = typex
		self.size = typex 
		self.const = 0# compile time constant
		self.class_type = 'local' #Will be changed acc.
		self.variables = []
		self.types_of_var = []
		self.numof = 0
		self.place = typex
		self.quad = typex
		self.truelist = []
		self.falselist = []
		self.nextlist = []
		self.breaklist = []
		self.continuelist = []
		self.returnlist = []
		self.param_list = []
		self.offset = 0
		self.ret = typex
		self.value = None #To store constants, for array size, say, a[10]
		self.values_of_var = []
		
def newvar(tt):
	global counter
	counter = counter + 1
	name = 'tmp@' + str(counter)
	st.make_var_entry(name, tt, False, None)
	return name
	
def backpatch(lists, quad):
	global instr
	for i in range(len(lists)):
		instr[int(lists[i])] = instr[int(lists[i])] + ' {' + str(quad) + '}'


start = 'translation_unit'

size = {}

size['INT'] = 4
size['CHAR'] = 1
size['FLOAT'] = 4
size['BOOL'] = 1
size["pointer_"] = 8
size['VOID'] = 0

def p_primary_expression(p):
	'''
	primary_expression : id
						| char_const
						| string
						| int
						| float
						| OP expression CP
	'''
	if p[1]=='(':
	  p[0] = p[2]
	  p[0].type = p[2].type
	  p[0].size = p[2].size
	  p[0].place = p[2].place
	  p[0].truelist = []
	  p[0].falselist = []
	  p[0].ret = p[2].ret
	else:
		p[0] = Node("primary_expression", [p[1]])
		p[0].type = p[1].type
		p[0].variables = p[1].variables
		p[0].size = p[1].size
		p[0].place = p[1].place
		p[0].truelist = []
		p[0].falselist = []
		p[0].value = p[1].value
		p[0].ret = p[1].ret
	p[0].name = 'primary_expression'	

def p_id(p):
	'''
	id : ID
	'''
	p[0] = Node("ID", None,p[1])
	p[0].name = 'id'
	p[0].variables.append(p[1])
	x = st.check_in_var(p[1])
	if x==None:
		p[0].type = 'EMPTY'
		p[0].size = 0
		if st.checkscope()!=0 and p[1]!='printf':
			messages.add(f'Error at line {p.lineno(1)} : Variable not declared')
	else:
		if isinstance(x,str):
			p[0].type = x
		else:
			p[0].type = x['type']
		if p[0].type[:8]=='pointer_':
			p[0].size=8
		else:
			if isinstance(p[0].type,list):#Pointer initialized to array name
				p[0].size = 8
			else:
				p[0].size = size[p[0].type]
	p[0].place = p[1]
	p[0].truelist = []
	p[0].falselist = []
	p[0].ret = p[1]

def p_char_const(p):
	'''
	char_const : CHAR_CONST
	'''
	p[0] = Node("char_const", None,p[1])
	p[0].name = "char_const"
	p[0].type = 'CHAR'
	p[0].size = 1
	p[0].place = p[1]
	p[0].truelist = []
	p[0].falselist = []
	p[0].ret = p[1]
	p[0].value = p[1][1:-1]
	
def p_string(p):
	'''
	string : STRING
	'''
	p[0] = Node("string", None,p[1])
	p[0].name = "string"
	p[0].type = "pointer_CHAR"
	p[0].size = 8
	p[0].place = p[1]
	p[0].truelist = []
	p[0].falselist = []
	p[0].ret = p[1]
	
def p_int(p):
	'''
	int : I_NUMBER
	'''
	p[0] = Node("int", None,p[1])
	p[0].name = "int"
	p[0].type = 'INT'
	p[0].size = 4
	p[0].place = p[1]
	p[0].truelist = []
	p[0].falselist = []
	p[0].ret = p[1]
	if p[1]=='x' or p[1]=='X':
		p[0].value = int(p[1][2:],16)
	else:	
		p[0].value = int(p[1])
	
def p_float(p):
	'''
	float : F_NUMBER
	'''
	p[0] = Node("float", None,p[1])
	p[0].name = "float"
	p[0].type = 'FLOAT'
	p[0].size = 4
	p[0].place = p[1]
	p[0].truelist = []
	p[0].falselist = []
	p[0].ret = p[1]
	p[0].value = float(p[1])
	
def p_postfix_expression(p):
	'''
	postfix_expression : primary_expression
						| postfix_expression OSP expression CSP
						| postfix_expression OP CP
						| postfix_expression OP argument_expression_list CP
						| postfix_expression DOT id
						| postfix_expression ARROW id
						| postfix_expression INCREMENT
						| postfix_expression DECREMENT
	'''
	global instr
	if len(p)==2:
		p[0] = p[1]
		p[0].variables=p[1].variables
		p[0].type = p[1].type
		p[0].size = p[1].size
		p[0].place = p[1].place
		p[0].truelist = []
		p[0].falselist = []
		p[0].ret = p[1].ret
	elif p[2]=='[':
		p[0] = Node("postfix_expression", [p[3]], p[1])
		p[0].type = p[1].type[3]
		p[0].size = size[p[0].type]
		x = newvar('INT')
		instr.append(x + ' = ' + str(size[p[0].type]) + ' * ' + p[3].place)
		p[0].place  = p[1].place + '[' + x + ']'
		
	elif p[2]=='++':
		p[0] = Node("postfix_expression", [p[1]], p[2])#7
		if(p[1].type == 'INT' or p[1].type == 'FLOAT'):
			p[0].type = 'VOID'
			p[0].size = 0
			p[0].truelist = []
			p[0].falselist = []
			instr.append(p[1].place + ' = ' + p[1].place + ' + 1')	
		else:
			p[0].type = 'TYPE_ERROR'
			p[0].size = 0
			messages.add(f'Error at line {p.lineno(2)} : Cannot use operator {str(p[2])} with type {str(p[1].type)}')
	elif p[2]=='--':
		p[0] = Node("postfix_expression", [p[1]], p[2])#8
		if(p[1].type == 'INT' or p[1].type == 'FLOAT'):
			p[0].type = 'VOID'
			p[0].size = 0
			p[0].truelist = []
			p[0].falselist = []
			instr.append(p[1].place + ' = ' + p[1].place + ' - 1')
		else:
			p[0].type = 'TYPE_ERROR'
			p[0].size = 0
			messages.add(f'Error at line {p.lineno(2)} : Cannot use operator {str(p[2])} with type {str(p[1].type)}')
	elif p[2]=='.':
		p[0] = Node("postfix_dot_exp", [p[1]], p[3])#5
		p[0].type = p[3].type
		p[0].size = p[3].size
	elif p[2]=='->':
		p[0] = Node("postfix_arrow_exp", [p[1]], p[3])#6
		p[0].type = p[3].type
		p[0].size = p[3].size
	elif p[3]==')':
		p[0] = p[1]
		instr.append("call " + p[1].variables[0] + ", 0")
		p[0].place = "ret-val"
		if st.func_exists(p[1].variables[0]):
			x = st.check_in_fs(p[1].variables[0])
			p[0].type = x[2] #Return type of function
		else:
			if p[1].variables[0] != "printf": print("\n Function not declared WARNING \n")
	elif p[2]=='(':
		p[0] = Node("postfix_expression", [p[3]], p[1])
		p[0].place = "ret-val"
		if st.func_exists(p[1].variables[0]):
			x = st.check_in_fs(p[1].variables[0])
			p[0].type = x[2] #Return type of function
			#Checking number of parameters match or not
			if x[1]!=p[3].numof:
				messages.add(f'Error at line {p.lineno(2)}: Number of Arguments of function call do not match')
		else:
			if p[1].variables[0] != "printf": print("\n Function not declared WARNING \n")
		for i in range(p[3].numof) :
			instr.append("param " + p[3].param_list[i]+",scope"+str(st.checkscope()))
		instr.append("call " + p[1].variables[0] + ", " + str(p[3].numof))
	p[0].name = 'postfix_expression'
 		
def p_argument_expression_list(p):
	'''
	argument_expression_list : assignment_expression
							| argument_expression_list COMMA assignment_expression
	'''
	if len(p)==2:
		p[0] = p[1]
		p[0].numof = 1
		p[0].param_list.append(p[1].place)
	else:
		p[0] = Node("arg_expr_list", [p[1],p[3]], None) #CHECKK, Comma not taken in leaf, all members of list connected to same node
		p[0].numof = p[1].numof + 1
		p[0].param_list = p[1].param_list
		p[0].param_list.append(p[3].place)
	p[0].name = 'argument_expression_list'

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
		p[0].type = p[1].type
		p[0].size = p[1].size
		p[0].place = p[1].place
		p[0].truelist = []
		p[0].falselist = []
		p[0].ret = p[1].ret
	elif p[1]=='++':
		p[0] = Node("unary_expression", [p[2]], p[1])
		if(p[2].type == 'INT' or p[2].type == 'FLOAT'):
			p[0].type = 'VOID'
			p[0].size = 0
			p[0].truelist = []
			p[0].falselist = []
			instr.append(p[2].place + ' = ' + p[2].place + ' + 1')
		else:
			p[0].type = 'TYPE_ERROR'
			p[0].size = p[2].size
			messages.add(f'Error at line {p.lineno(1)} : Cannot use operator {str(p[1])} with type {str(p[2].type)}')
	elif p[1]=='--':
		p[0] = Node("unary_expression", [p[2]], p[1])
		if(p[2].type == 'INT' or p[2].type == 'FLOAT'):
			p[0].type = 'VOID'
			p[0].size = 0
			p[0].truelist = []
			p[0].falselist = []
			instr.append(p[2].place + ' = ' + p[2].place + ' - 1')
		else:
			p[0].type = 'TYPE_ERROR'
			p[0].size = p[2].size
			messages.add(f'Error at line {p.lineno(1)} : Cannot use operator {str(p[1])} with type {str(p[2].type)}')
	elif p[2]=='(':
		p[0] = Node("unary_expression", [p[3]], p[1])
		p[0].type = 'INT'
		p[0].size = 4
	elif p[1]=='sizeof':
		p[0] = Node("unary_expression", [p[2]], p[1])
		p[0].type = 'INT'
		p[0].size = 4
	else:
		p[0] = Node("unary_expression", [p[2]], p[1])
		#Pointer referencing and dereferencing
		if p[2].type[0:8]=='pointer_' and p[1].name=='unaryop_deref':
			p[0].type = p[2].type[8:]
			p[0].size = size[p[0].type]
			p[0].place = 'value(' + p[2].place + ')'
		elif p[1].name=='unaryop_ref':
			p[0].type='pointer_'+p[2].type
			p[0].size = 8
			p[0].place = 'addr(' + p[2].place + ')'
		else :
			p[0].type = p[2].type
			p[0].size = p[2].size
	p[0].name = 'unary_expression'
		
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
	p[0].name = 'unary_operator'
	if p[1]=='&':
		p[0].name='unaryop_ref'
	elif p[1]=='*':
		p[0].name='unaryop_deref'
#done
	
def p_cast_expression(p):
	'''
	cast_expression : unary_expression
					| OP type_name CP cast_expression
	'''
	global instr
	if len(p)==2:
		p[0] = p[1]
		p[0].type = p[1].type
		p[0].size = p[1].size
		p[0].place = p[1].place
		p[0].truelist = []
		p[0].falselist = []
		p[0].ret = p[1].ret
	else:
		p[0] = p[4]
		if(p[4].type[0:8]=='pointer_'):
			p[0].type = p[2].type 
			p[0].size = p[2].size
			if(p[4].type != 'TYPE_ERROR'):
				messages.add(f'Warning at line {p.lineno(1)} : Casting from {p[4].type} to {p[2].type} ', "warning")
		else :
			p[0].type = p[2].type
			p[0].size = p[2].size
		x = 'to_' + p[2].type.lower()
		p[0].place = newvar(p[2].type) 
		instr.append(p[0].place + ' = ' + x + '(' + p[4].place + ')')
		p[0].truelist = []
		p[0].falselist = []
		
	p[0].name = 'cast_expression'

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
	global instr
	if len(p)==2:
		p[0] = p[1]
		p[0].type = p[1].type
		p[0].size = p[1].size
		p[0].place = p[1].place
		p[0].truelist = []
		p[0].falselist = []
		p[0].ret = p[1].ret
	elif p[1]=='(':
		p[0] = p[2]
		p[0].type = p[2].type
		p[0].size = p[2].size
		p[0].place = p[2].place
		p[0].truelist = []
		p[0].falselist = []
	elif p[2]=='%':
		p[0] = Node("unary_expression", [p[1],p[3]], p[2])
		if(p[1].type[0:8] == 'pointer_' or p[3].type[0:8] == 'pointer_'):
			p[0].type = 'TYPE_ERROR'
			p[0].size = 0
			messages.add(f'Error at line {p.lineno(2)} : Invalid type of operands with {p[2]} operator')
		elif(p[1].type == 'FLOAT' or p[3].type == 'FLOAT'):
			p[0].type = 'TYPE_ERROR'
			p[0].size = 0
			messages.add(f'Error at line {p.lineno(2)} : Invalid type of operands with {p[2]} operator')
		else:
			if(p[1].type != 'INT' and p[3].type != 'INT'):
				x = newvar('INT')
				instr.append(x + ' = ' + 'to_int' + '(' + p[1].place + ')')
				y = newvar('INT')
				instr.append(y + ' = ' + 'to_int' + '(' +  p[3].place + ')')
				p[0].place = newvar('INT')
				instr.append(p[0].place + ' = ' + x + ' '+ p[2] + ' ' + y)	
			elif(p[1].type != 'INT' and p[3].type == 'INT'):
				x = newvar('INT')
				instr.append(x + ' = ' + 'to_int' + '(' +  p[1].place + ')')
				p[0].place = newvar('INT')
				instr.append(p[0].place + ' = ' + x + ' ' + p[2] + ' ' + p[3].place)
			elif(p[1].type == 'INT' and p[3].type != 'INT'):
				x = newvar('INT')
				instr.append(x + ' = ' + 'to_int' + '(' + p[3].place + ')')
				p[0].place = newvar('INT')
				instr.append(p[0].place + ' = ' + p[1].place + ' ' + p[2] + ' ' + x)
			else : 
				p[0].place = newvar('INT')
				instr.append(p[0].place + ' = ' + p[1].place + ' ' + p[2] + ' ' + p[3].place)	
			p[0].truelist = []
			p[0].falselist = []
			p[0].type = 'INT'
			p[1].type = 'INT'
			p[3].type = 'INT'
			p[0].size = 4
			p[1].size = 4
			p[3].size = 4
			
	else :
		p[0] = Node("unary_expression", [p[1],p[3]], p[2])
		if(p[1].type[0:8] == 'pointer_' or p[3].type[0:8] == 'pointer_'):
			p[0].type = 'TYPE_ERROR'
			p[0].size = 0
			messages.add(f'Error at line {p.lineno(2)} : Invalid type of operands with {p[2]} operator')
		elif(p[1].type == 'FLOAT' or p[3].type == 'FLOAT'):
			if(p[1].type != 'FLOAT' and p[3].type == 'FLOAT'):
				x = newvar('FLOAT')
				instr.append(x + ' = ' + 'to_float' + '(' + p[1].place + ')')
				p[0].place = newvar('FLOAT')
				instr.append(p[0].place + ' = ' + x + ' ' + p[2] + ' ' + p[3].place)
			elif(p[1].type == 'FLOAT' and p[3].type != 'FLOAT'):
				x = newvar('FLOAT')
				instr.append(x + ' = ' + 'to_float' + '(' + p[3].place + ')')
				p[0].place = newvar('FLOAT')
				instr.append(p[0].place + ' = ' + p[1].place + ' ' + p[2] + ' ' + x)
			else : 
				p[0].place = newvar('FLOAT')
				instr.append(p[0].place + ' = ' + p[1].place + ' ' + p[2] + ' ' + p[3].place)
			p[0].truelist = []
			p[0].falselist = []
			p[0].type = 'FLOAT'
			p[1].type = 'FLOAT'
			p[3].type = 'FLOAT'
			p[0].size = 4
			p[1].size = 4
			p[3].size = 4
		else:
			if(p[1].type != 'INT' and p[3].type != 'INT'):
				x = newvar('INT')
				instr.append(x + ' = ' + 'to_int' + '(' + p[1].place + ')')
				y = newvar('INT')
				instr.append(y + ' = ' + 'to_int' + '(' + p[3].place + ')')
				p[0].place = newvar('INT')
				instr.append(p[0].place + ' = ' + x + ' ' + p[2] + ' ' + y)	
			elif(p[1].type != 'INT' and p[3].type == 'INT'):
				x = newvar('INT')
				instr.append(x + ' = ' + 'to_int' + '(' + p[1].place + ')')
				p[0].place = newvar('INT')
				instr.append(p[0].place + ' = ' + x + ' ' + p[2] + ' ' + p[3].place)
			elif(p[1].type == 'INT' and p[3].type != 'INT'):
				x = newvar('INT')
				instr.append(x + ' = ' + 'to_int' + '(' + p[3].place + ')')
				p[0].place = newvar('INT')
				instr.append(p[0].place + ' = ' + p[1].place + ' ' + p[2] + ' ' + x)
			else : 
				p[0].place = newvar('INT')
				instr.append(p[0].place + ' = ' + p[1].place + ' ' + p[2] + ' ' + p[3].place)
			p[0].truelist = []
			p[0].falselist = []
			p[0].type = 'INT'
			p[1].type = 'INT'
			p[3].type = 'INT'
			p[0].size = 4
			p[1].size = 4
			p[3].size = 4
	p[0].name = 'multiplicative_expression'

def p_additive_expression(p):
	'''
	additive_expression : multiplicative_expression 
						| additive_expression ADD multiplicative_expression
						| additive_expression SUBTRACT multiplicative_expression
	'''
	global instr
	if len(p)==2:
		p[0] = p[1]
		p[0].type = p[1].type
		p[0].size = p[1].size
		p[0].place = p[1].place
		p[0].truelist = p[1].truelist
		p[0].falselist = p[1].falselist
		p[0].ret = p[1].ret
	else:
		p[0] = Node("additive_expression", [p[1],p[3]], p[2])
		if(p[1].type[0:8] == 'pointer_' or p[3].type[0:8] == 'pointer_'):
			p[0].type = 'TYPE_ERROR'
			p[0].size = 0
			messages.add(f'Error at line {p.lineno(2)} : Invalid type of operands with {p[2]} operator')
		elif(p[1].type == 'FLOAT' or p[3].type == 'FLOAT'):
			if(p[1].type != 'FLOAT' and p[3].type == 'FLOAT'):
				x = newvar('FLOAT')
				instr.append(x + ' = ' + 'to_float' + '(' +  p[1].place + ')')
				p[0].place = newvar('FLOAT')
				instr.append(p[0].place + ' = ' + x + ' '  + p[2] + ' ' + p[3].place)
			elif(p[1].type == 'FLOAT' and p[3].type != 'FLOAT'):
				x = newvar('FLOAT')
				instr.append(x + ' = ' + 'to_float' + '(' +  p[3].place + ')')
				p[0].place = newvar('FLOAT')
				instr.append(p[0].place + ' = ' + p[1].place + ' ' + p[2] + ' ' + x)
			else : 
				p[0].place = newvar('FLOAT')
				instr.append(p[0].place + ' = ' + p[1].place + ' ' + p[2] + ' ' + p[3].place)
			p[0].truelist = []
			p[0].falselist = []
			p[0].type = 'FLOAT'
			p[1].type = 'FLOAT'
			p[3].type = 'FLOAT'
			p[0].size = 4
			p[1].size = 4
			p[3].size = 4
		else:
			if(p[1].type != 'INT' and p[3].type != 'INT'):
				x = newvar('INT')
				instr.append(x + ' = ' + 'to_int' + '(' +  p[1].place + ')')
				y = newvar('INT')
				instr.append(y + ' = ' + 'to_int' + '(' +  p[3].place + ')')
				p[0].place = newvar('INT')
				instr.append(p[0].place + ' = ' + x + ' ' + p[2] + ' ' + y)	
			elif(p[1].type != 'INT' and p[3].type == 'INT'):
				x = newvar('INT')
				instr.append(x + ' = ' + 'to_int' + '(' +  p[1].place + ')')
				p[0].place = newvar('INT')
				instr.append(p[0].place + ' = ' + x + ' ' + p[2] + ' ' + p[3].place)
			elif(p[1].type == 'INT' and p[3].type != 'INT'):
				x = newvar('INT')
				instr.append(x + ' = ' + 'to_int' + '(' +  p[3].place + ')')
				p[0].place = newvar('INT')
				instr.append(p[0].place + ' = ' + p[1].place + ' ' + p[2] + ' ' + x)
			else : 
				p[0].place = newvar('INT')
				instr.append(p[0].place + ' = ' + p[1].place + ' ' + p[2] + ' ' + p[3].place)
			p[0].truelist = []
			p[0].falselist = []
			p[0].type = 'INT'
			p[1].type = 'INT'
			p[3].type = 'INT'
			p[0].size = 4
			p[1].size = 4
			p[3].size = 4
	p[0].name = 'additive_expression'

def p_shift_expression(p):
	'''
	shift_expression : additive_expression
					| shift_expression LSHIFT additive_expression
					| shift_expression RSHIFT additive_expression
	'''
	global instr
	if len(p)==2:
		p[0] = p[1]
		p[0].type = p[1].type
		p[0].size = p[1].size
		p[0].place = p[1].place
		p[0].truelist = p[1].truelist
		p[0].falselist = p[1].falselist
		p[0].ret = p[1].ret
	else:
		p[0] = Node("shift_expression", [p[1],p[3]], p[2])
		if(p[1].type[0:8] == 'pointer_' or p[3].type[0:8] == 'pointer_'):
			p[0].type = 'TYPE_ERROR'
			p[0].size = 0
			messages.add(f'Error at line {p.lineno(2)} : Invalid type of operands with {p[2]} operator')
		elif(p[1].type == 'FLOAT' or p[3].type == 'FLOAT'):
			p[0].type = 'TYPE_ERROR'
			p[0].size = 0
			messages.add(f'Error at line {p.lineno(2)} : Invalid type of operands with {p[2]} operator')
		else:
			if(p[1].type != 'INT' and p[3].type != 'INT'):
				x = newvar('INT')
				instr.append(x + ' = ' + 'to_int' + '(' +  p[1].place + ')')
				y = newvar('INT')
				instr.append(y + ' = ' + 'to_int' + '(' + p[3].place + ')')
				p[0].place = newvar('INT')
				instr.append(p[0].place + ' = ' + x + ' ' + p[2] + ' ' + y)	
			elif(p[1].type != 'INT' and p[3].type == 'INT'):
				x = newvar('INT')
				instr.append(x + ' = ' + 'to_int' + '(' +  p[1].place + ')')
				p[0].place = newvar('INT')
				instr.append(p[0].place + ' = ' + x + ' ' + p[2] + ' ' + p[3].place)
			elif(p[1].type == 'INT' and p[3].type != 'INT'):
				x = newvar('INT')
				instr.append(x + ' = ' + 'to_int' + '(' +  p[3].place + ')')
				p[0].place = newvar('INT')
				instr.append(p[0].place + ' = ' + p[1].place + ' ' + p[2] + ' ' + x)
			else : 
				p[0].place = newvar('INT')
				instr.append(p[0].place + ' = ' + p[1].place + ' ' + p[2] + ' ' + p[3].place)	
			p[0].truelist = []
			p[0].falselist = []
			p[0].type = 'INT'
			p[1].type = 'INT'
			p[3].type = 'INT'
			p[0].size = 4
			p[1].size = 4
			p[3].size = 4
	p[0].name = 'shift_expression'

def p_relational_expression(p):
	'''
	relational_expression : shift_expression
							| relational_expression LT shift_expression
							| relational_expression GT shift_expression
							| relational_expression LEQ shift_expression
							| relational_expression GEQ shift_expression
	'''
	global instr
	if len(p)==2:
		p[0] = p[1]
		p[0].type = p[1].type
		p[0].size = p[1].size
		p[0].place = p[1].place
		p[0].truelist = []
		p[0].falselist = []
		p[0].ret = p[1].ret
	else:
		p[0] = Node("relational_expression", [p[1],p[3]], p[2])
		if((p[1].type[0:8] == 'pointer_' and p[3].type[0:8] != 'pointer_') or (p[1].type[0:8] != 'pointer_' and p[3].type[0:8] == 'pointer_')):
			p[0].type = 'TYPE_ERROR'
			p[0].size = 0
			messages.add(f'Error at line {p.lineno(2)} : Comparison between different type of operands')
		else : 
			p[0].type = 'BOOL'
			p[0].size = 1
			if(p[1].place == None or p[3].place == None):
				messages.add(f'Error at line {p.lineno(2)} : Too complex expression to evaluate')
			p[0].place = None
			p[0].truelist = [len(instr)]
			p[0].falselist = [len(instr)+1]
			instr.append('if {' + p[1].place + ' ' + p[2] + ' ' + p[3].place + '}' + ' goto')
			instr.append('goto')
	p[0].name = 'relational_expression'

def p_equality_expression(p):
	'''
	equality_expression : relational_expression
						| equality_expression EQUAL relational_expression
						| equality_expression NEQ relational_expression
	'''
	global instr
	if len(p)==2:
		p[0] = p[1]
		p[0].type = p[1].type
		p[0].size = p[1].size
		p[0].place = p[1].place
		p[0].truelist = p[1].truelist
		p[0].falselist = p[1].falselist
		p[0].ret = p[1].ret
	else:
		p[0] = Node("equality_expression", [p[1],p[3]], p[2])
		if((p[1].type[0:8] == 'pointer_' and p[3].type[0:8] != 'pointer_') or (p[1].type[0:8] != 'pointer_' and p[3].type[0:8] == 'pointer_')):
			p[0].type = 'TYPE_ERROR'
			p[0].size = 0
			messages.add(f'Error at line {p.lineno(2)} : Comparison between different type of operands')
		else : 
			p[0].type = 'BOOL'
			p[0].size = 1
			if(p[1].place == None or p[3].place == None):
				messages.add(f'Error at line {p.lineno(2)} : Too complex expression to evaluate')
			p[0].place = None
			p[0].truelist = [len(instr)]
			p[0].falselist = [len(instr)+1]
			instr.append('if ' + p[1].place + ' ' + p[2] + ' ' + p[3].place + ' goto')
			instr.append('goto')
			
	p[0].name = 'equality_expression'

def p_and_expression(p):
	'''
	and_expression : equality_expression
					| and_expression B_AND equality_expression
	'''
	global instr
	if len(p)==2:
		p[0] = p[1]
		p[0].type = p[1].type
		p[0].size = p[1].size
		p[0].place = p[1].place
		p[0].truelist = p[1].truelist
		p[0].falselist = p[1].falselist
		p[0].ret = p[1].ret
	else:
		p[0] = Node("and_expression", [p[1],p[3]], p[2])
		if(p[1].type[0:8] == 'pointer_' or p[3].type[0:8] == 'pointer_'):
			p[0].type = 'TYPE_ERROR'
			p[0].size = 0
			messages.add(f'Error at line {p.lineno(2)} : Invalid type of operands with {p[2]} operator')	
		elif(p[1].type == 'FLOAT' or p[3].type == 'FLOAT'):
			p[0].type = 'TYPE_ERROR'
			p[0].size = 0
			messages.add(f'Error at line {p.lineno(2)} : Invalid type of operands with {p[2]} operator')	
		else:
			if(p[1].place == None or p[3].place == None):
				messages.add(f'Error at line {p.lineno(2)} : Too complex expression to evaluate')
			if(p[1].type != 'INT' and p[3].type != 'INT'):
				x = newvar('INT')
				instr.append(x + ' = ' + 'to_int' + p[1].place)
				y = newvar('INT')
				instr.append(y + ' = ' + 'to_int' + p[3].place)
				p[0].place = newvar('INT')
				instr.append(p[0].place + ' = ' + x + ' ' + p[2] + ' ' + y)	
			elif(p[1].type != 'INT' and p[3].type == 'INT'):
				x = newvar('INT')
				instr.append(x + ' = ' + 'to_int' + p[1].place)
				p[0].place = newvar('INT')
				instr.append(p[0].place + ' = ' + x + ' ' + p[2] + ' ' + p[3].place)
			elif(p[1].type == 'INT' and p[3].type != 'INT'):
				x = newvar('INT')
				instr.append(x + ' = ' + 'to_int' + p[3].place)
				p[0].place = newvar('INT')
				instr.append(p[0].place + ' = ' + p[1].place + ' ' + p[2] + ' ' + x)
			else : 
				p[0].place = newvar('INT')
				instr.append(p[0].place + ' = ' + p[1].place + ' ' + p[2] + ' ' + p[3].place)	
			p[0].truelist = []
			p[0].falselist = []
			p[0].type = 'INT'
			p[1].type = 'INT'
			p[3].type = 'INT'
			p[0].size = 4
			p[1].size = 4
			p[3].size = 4
	p[0].name = 'and_expression'
	
def p_exclusive_or_expression(p):
	'''
	exclusive_or_expression : and_expression
							| exclusive_or_expression XOR and_expression
	'''
	global instr
	if len(p)==2:
		p[0] = p[1]
		p[0].type = p[1].type
		p[0].size = p[1].size
		p[0].place = p[1].place
		p[0].truelist = p[1].truelist
		p[0].falselist = p[1].falselist
		p[0].ret = p[1].ret
		
	else:
		p[0] = Node("exclusive_or_expression", [p[1],p[3]], p[2])
		if(p[1].type[0:8] == 'pointer_' or p[3].type[0:8] == 'pointer_'):
			p[0].type = 'TYPE_ERROR'
			p[0].size = 0
			messages.add(f'Error at line {p.lineno(2)} : Invalid type of operands with {p[2]} operator')	
		elif(p[1].type == 'FLOAT' or p[3].type == 'FLOAT'):
			p[0].type = 'TYPE_ERROR'
			p[0].size = 0
			messages.add(f'Error at line {p.lineno(2)} : Invalid type of operands with {p[2]} operator')
		else:
			if(p[1].place == None or p[3].place == None):
				messages.add(f'Error at line {p.lineno(2)} : Too complex expression to evaluate')
			if(p[1].type != 'INT' and p[3].type != 'INT'):
				x = newvar('INT')
				instr.append(x + ' = ' + 'to_int' + p[1].place)
				y = newvar('INT')
				instr.append(y + ' = ' + 'to_int' + p[3].place)
				p[0].place = newvar('INT')
				instr.append(p[0].place + ' = ' + x + ' ' + p[2] + ' ' + y)	
			elif(p[1].type != 'INT' and p[3].type == 'INT'):
				x = newvar('INT')
				instr.append(x + ' = ' + 'to_int' + p[1].place)
				p[0].place = newvar('INT')
				instr.append(p[0].place + ' = ' + x + ' ' + p[2] + ' ' + p[3].place)
			elif(p[1].type == 'INT' and p[3].type != 'INT'):
				x = newvar('INT')
				instr.append(x + ' = ' + 'to_int' + p[3].place)
				p[0].place = newvar('INT')
				instr.append(p[0].place + ' = ' + p[1].place + ' ' + p[2] + ' ' + x)
			else : 
				p[0].place = newvar('INT')
				instr.append(p[0].place + ' = ' + p[1].place + ' ' + p[2] + ' ' + p[3].place)	
			p[0].truelist = []
			p[0].falselist = []
			p[0].type = 'INT'
			p[1].type = 'INT'
			p[3].type = 'INT'
			p[0].size = 4
			p[1].size = 4
			p[3].size = 4
	p[0].name = 'exclusive_or_expression'

def p_inclusive_or_expression(p):
	'''
	inclusive_or_expression : exclusive_or_expression
							| inclusive_or_expression B_OR exclusive_or_expression
	'''
	global instr
	if len(p)==2:
		p[0] = p[1]
		p[0].type = p[1].type
		p[0].size = p[1].size
		p[0].place = p[1].place
		p[0].truelist = p[1].truelist
		p[0].falselist = p[1].falselist
		p[0].ret = p[1].ret
	else:
		p[0] = Node("inclusive_or_expression", [p[1],p[3]], p[2])
		if(p[1].type[0:8] == 'pointer_' or p[3].type[0:8] == 'pointer_'):
			p[0].type = 'TYPE_ERROR'
			p[0].size = 0
			messages.add(f'Error at line {p.lineno(2)} : Invalid type of operands with {p[2]} operator')	
		elif(p[1].type == 'FLOAT' or p[3].type == 'FLOAT'):
			p[0].type = 'TYPE_ERROR'
			p[0].size = 0
			messages.add(f'Error at line {p.lineno(2)} : Invalid type of operands with {p[2]} operator')
		else:
			if(p[1].place == None or p[3].place == None):
				messages.add(f'Error at line {p.lineno(2)} : Too complex expression to evaluate')
			if(p[1].type != 'INT' and p[3].type != 'INT'):
				x = newvar('INT')
				instr.append(x + ' = ' + 'to_int' + p[1].place)
				y = newvar('INT')
				instr.append(y + ' = ' + 'to_int' + p[3].place)
				p[0].place = newvar('INT')
				instr.append(p[0].place + ' = ' + x + ' ' + p[2] + ' ' + y)	
			elif(p[1].type != 'INT' and p[3].type == 'INT'):
				x = newvar()
				instr.append(x + ' = ' + 'to_int' + p[1].place)
				p[0].place = newvar()
				instr.append(p[0].place + ' = ' + x + ' ' + p[2] + ' ' + p[3].place)
			elif(p[1].type == 'INT' and p[3].type != 'INT'):
				x = newvar('INT')
				instr.append(x + ' = ' + 'to_int' + p[3].place)
				p[0].place = newvar('INT')
				instr.append(p[0].place + ' = ' + p[1].place + ' ' + p[2] + ' ' + x)
			else : 
				p[0].place = newvar('INT')
				instr.append(p[0].place + ' = ' + p[1].place + ' ' + p[2] + ' ' + p[3].place)	
			p[0].truelist = []
			p[0].falselist = []
			p[0].type = 'INT'
			p[1].type = 'INT'
			p[3].type = 'INT'
			p[0].size = 4
			p[1].size = 4
			p[3].size = 4
	p[0].name = 'inclusive_or_expression'

def p_logical_and_expression(p):
	'''
	logical_and_expression : inclusive_or_expression
						   | logical_and_expression AND label_m inclusive_or_expression
	'''
	if len(p)==2:
		p[0] = p[1]
		p[0].type = p[1].type
		p[0].size = p[1].size
		p[0].place = p[1].place
		p[0].truelist = p[1].truelist
		p[0].falselist = p[1].falselist
		p[0].ret = p[1].ret
	else:
		p[0] = Node("logical_and_expression", [p[1],p[4]], p[2])
		p[0].type = 'BOOL'
		p[0].size = 1
		backpatch(p[1].truelist, p[3].quad)
		p[0].truelist = p[4].truelist
		p[0].falselist = p[1].falselist + p[4].falselist
		p[0].place = None
	p[0].name = 'logical_and_expression'

def p_label_m(p):
	'''
	label_m : 
	'''
	p[0] = Node("label_m", None, None)
	p[0].quad = len(instr)

def p_label_n(p):
	'''
	label_n :
	'''
	p[0] = Node("label_n", None, None) 
	p[0].nextlist = [len(instr)]
	instr.append('goto')

def p_logical_or_expression(p):
	'''
	logical_or_expression : logical_and_expression
						  | logical_or_expression OR label_m logical_and_expression
	'''
	if len(p)==2:
		p[0] = p[1]
		p[0].type = p[1].type
		p[0].size = p[1].size
		p[0].place = p[1].place
		p[0].truelist = p[1].truelist
		p[0].falselist = p[1].falselist
		p[0].ret = p[1].ret
	else:
		p[0] = Node("logical_or_expression", [p[1],p[4]], p[2])
		p[0].type = 'BOOL'
		p[0].size = 1
		backpatch(p[1].falselist, p[3].quad)
		p[0].truelist = p[1].truelist + p[4].truelist
		p[0].falselist = p[4].falselist
		p[0].place = None
	p[0].name = 'logical_or_expression'

def p_conditional_expression(p):
	'''
	conditional_expression : logical_or_expression
						   | logical_or_expression TERNARYOP expression COLON conditional_expression
	'''
	if len(p)==2:
		p[0] = p[1]
		p[0].type = p[1].type
		p[0].place = p[1].place
		p[0].truelist = p[1].truelist
		p[0].falselist = p[1].falselist
		p[0].ret = p[1].ret
	else:
		p[0] = Node("conditional_expression", [p[1],p[3],p[5]], '? :')
	p[0].name = 'conditional_expression'

def p_assignment_expression(p):
	'''
	assignment_expression : conditional_expression
						  | unary_expression assignment_operator assignment_expression    
	'''

	if len(p)==2:
		p[0] = p[1]
		p[0].type = p[1].type
		p[0].size = p[1].size
		p[0].place = p[1].place
		p[0].truelist = p[1].truelist
		p[0].falselist = p[1].falselist
		p[0].ret = p[1].ret
	else:
		p[0] = Node("assignment_expression", [p[1],p[3]], p[2])
		if(p[1].place == None or p[3].place == None):
				messages.add(f'Error at line {p.lineno(2)} : Too complex expression to evaluate')
		if(p[1].type != p[3].type and p[1].type != 'EMPTY'):
			messages.add(f'Warning at line {p.lineno(2)} : Casting from {p[3].type} to {p[1].type} ', "warning")
			x = newvar(p[1].type)
			instr.append(x + ' = ' + 'to_' + p[1].type.lower() + '(' + p[3].place + ')')
			instr.append(p[1].place + ' ' + p[2].type + ' ' + x)
			p[0].type = p[1].type
			p[3].type = p[1].type
			p[0].size = p[1].size
			p[3].size = p[1].size
		else :
			p[0].type = p[1].type
			p[3].type = p[1].type
			p[0].size = p[1].size
			p[3].size = p[1].size
			instr.append(p[1].place + ' ' + p[2].type + ' ' + p[3].place)
		p[0].place = None
		p[0].truelist = []
		p[0].falselist = []
	p[0].name = 'assignment_expression'

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
	p[0].type = p[1]
	p[0].name = 'assignment_operator'
#done
	
def p_expression(p):
	'''
	expression : assignment_expression
			   | expression COMMA assignment_expression
	'''
	if len(p)==2:
		p[0] = p[1]
		p[0].type = p[1].type
		p[0].size = p[1].size
		p[0].place = p[1].place
		p[0].truelist = p[1].truelist
		p[0].falselist = p[1].falselist
		p[0].ret = p[1].ret
	else:
		p[0] = Node("expression", [p[1],p[3]], None)
		if(p[1].type != p[3].type):
			p[0].type = 'TYPE_ERROR'
			p[0].size = 0
			messages.add(f'Error at line {p.lineno(2)} : Type mismatch')
		else:
			p[0].type = p[1].type
			p[0].size = p[1].size
	p[0].name = 'expression'

def p_constant_expression(p):
	'''
	constant_expression : conditional_expression
	'''
	p[0] = p[1]
	p[0].name = 'constant_expression'
	p[0].type = p[1].type
	p[0].size = p[1].size
	p[0].place = p[1].place
	p[0].truelist = p[1].truelist
	p[0].falselist = p[1].falselist
	p[0].ret = p[1].ret

def p_declaration(p):
	'''
	declaration : declaration_specifiers SEMICOLON
				| declaration_specifiers init_declarator_list SEMICOLON
	'''
	if len(p)==3:
		p[0] = p[1]
		p[0].nextlist = []
	else:
		p[0] = Node("declaration", [p[1],p[2]], None)
		for i in range(0,len(p[2].variables)):
			if p[2].types_of_var[i] == 'EMPTY':
				#print("-",p[2].variables[i],p[2].types_of_var[i],p[1].type)
				if st.var_curr_scope_exists(p[2].variables[i]):
					messages.add(f'Error at line {p.lineno(2)}: Redeclaration')
				else:
					if p[2].values_of_var[i]==None:
						st.make_var_entry(p[2].variables[i],p[1].type,False,None)
					else:
						st.make_var_entry(p[2].variables[i],p[1].type,True,p[2].values_of_var[i])
				p[2].types_of_var[i] = p[1].type

			elif p[2].types_of_var[i][0:8]=='pointer_':
				#Pointer of unknown type
				if p[2].types_of_var[i][-8:]=='pointer_':
					if st.var_curr_scope_exists(p[2].variables[i]):
						messages.add(f'Error at line {p.lineno(2)}: Redeclaration')
					else:
						if p[2].values_of_var[i]==None:
							st.make_var_entry(p[2].variables[i],p[2].types_of_var[i]+p[1].type,False,None)
						else:
							st.make_var_entry(p[2].variables[i],p[2].types_of_var[i]+p[1].type,True,p[2].values_of_var[i])
					p[2].types_of_var[i]=p[2].types_of_var[i]+p[1].type

				elif p[2].types_of_var[i][-len(p[1].type):]==p[1].type:#Pointer type matched
					if st.var_curr_scope_exists(p[2].variables[i]):
						messages.add(f'Error at line {p.lineno(2)}: Redeclaration')
					else:
						if p[2].values_of_var[i]==None:
							st.make_var_entry(p[2].variables[i],p[2].types_of_var[i],False,None)
						else:
							st.make_var_entry(p[2].variables[i],p[2].types_of_var[i],True,p[2].values_of_var[i])
				else:
					#print(p[2].variables[i],p[2].types_of_var[i])
					messages.add(f'Error at line {p.lineno(2)}: TYPE ERROR IN POINTER DECLARATION')

			elif isinstance(p[2].types_of_var[i] , list):# Array
				p[2].types_of_var[i].append(p[1].type)
				if st.var_curr_scope_exists(p[2].variables[i]):
					messages.add(f'Error at line {p.lineno(2)}: Redeclaration')
				else:
					st.make_var_entry(p[2].variables[i],p[2].types_of_var[i],False,None)

			elif p[1].type!=p[2].types_of_var[i]:
				messages.add(f'Error at line {p.lineno(2)}: TYPE ERROR IN DECLARATION')
				#print("-",p[2].variables[i],p[2].types_of_var[i],p[1].type)
				if st.var_curr_scope_exists(p[2].variables[i]):
					messages.add(f'Error at line {p.lineno(2)}: Redeclaration')
			else:
				if st.var_curr_scope_exists(p[2].variables[i]):
					messages.add(f'Error at line {p.lineno(2)}: Redeclaration')
				else:
						if p[2].values_of_var[i]==None:
							st.make_var_entry(p[2].variables[i],p[1].type,False,None)
						else:
							st.make_var_entry(p[2].variables[i],p[1].type,True,p[2].values_of_var[i])
		p[0].type=p[1].type
		p[0].nextlist = []
	p[0].name = 'declaration'


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
		func_type_list.append(p[1].type)
		#p[0].type = p[1].type
	else:
		p[0] = Node("declaration_specifiers", [p[1],p[2]], None)
		#p[0].type += p[1].type
		#p[0].type += p[2].type
	p[0].name = 'declaration_specifiers'
		
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
		p[0].values_of_var = p[1].values_of_var
		p[0].values_of_var.append(p[3].value)
	else:
		p[0] = p[1]
		p[0].values_of_var.append(p[1].value)
	p[0].name = 'init_declarator_list'	

def p_init_declarator(p):
	'''
	init_declarator : declarator
					| declarator ASSIGN initializer
	'''
	if (len(p)==4):
		p[0] = Node("init_declarator", [p[1],p[3]], p[2])
		p[0].value = p[3].value
		instr.append(p[1].place + ' = ' + p[3].place)
		# Pointer error eg : int **x=y; y is int*
		if isinstance(p[1].type,list):
			if  p[1].type[1]!=int(p[3].name[-1]):
				messages.add(f'Error at line {p.lineno(1)}: Array declaration dimension not matched')
		elif isinstance(p[3].type,list):#pointer initialized to array name
			if p[1].type.count('_')!=p[3].type[1]:#Dimension of pointer and array not matched
				messages.add(f'Error at line {p.lineno(1)}: Dimension of pointer and array pointer not matched')
			else:
				p[1].type = p[1].type+p[3].type[2]# pointer_INT eg.
		elif p[1].type.count('_')>0 and p[1].type.count('_')!=p[3].type.count('_'):
			messages.add(f'Error at line {p.lineno(1)}: POINTER TYPE ERROR {p[1].type} {p[3].type}')
		else:
			p[1].type = p[3].type
		p[0].type = p[1].type #Inherited
		# Add the actual type of ID 
		#st.make_var_entry(p[1].variables[0],p[0].type)
		p[1].types_of_var[0] = p[0].type
		p[0].variables.append(p[1].variables[0])
		p[0].types_of_var.append(p[1].types_of_var[0])
	else:
		p[0] = p[1]
		if isinstance(p[1].type,list)!=True and p[1].type[:8]!='pointer_' :#NOt pointer and not array
			p[1].type='EMPTY'
		p[0].type=p[1].type
		
	if len(func_type_list)>0:
		func_type_list.pop()
	p[0].name = 'init_declarator'

def p_storage_class_specifier(p):
	'''
	storage_class_specifier : TYPEDEF
							| EXTERN
							| STATIC
							| AUTO
							| REGISTER
	'''
	p[0] = None
	p[0].name = 'storage_class_specifier'
		#p[0].other[p[1]] = 1
#done
		
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
	else:
		p[0] = p[1]
	p[0].name = 'type_specifier'
	
	if (p[1]=='void' or p[1]=='char' or p[1]=='short' or p[1]=='int' or p[1]=='long' or p[1]=='float' or p[1]=='double'):
		p[0].type = p[1].upper()
	#elif(p[1]=='SIGNED' or p[1]=='UNSIGNED' or p[1]=='TYPE_NAME'):
		#p[0].other[p[1]] = 1
	else:
		p[0].type = p[1].type
#done

def p_struct_or_union_specifier(p):
	'''
	struct_or_union_specifier : struct_or_union ID ocp struct_declaration_list ccp
							  | struct_or_union OCP struct_declaration_list CCP
							  | struct_or_union ID
	'''
	if len(p)==3:
		p[0] = Node("struct_or_union", [p[1]], p[2])
		if st.check_in_structures(p[2])==None:
			messages.add(f'Error at line {p.lineno(2)}: UNDECLARED structure/union')
	elif len(p)==5:
		p[0] = Node("struct_or_union_specifier", [p[1],p[3]], None)
	else:
		p[0] = Node("struct_or_union_specifier", [p[1],p[2],p[4]], 'struct/union')
		if st.struct_union_exists(p[2]):
			messages.add(f'Error at line {p.lineno(2)}: Structure/Union Redeclaration')
		else:
			st.make_struct_entry(p[2])
	p[0].name = 'struct_or_union_specifier'

def p_struct_or_union(p):
	'''
	struct_or_union : STRUCT
					| UNION
	'''
	p[0] = Node("struct_or_union")
	p[0].name = 'struct_or_union'

def p_struct_declaration_list(p):
	'''
	struct_declaration_list : struct_declaration
							| struct_declaration_list struct_declaration
	'''
	if (len(p)==2):
		p[0] = p[1]
	else:
		p[0] = Node("struct_declaration_list", [p[1],p[2]], None)
	p[0].name = 'struct_declaration_list'

def p_struct_declaration(p):
	'''
	struct_declaration : specifier_qualifier_list struct_declarator_list SEMICOLON
	'''
	p[0] = Node("struct_declaration", [p[1],p[2]], None)
	for x in p[2].variables:
		if st.var_curr_scope_exists(x):
			messages.add(f'Error at line {p.lineno(2)}: Redeclaration')
		else:
			st.make_var_entry(x,p[1].type,False,None)
	p[0].type=p[1].type
	p[0].name = 'struct_declaration'

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
	p[0].name = 'specifier_qualifier_list'
	
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
	p[0].name = 'struct_declarator_list'
		
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
	p[0].name = 'struct_declarator'

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
	p[0].name = 'enum_specifier'

def p_enumerator_list(p):
	'''
	enumerator_list : enumerator
					| enumerator_list COMMA enumerator
	'''
	if (len(p)==4):
		p[0] = Node("enumerator_list", [p[1],p[3]], None)
	else:
		p[0] = Node("enumerator_list", [p[1]], None)
	p[0].name = 'enumerator_list'

def p_enumerator(p):
	'''
	enumerator : ID
			   | ID ASSIGN constant_expression
	'''
	if (len(p)==4):
		p[0] = Node("enumerator", [p[1],p[3]], p[2])
		
	else:
		p[0] = Node("enumerator", [p[1]], None)
		#p[0].dict(typ) = 'void'
	p[0].name = 'enumerator'

def p_type_qualifier(p):
	'''
	type_qualifier : CONST
				   | VOLATILE
	'''
	p[0] = Node('type_qualifier')
	p[0].name = p[1]
	#if(p[1] == 'CONST'):
			#p[0].other['CONSTANT'] = 1

def p_declarator(p):
	'''
	declarator : pointer direct_declarator
			   | direct_declarator
	'''
	global func_name
	if (len(p)==3):
		p[0] = Node("declarator", [p[1],p[2]], None)
		p[0].type = p[1].type
		p[0].place = p[2].place
		p[0].variables=p[2].variables
		p[0].types_of_var.append(p[0].type)
		func_name = p[0].variables[0]
	else:
		p[0] = p[1]
		p[0].place = p[1].place
		func_name = p[0].variables[0]
	p[0].name = 'declarator'
		
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
		p[0].type = 'EMPTY'
		p[0].place = p[1]
		p[0].variables.append(p[1])
		p[0].types_of_var.append('EMPTY')
	elif p[1]=='(':
		p[0] = p[2]
	elif (len(p)==4):
		p[0] = p[1]
		if p[2]=='[':#Array, unknown length
			if isinstance(p[1].type,list): #Already an array, dimension increasing
				p[0].type = p[1].type
				p[0].type[1]+=1
			else:
				p[0].type = ['array',1]
			messages.add(f'Error at line {p.lineno(2)}: size unknown')
			p[0].types_of_var[-1]=p[0].type
	elif (len(p)==5):
		p[0] = Node("direct_declarator", [p[3]], p[1]) #CHECKK Direct decl made leaf so that param_type_list, id_list can attatch to that node
		if p[2]=='(': # Making function variable entry
			# Add all the info in the list. Make function and params/ids i.e args entry in symtab in p_func_def
			p[0].variables=p[1].variables
			p[0].types_of_var=p[1].types_of_var
			p[0].variables+=p[3].variables
			p[0].types_of_var+=p[3].types_of_var
			# FOR func decl case, i.e f(int a, int b)
			for x in p[1].variables:
				if len(func_type_list)>0:
					func_type_list.pop()
		elif p[2]=='[':
			if p[3].type!='INT' and p[3].type!='FLOAT' and p[3].type!='CHAR':
				messages.add(f'Error at line {p.lineno(2)}: Array index not integer')
			if isinstance(p[1].type,list): #Already an array, dimension increasing
				p[0].type = p[1].type
				p[0].type[1]+=1
				if isinstance(p[3].value,int):
					p[0].type[2].append(p[3].value)
			else:
				p[0].type = ['array',1]
				if isinstance(p[3].value,int):
					p[0].type.append([p[3].value])
			p[0].variables=p[1].variables
			p[0].types_of_var.append(p[0].type)

	p[0].name = 'direct_declarator'
		

def p_pointer(p):
	'''
	pointer : MULTIPLY
			| MULTIPLY type_qualifier_list
			| MULTIPLY pointer
			| MULTIPLY type_qualifier_list pointer
	'''
	if (len(p)==2):
		p[0] = Node("pointer", None, p[1])
		p[0].type='pointer_'
	elif (len(p)==3):
		p[0] = Node("pointer", [p[2]], p[1])
		if p[2].type[:8]=='pointer_':
			p[0].type=p[2].type+'pointer_'
	else:
		p[0] = Node("pointer", [p[2],p[3]], p[1])
	p[0].name = 'pointer'


def p_type_qualifier_list(p):
	'''
	type_qualifier_list : type_qualifier
						| type_qualifier_list type_qualifier
	'''
	if (len(p)==3):
		p[0] = Node("type_qualifier_list", [p[1],p[2]], None)
		if(p[1].other['CONSTANT'] == 1 or p[2].other['CONSTANT'] == 1):
					p[0].other['CONSTANT'] = 1
	else:
		p[0] = p[1]
		if(p[1].other['CONSTANT'] == 1):
			p[0].other['CONSTANT'] = 1
	p[0].name = 'type_qualifier_list'
#done

def p_parameter_type_list(p):
	'''
	parameter_type_list : parameter_list
						| parameter_list COMMA ELLIPSIS
	'''
	if (len(p)==4):
		p[0] = Node("parameter_type_list", p[1],  p[3])
	else:
		p[0] = p[1]
		st.add_function_params(p[1].variables,p[1].types_of_var)
	p[0].name = 'parameter_type_list'

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
	p[0].name = 'parameter_list'

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
	p[0].name = 'parameter_declaration'

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
		p[0].types_of_var.append('EMPTY')
	else:
		p[0] = Node("identifier_list", None, p[1])
		p[0].variables.append(p[1])
		p[0].types_of_var.append('EMPTY')
	p[0].name = 'identifier_list'
#done

def p_type_name(p):
	'''
	type_name : specifier_qualifier_list
			  | specifier_qualifier_list abstract_declarator
	'''
	if (len(p)==3):
		p[0] = Node("type_name", [p[1],p[2]], None)
	else:
		p[0] = p[1]
	p[0].name = 'type_name'

def p_abstract_declarator(p):
	'''
	abstract_declarator : pointer
						| direct_abstract_declarator
						| pointer direct_abstract_declarator
	'''
	if (len(p)==3):
		p[0] = Node("abstract_declarator", [p[1],p[2]], None)
	else:
		p[0] = p[1]
	p[0].name = 'abstract_declarator'

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
		p[0] = Node("direct_abstract_declarator", [p[3]], p[1]) #CHECKK p[1] made child coz of list
	elif (p[1]=='(' or p[1]=='['):
		p[0] = p[2]
	else:
		p[0] = p[1]
	p[0].name = 'direct_abstract_declarator'

def p_initializer(p):
	'''
	initializer : assignment_expression
				| OCP initializer_list CCP
				| OCP initializer_list COMMA CSP
	'''
	if len(p)==5:
		p[0] = Node('initializer', [p[2]],p[3])
		p[0].type = p[2].type
		p[0].place = p[2].place
		p[0].truelist = p[2].truelist
		p[0].falselist = p[2].falselist
		p[0].name = 'initializer'
	elif len(p)==4:
		p[0] = p[2]
		p[0].type = p[2].type
		if p[2].name.find('curly')!=-1:
			p[0].name=p[2].name[:-1]+str(int(p[2].name[-1])+1)
		else:
			p[0].name = 'initializer_curly_brace_1'
	else:
		p[0] = p[1]
		p[0].type = p[1].type
		p[0].place = p[1].place
		p[0].truelist = p[1].truelist
		p[0].falselist = p[1].falselist
		p[0].name = 'initializer'
		
def p_initializer_list(p):
	'''
	initializer_list : initializer
					 | initializer_list COMMA initializer
	'''
	if len(p)==2:
		p[0] = p[1]
		p[0].type = p[1].type
		p[0].place = p[1].place
		p[0].truelist = p[1].truelist
		p[0].falselist = p[1].falselist
		if p[1].name.find('curly')==-1:
			p[0].name = 'initializer_list'
	else:
		p[0] = Node('initializer_list',[p[1],p[3]],None)
		p[0].name = p[1].name
		p[0].type = p[1].type
		if p[1].name.find('curly')!=-1 or p[3].name.find('curly')!=-1:#Dimension Type checking for array initializers
			if p[1].name!=p[3].name:
				messages.add(f'Error at line {p.lineno(2)}: Dimension of elements in initializer list not matched')
		if p[1].type!=p[3].type:
			messages.add(f'Error at line {p.lineno(2)}: List elements type not consistent')

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
	p[0].name = 'statement'
	p[0].type= p[1].type
	p[0].nextlist = p[1].nextlist
	p[0].breaklist = p[1].breaklist
	p[0].continuelist = p[1].continuelist
	p[0].returnlist = p[1].returnlist

def p_labeled_statement(p):
	'''
	labeled_statement : ID COLON statement
					  | CASE constant_expression COLON statement
					  | DEFAULT COLON statement
	'''
	if len(p) == 4:
		if p[1] == 'default':
			p[0] = Node('labeled-stmt-default', [p[3]])
			p[0].type = p[3].type
		else:
			p[0] = Node('labeled-stmt-normal', [p[1], p[3]])
			st.add_label(p[1],p.lineno(1))
			p[0].type = p[3].type

	elif len(p) == 5:
		p[0] = Node('labeled-stmt-case', [p[2], p[4]])
		p[0].type = p[4].type
	p[0].name = 'labeled_statement'

def p_compound_statement(p):
	'''
	compound_statement : OCP CCP
					   | ocp statement_list ccp
					   | ocp declaration_list ccp
					   | ocp declaration_list label_m statement_list ccp
	'''
	if len(p)==4:
		p[0] = Node('compound_statement',[p[2]],'{}')
		p[0].type = p[2].type
		p[0].nextlist = p[2].nextlist
		p[0].breaklist = p[2].breaklist
		p[0].continuelist = p[2].continuelist
		p[0].returnlist = p[2].returnlist
		
	elif len(p)==6:
		p[0] = Node('compound_statement',[p[2],p[4]],'{}')
		if (p[4].type == 'TYPE_ERROR' or p[2].type == 'TYPE_ERROR'):
			p[0].type = 'TYPE_ERROR'
		else:
			p[0].type = 'VOID'
		p[0].nextlist = p[4].nextlist
		p[0].breaklist = p[4].breaklist
		p[0].continuelist = p[4].continuelist
		p[0].returnlist = p[4].returnlist
		backpatch(p[2].nextlist, p[3].quad)
	else:
		p[0]=None
		p[0].type = 'VOID'
	p[0].name = 'compound_statement'

def p_ocp(p):
	'''
	ocp : OCP
	'''
	st.newscope()

def p_ccp(p):
	'''
	ccp : CCP
	'''
	st.endscope()

def p_declaration_list(p):
	'''
	declaration_list : declaration
					 | declaration_list label_m declaration
	'''
	if len(p) == 2:
		p[0] = p[1]
		p[0].type = p[1].type
		p[0].nextlist = []
	else:
		p[0] = Node('decl-list', [p[1], p[3]])
		if (p[1].type == 'TYPE_ERROR' or p[3].type == 'TYPE_ERROR'):
			p[0].type = 'TYPE_ERROR'
		else:
			p[0].type = 'VOID'
		p[0].nextlist = []
	p[0].name = 'declaration_list'

def p_statement_list(p):
	'''
	statement_list : statement
				   | statement_list label_m statement
	'''
	if len(p) == 2:
		p[0] = Node('stmt', [p[1]])
		p[0].type = p[1].type
		p[0].nextlist = p[1].nextlist
		p[0].breaklist = p[1].breaklist
		p[0].continuelist = p[1].continuelist
		p[0].returnlist = p[1].returnlist
		
	else:
		p[0] = Node('stmt-list', [p[1], p[3]])
		if (p[1].type == 'TYPE_ERROR' or p[3].type == 'TYPE_ERROR'):
			p[0].type = 'TYPE_ERROR'
		else:
			p[0].type = 'VOID'
		p[0].nextlist = p[3].nextlist
		backpatch(p[1].nextlist, p[2].quad)
		p[0].breaklist = p[1].breaklist + p[3].breaklist
		p[0].continuelist = p[1].continuelist + p[3].continuelist
		p[0].returnlist = p[1].returnlist + p[3].returnlist
	p[0].name = 'statement_list'

def p_expression_statement(p):
	'''
	expression_statement : SEMICOLON
						 | expression SEMICOLON
	'''
	if len(p) == 3:
		p[0] = Node('expr-stmt', [p[1]], None)
		if(p[1].type == 'TYPE_ERROR'):
			p[0].type = 'TYPE_ERROR'
		else : 
			p[0].type = 'VOID'
	else:
		p[0] = Node('exr-stmt')
	p[0].nextlist = []
	p[0].name = 'expression_statement'
	

def p_selection_statement(p):
	'''
	selection_statement : IF OP expression CP label_m statement
						| IF OP expression CP label_m statement label_n ELSE label_m statement
						| SWITCH OP expression CP statement
	'''
	if (len(p) == 7):
		p[0] = Node('if-then', [p[3], p[6]], "if")
		p[0].type = p[6].type               
		backpatch(p[3].truelist, p[5].quad)
		p[0].nextlist = p[3].falselist + p[6].nextlist
		p[0].breaklist = p[6].breaklist 	
		p[0].continuelist = p[6].continuelist
		p[0].returnlist = p[6].returnlist
		
	elif (len(p) == 6):
		p[0] = Node('switch', [p[3], p[5]], 'switch')
		p[0].type = p[5].type
			
	elif (len(p) == 11):
		p[0] = Node('if-then-else', [p[3], p[6], p[10]], "if-then-else")
		if (p[6].type == 'TYPE_ERROR' or p[10].type == 'TYPE_ERROR'):
			p[0].type = 'TYPE_ERROR'
		else:
			p[0].type = 'VOID'
		backpatch(p[3].truelist, p[5].quad)
		backpatch(p[3].falselist, p[9].quad)
		p[6].nextlist = p[6].nextlist + p[7].nextlist
		p[7].nextlist = p[6].nextlist
		p[0].nextlist = p[6].nextlist + p[10].nextlist
		p[0].breaklist = p[6].breaklist + p[10].breaklist
		p[0].continuelist = p[6].continuelist + p[10].continuelist
		p[0].returnlist = p[6].returnlist + p[10].returnlist
		
	p[0].name = 'selection_statement'

def p_emp_expression(p) : 
	'''
	emp_expression : 
			| expression
	'''
	
	if(len(p) == 1) :
		p[0] = Node("emp_expr", None , None)
	else : 
		p[0] = p[1]
	
def p_iteration_statement(p):
	'''
	iteration_statement : WHILE OP label_m expression CP label_m statement label_n
						| DO label_m statement label_n WHILE OP label_m expression CP SEMICOLON
						| FOR OP emp_expression SEMICOLON label_m emp_expression SEMICOLON label_m emp_expression label_n CP label_m statement label_n
	'''
	if len(p) == 9:
		p[0] = Node('while', [p[4], p[7]], 'while')
		p[0].type = p[7].type
		p[8].nextlist = p[7].nextlist + p[8].nextlist + p[7].continuelist
		p[7].nextlist = p[8].nextlist
		backpatch(p[7].nextlist, p[3].quad)
		backpatch(p[4].truelist, p[6].quad)
		p[0].nextlist = p[4].falselist + p[7].breaklist
		p[0].returnlist = p[7].returnlist
	
	elif len(p) == 11:
		p[0] = Node('do-while', [p[3], p[8]], 'do-while')
		p[0].type = p[3].type
		p[3].nextlist = p[3].nextlist + p[4].nextlist + p[3].continuelist
		p[4].nextlist = p[3].nextlist
		backpatch(p[4].nextlist, p[7].quad)
		backpatch(p[8].truelist, p[2].quad)
		p[0].nextlist = p[8].falselist + p[3].breaklist
		p[0].returnlist = p[3].returnlist
		
	elif len(p) == 15:
		p[0] = Node('for-with-update', [p[3], p[6], p[9],p[13]], 'for-with-update')
		if (p[3].type != 'TYPE_ERROR' and p[6].type != 'TYPE_ERROR' and p[9].type != 'TYPE_ERROR'):
			p[0].type = p[13].type
		else:
			p[0].type = 'TYPE_ERROR'
		backpatch(p[6].truelist, p[12].quad)
		p[13].nextlist = p[13].nextlist + p[14].nextlist + p[13].continuelist
		p[14].nextlist = p[13].nextlist
		backpatch(p[14].nextlist, p[8].quad)
		backpatch(p[10].nextlist, p[5].quad)
		p[0].nextlist = p[6].falselist + p[13].breaklist
		p[0].returnlist = p[13].returnlist
	p[0].name = 'iteration_statement'

def p_jump_statement(p):
	'''
	jump_statement : GOTO ID SEMICOLON
				   | CONTINUE label_n SEMICOLON
				   | BREAK label_n SEMICOLON
				   | RETURN SEMICOLON
				   | RETURN expression SEMICOLON
	'''
	if (p[1] == 'goto'):
		p[0] = Node('goto', p[2], "goto")
		st.add_goto_ref(p[2],p.lineno(2))
		
	elif(p[1] == 'break'): 
		p[0] = Node('break', None, 'break')
		p[0].breaklist = p[2].nextlist
		
	elif (p[1] == 'continue'): 
		p[0] = Node('continue', None, 'continue')
		p[0].continuelist = p[2].nextlist
			
	elif (p[1] == 'return' and len(p)==3):
		p[0] = Node('return', None, 'return')
		instr.append("return")
		#p[0].returnlist = [len(instr)]
		#instr.append("goto")
		if len(func_type_list)>0 and func_type_list[-1]!='VOID' and func_type_list[-1]!='void':
			messages.add(f'Error at line {p.lineno(1)}: Does not match function return type')
				
	else:
		p[0] = Node('return', [p[2]], "return")
		instr.append("return " + p[2].ret)
		#p[0].returnlist = [len(instr)]
		#instr.append("goto")
		if len(func_type_list)>0:
			if p[2].type!=func_type_list[-1]:
				if (p[2].type=='INT' and func_type_list[-1]=='FLOAT') or (p[2].type=='FLOAT' and func_type_list[-1]=='INT'):
					messages.add(f'Error at line {p.lineno(1)}: Does not match function return type, INT and FLOAT')
				else:
					messages.add(f'Error at line {p.lineno(1)}: Does not match function return type')
			
	p[0].name = 'jump_statement'
	p[0].type = 'VOID'


def p_translation_unit(p):
	'''
	translation_unit : external_declaration
					 | translation_unit external_declaration
	'''
	if len(p) == 2:
		p[0] = Node('start_state', [p[1]], None)
	else:
		p[0]= Node('start_state_1', [p[1], p[2]], None)
	p[0].name = 'translation_unit'

def p_external_declaration(p):
	'''
	external_declaration : function_definition
						 | declaration
	'''
	p[0] = p[1]
	p[0].name = 'external_declaration'
	#if(len(p)==3):
	#	backpatch(p[1].nextlist, p[2].quad)

def p_param_call(p):
	'''
	param_call : 
	'''
	global instr
	global func_name
	instr.append(func_name + ":")	

def p_function_definition(p):
	'''
	function_definition : declaration_specifiers declarator declaration_list param_call compound_statement
						| declaration_specifiers declarator param_call compound_statement
						| declarator declaration_list param_call compound_statement
						| declarator param_call compound_statement
	'''
	if len(p)==4:
		p[0] = Node('func_defn_1',[p[1],p[3]],None)
	elif len(p)==5:
		p[0] = Node('func_defn_2',[p[1],p[2],p[4]],None)
		p[2].type=p[1].type
		p[0].type = p[1].type
		p[0].nextlist = p[4].returnlist
		if st.func_exists(p[2].variables[0]):
			messages.add(f'Error at line {p.lineno(2)}: Function Redeclaration')
		else:
			st.make_func_entry(p[2].variables,p[2].types_of_var,p[1].type)
	elif len(p)==6:
		p[0] = Node('func_defn_3',[p[1],p[2],p[3],p[5]],None)
	p[0].name = 'function_definition'
		
def p_error(p):
	messages.add(f'Error for {p} : syntax error found at line {p.lineno}')
	

parser = yacc.yacc(debug=1)
