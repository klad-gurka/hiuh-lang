.text
.globl _start
_start:
    lea stack(%rip), %r14  # init stack ptr
    lea num_buf(%rip), %rsi
    mov %r12b, (%rsi)
    mov $1, %rdx
    mov $1, %rdi
    mov $1, %eax
    syscall
    mov $0, %edi
    mov $60, %rax
    syscall

.data
num_buf: .byte 0
input_buf: .skip 256
.bss
.align 8
stack: .skip 4096
