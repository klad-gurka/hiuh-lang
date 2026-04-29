#!/usr/bin/env python3
"""
HIUH x86_64 Backend - generates x86 Linux assembly from IR
"""

import sys

REGISTERS = ['%r12', '%r13', '%r8', '%r9', '%r10', '%r11']
REG_MAP = {}
NEXT_REG = 0
STRINGS = []
LABEL_CNT = 0
BREAK_STACK = []  # Stack of end labels for BREAK

def alloc_reg(name):
    global NEXT_REG
    if name not in REG_MAP:
        REG_MAP[name] = REGISTERS[NEXT_REG % len(REGISTERS)]
        NEXT_REG += 1
    return REG_MAP[name]

def new_label():
    global LABEL_CNT
    LABEL_CNT += 1
    return str(LABEL_CNT)

def emit(s):
    print(s)

def compile_ir(ir, target='linux'):
    """Compile IR to x86 assembly"""
    emit(".text")
    if target == 'windows':
        emit(".globl main")
        emit("main:")
    else:
        emit(".globl _start")
        emit("_start:")
        emit("    call main")
        emit("    xor %edi, %edi")
        emit("    mov $60, %rax")
        emit("    syscall")
        emit("main:")
    
    emit("    push %r12")
    emit("    push %r13")
    emit("    push %rbp")
    emit("    lea stack(%rip), %r14")
    
    for stmt in ir:
        compile_stmt(stmt, target)
    
    emit("    xor %eax, %eax")
    emit("    pop %rbp")
    emit("    pop %r13")
    emit("    pop %r12")
    emit("    ret")
    
    # Data section
    emit(".data")
    for i, s in enumerate(STRINGS):
        escaped = s.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n')
        emit(f'msg_{i}: .ascii "{escaped}\\n\\0"')
    emit("msg_nl: .ascii \"\\n\\0\"")
    emit("num_buf: .skip 8")
    emit("input_buf: .skip 256")
    emit(".bss")
    emit(".align 8")
    emit("stack: .skip 4096")

