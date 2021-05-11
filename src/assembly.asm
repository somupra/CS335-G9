global main
section .text
f:
push rbp
mov  rbp, rsp
sub rsp, byte 0
mov rax, 1
mov rsp, rbp
pop rbp
ret
mov rax, 0
mov rsp, rbp
pop rbp
ret
main:

push 4
push rax
push rbx
push rcx
push rdx
push rsi
push rdi
call f
pop rdi
pop rsi
pop rdx
pop rcx
pop rbx
pop rax
add rsp, byte 16
mov rax, 0
