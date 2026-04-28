.text
.globl _start
_start:
    lea stack(%rip), %r14  # init stack ptr
    mov $0, %eax  # read
    mov $0, %edi  # stdin
    lea input_buf(%rip), %rsi
    mov $256, %edx  # max bytes
    syscall
    mov $0, %r12  # for i
L1:
    mov $255, %rax
    cmp %rax, %r12
    jge L2
    mov %r12, %rax  # cmp tecken == 0
    cmp $0, %rax
    sete %al
    cmp $0, %al  # if
    je L3
    cmp $0, %al  # if
    je L4
L4:
L3:
    mov %r15, %rax  # cmp_lt tecken < 33
    cmp $33, %rax
    setl %al
    cmp $0, %al  # if
    je L5
    cmp $0, %al  # if
    je L6
L6:
L5:
    mov %r15, %rax  # cmp_gt tecken > 32
    cmp $32, %rax
    setg %al
    cmp $0, %al  # if
    je L7
    lea ord_buf(%rip), %rsi
    mov %r12, %rcx
    add %rcx, %rsi
    mov %r15b, (%rsi)
L7:
    mov %r12, %rax  # cmp f == 1
    cmp $1, %rax
    sete %al
    cmp $0, %al  # if
    je L8
    mov $0, %rdx  # count fallback
    lea ord_buf(%rip), %rsi
    mov $1, %edi
    mov $1, %eax
    syscall
    lea _nl(%rip), %rsi
    mov $1, %rdx
    mov $1, %edi
    mov $1, %eax
    syscall
L8:
    lea num_buf(%rip), %rsi
    mov %r12b, (%rsi)
    mov $1, %rdx
    mov $1, %rdi
    mov $1, %eax
    syscall
    inc %r12
    jmp L1
L2:
    mov $0, %edi
    mov $60, %rax
    syscall

.data
num_buf: .byte 0
input_buf: .skip 256
ord_buf: .skip 256
_nl: .ascii "\n"
.bss
.align 8
stack: .skip 4096