def compile_stmt(stmt, target):
    global LABEL_CNT
    op = stmt[0]
    if op == 'SET':
        name, val = stmt[1], stmt[2]
        reg = alloc_reg(name)
        if isinstance(val, int):
            emit(f"    mov ${val}, {reg}")
        elif isinstance(val, tuple) and val[0] == '+':
            _, a, b = val
            reg_a = alloc_reg(a)
            emit(f"    mov {reg_a}, {reg}")
            emit(f"    add ${b}, {reg}")
        elif isinstance(val, tuple) and val[0] == '-':
            _, a, b = val
            reg_a = alloc_reg(a)
            emit(f"    mov {reg_a}, {reg}")
            emit(f"    sub ${b}, {reg}")
        elif isinstance(val, tuple) and val[0] == '*':
            _, a, b = val
            reg_a = alloc_reg(a)
            emit(f"    mov {reg_a}, %rax")
            emit(f"    imul ${b}, %rax")
            emit(f"    mov %rax, {reg}")
        elif isinstance(val, tuple) and val[0] == '/':
            _, a, b = val
            reg_a = alloc_reg(a)
            emit(f"    mov {reg_a}, %rax")
            emit(f"    xor %edx, %edx")
            emit(f"    mov ${b}, %rcx")
            emit(f"    idiv %rcx")
            emit(f"    mov %rax, {reg}")
        else:
            reg_v = alloc_reg(val)
            emit(f"    mov {reg_v}, {reg}")
    elif op == 'FOR':
        var, start, end, body = stmt[1], stmt[2], stmt[3], stmt[4]
        reg = alloc_reg(var)
        start_lbl = new_label()
        end_lbl = new_label()
        BREAK_STACK.append(end_lbl)
        emit(f"    mov ${start}, {reg}")
        emit(f".L{start_lbl}:")
        emit(f"    cmp ${end}, {reg}")
        emit(f"    jge .L{end_lbl}")
        for s in body:
            compile_stmt(s, target)
        emit(f"    inc {reg}")
        emit(f"    jmp .L{start_lbl}")
        emit(f".L{end_lbl}:")
        BREAK_STACK.pop()
    elif op == 'IF':
        cmp, body = stmt[1], stmt[2]
        var, op, val = cmp
        reg = alloc_reg(var)
        lbl = new_label()
        try:
            val_int = int(val)
        except (ValueError, TypeError):
            val_int = 0
        if op == '==':
            emit(f"    cmp ${val_int}, {reg}")
            emit(f"    jne .L{lbl}")
        elif op == '!=':
            emit(f"    cmp ${val_int}, {reg}")
            emit(f"    je .L{lbl}")
        elif op == '<':
            emit(f"    cmp ${val_int}, {reg}")
            emit(f"    jge .L{lbl}")
        elif op == '>':
            emit(f"    cmp ${val_int}, {reg}")
            emit(f"    jle .L{lbl}")
        elif op == '<=':
            emit(f"    cmp ${val_int}, {reg}")
            emit(f"    jg .L{lbl}")
        elif op == '>=':
            emit(f"    cmp ${val_int}, {reg}")
            emit(f"    jl .L{lbl}")
        for s in body:
            compile_stmt(s, target)
        emit(f".L{lbl}:")
    elif op == 'WHILE':
        cmp, body = stmt[1], stmt[2]
        var, op, val = cmp
        reg = alloc_reg(var)
        start_lbl = new_label()
        end_lbl = new_label()
        BREAK_STACK.append(end_lbl)
        emit(f".L{start_lbl}:")
        try:
            val_int = int(val)
        except (ValueError, TypeError):
            val_int = 0
        if op == '==':
            emit(f"    cmp ${val_int}, {reg}")
            emit(f"    jne .L{end_lbl}")
        elif op == '!=':
            emit(f"    cmp ${val_int}, {reg}")
            emit(f"    je .L{end_lbl}")
        elif op == '<':
            emit(f"    cmp ${val_int}, {reg}")
            emit(f"    jge .L{end_lbl}")
        elif op == '>':
            emit(f"    cmp ${val_int}, {reg}")
            emit(f"    jle .L{end_lbl}")
        elif op == '<=':
            emit(f"    cmp ${val_int}, {reg}")
            emit(f"    jg .L{end_lbl}")
        elif op == '>=':
            emit(f"    cmp ${val_int}, {reg}")
            emit(f"    jl .L{end_lbl}")
        for s in body:
            compile_stmt(s, target)
        emit(f"    jmp .L{start_lbl}")
        emit(f".L{end_lbl}:")
        BREAK_STACK.pop()
    elif op == 'BREAK':
        end_lbl = BREAK_STACK[-1] if BREAK_STACK else 'end'
        emit(f"    jmp .L{end_lbl}")
    elif op == 'EXIT':
        emit("    xor %edi, %edi")
        emit("    mov $60, %rax")
        emit("    syscall")
    elif op in ('SKRIV', 'SKRIV_NL'):
        expr = stmt[1] if len(stmt) > 1 else ''
        if expr:
            if isinstance(expr, str) and not expr.isdigit():
                reg = alloc_reg(expr)
                lbl_s = new_label()
                lbl_d = new_label()
                emit(f"    # Print variable {expr}")
                emit(f"    mov {reg}, %rax")
                emit(f"    xor %edx, %edx  # clear for div")
                emit(f"    lea num_buf(%rip), %rsi")
                emit(f"    cmp $10, %rax")
                emit(f"    jb .Ls{lbl_s}")
                emit(f"    # >=10: two digits")
                emit(f"    mov $10, %rcx")
                emit(f"    div %rcx  # al=quotient, dl=remainder")
                emit(f"    push %rax  # save quotient")
                emit(f"    add $48, %dl")
                emit(f"    movb %dl, 1(%rsi)  # ones digit")
                emit(f"    pop %rax")
                emit(f"    add $48, %al  # tens digit")
                emit(f"    movb %al, (%rsi)")
                emit(f"    mov $2, %rdx")
                emit(f"    mov $1, %edi")
                emit(f"    mov $1, %eax")
                emit(f"    syscall")
                emit(f"    jmp .Ld{lbl_d}")
                emit(f".Ls{lbl_s}:")
                emit(f"    add $48, %rax  # single digit")
                emit(f"    movb %al, (%rsi)")
                emit(f"    mov $1, %edx")
                emit(f"    mov $1, %edi")
                emit(f"    mov $1, %eax")
                emit(f"    syscall")
                emit(f".Ld{lbl_d}:")
        if op == 'SKRIV_NL':
            emit(f"    lea msg_nl(%rip), %rsi")
            emit(f"    mov $1, %rdx")
            emit(f"    mov $1, %edi")
            emit(f"    mov $1, %eax")
            emit(f"    syscall")
    elif op == 'SKRIV_VAR':
        name = stmt[1]
        reg = alloc_reg(name)
        lbl_s = new_label()
        lbl_d = new_label()
        emit(f"    # Print variable value: {name}")
        emit(f"    mov {reg}, %rax")
        emit(f"    xor %edx, %edx  # clear for div")
        emit(f"    lea num_buf(%rip), %rsi")
        emit(f"    cmp $10, %rax")
        emit(f"    jb .LV{lbl_s}")
        emit(f"    # >=10: two digits")
        emit(f"    mov $10, %rcx")
        emit(f"    div %rcx  # al=quotient, dl=remainder")
        emit(f"    push %rax  # save quotient")
        emit(f"    add $48, %dl")
        emit(f"    movb %dl, 1(%rsi)  # ones digit")
        emit(f"    pop %rax")
        emit(f"    add $48, %al  # tens digit")
        emit(f"    movb %al, (%rsi)")
        emit(f"    mov $2, %rdx")
        emit(f"    mov $1, %edi")
        emit(f"    mov $1, %eax")
        emit(f"    syscall")
        emit(f"    jmp .LV{lbl_d}")
        emit(f".LV{lbl_s}:")
        emit(f"    add $48, %rax  # single digit")
        emit(f"    movb %al, (%rsi)")
        emit(f"    mov $1, %edx")
        emit(f"    mov $1, %edi")
        emit(f"    mov $1, %eax")
        emit(f"    syscall")
        emit(f".LV{lbl_d}:")
    elif op == 'READ':
        var_name = stmt[1] if len(stmt) > 1 else 'input_buf'
        lbl_loop = new_label()
        lbl_null = new_label()
        lbl_done = new_label()
        emit(f"    # READ: read integer from stdin")
        emit(f"    lea input_buf(%rip), %rsi")
        emit(f"    mov $256, %rdx")
        emit(f"    mov $0, %edi  # stdin")
        emit(f"    mov $0, %eax  # sys_read")
        emit(f"    syscall")
        emit(f"    # atoi: convert string in input_buf to integer")
        emit(f"    lea input_buf(%rip), %rsi")
        emit(f"    xor %rax, %rax  # result = 0")
        emit(f"    xor %rcx, %rcx  # index = 0")
        emit(f"    mov $10, %r8   # divisor = 10")
        emit(f".L{lbl_loop}_read_loop:")
        emit(f"    movb (%rsi, %rcx), %bl")
        emit(f"    cmp $0, %bl  # null terminator?")
        emit(f"    je .L{lbl_done}_read_done")
        emit(f"    cmp $48, %bl  # '0'?")
        emit(f"    jb .L{lbl_done}_read_done")
        emit(f"    cmp $57, %bl  # '9'?")
        emit(f"    ja .L{lbl_done}_read_done")
        emit(f"    imul $10, %rax  # result *= 10")
        emit(f"    sub $48, %bl  # digit = char - '0'")
        emit(f"    add %rbx, %rax  # result += digit")
        emit(f"    inc %rcx")
        emit(f"    jmp .L{lbl_loop}_read_loop")
        emit(f".L{lbl_done}_read_done:")
        reg = alloc_reg(var_name)
        emit(f"    mov %rax, {reg}  # store result in {var_name}")

def compile_stream():
    """Read IR (as repr lines) from stdin, output x86 assembly"""
    ir = []
    for line in sys.stdin:
        line = line.strip()
        if line.startswith('('):
            ir.append(eval(line))
    compile_ir(ir)

if __name__ == '__main__':
    compile_stream()