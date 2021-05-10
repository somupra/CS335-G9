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
	for x in instr:
		print(x)
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



