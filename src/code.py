import symbol_table
from parser.grammar import instr


code = []
regs = ['RBX','RCX','RDX','RSI','RDI']

def param(x):
	code.append('pushq '+str(x))

def call_begin(ID,name):
	#Fulfills both caller and callee partially.
	# CALLER PART
	code.append('push rax')
	code.append('push rbx')
	code.append('push rcx')
	code.append('push rdx')
	code.append('push rsi')
	code.append('push rdi')
	code.append('call '+str(ID))# is this the right instr? call func? func is the label here before the function code, similar to goto labels.
	# CALLEE PART
	code.append('push rbp')
	code.append('mov  rsp, rbp')
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
	code.append('subb rsp, '+str(space_for_variables))


def call_end(name):
	# pop the regs
	# Pop the parameters and put the return value from eax into ...
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
	code.append('addb rsp, '+str(space_for_params))

def returnn(ret_val):
	# Assuming 8Bytes and that ret_val is the memory address that has the return value
	code.append('movq '+str(ret_val)+', %rax')
	code.append('mov %rbp, %rsp') # move ebp into esp  
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



def main():
	return
	for x in instr:
		if x=='printcall':
			print_call()
	f = open("./src/assembly.asm", "w")
	for x in code:
		f.write(x)
		f.write('\n')
	f.close()



