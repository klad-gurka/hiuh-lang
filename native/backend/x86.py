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

def alloc_reg(name):
    global NEXT_REG
    if name not in REG_MAP:
        REG_MAP[name] = REGISTERS[NEXT_REG % len(REGISTERS)]
        NEXT_REG += 1
    return REG_MAP[name]

def new_label():
    global LABEL_CNT
    LABEL_CNT += 1
    return f".L{LABEL_CNT}"

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
    emit("num_buf: .byte 0")
    emit("input_buf: .skip 256")
    emit(".bss")
    emit(".align 8")
    emit("stack: .skip 4096")

def compile_stmt(stmt, target):
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
        else:
            reg_v = alloc_reg(val)
            emit(f"    mov {reg_v}, {reg}")
    elif op == 'FOR':
        var, start, end, body = stmt[1], stmt[2], stmt[3], stmt[4]
        reg = alloc_reg(var)
        start_lbl = new_label()
        end_lbl = new_label()
        emit(f"    mov ${start}, {reg}")
        emit(f"{start_lbl}:")
        emit(f"    cmp ${end}, {reg}")
        emit(f"    jge {end_lbl}")
        for s in body:
            compile_stmt(s, target)
        emit(f"    inc {reg}")
        emit(f"    jmp {start_lbl}")
        emit(f"{end_lbl}:")
    elif op == 'IF':
        cmp, body = stmt[1], stmt[2]
        var, op, val = cmp
        reg = alloc_reg(var)
        lbl = new_label()
        if op == '==':
            emit(f"    cmp ${val}, {reg}")
            emit(f"    jne {lbl}")
        elif op == '!=':
            emit(f"    cmp ${val}, {reg}")
            emit(f"    je {lbl}")
        for s in body:
            compile_stmt(s, target)
        emit(f"{lbl}:")
    elif op == 'BREAK':
        emit("    jmp .Lend")  # Simplified
    elif op == 'EXIT':
        emit("    xor %edi, %edi")
        emit("    mov $60, %rax")
        emit("    syscall")
    elif op in ('SKRIV', 'SKRIV_NL'):
        expr = stmt[1] if len(stmt) > 1 else ''
        if expr:
            reg = alloc_reg(expr)
            STRINGS.append(f"%d" if expr else "")
            idx = len(STRINGS) - 1
            emit(f"    lea msg_{idx}(%rip), %rsi")
            emit(f"    mov ${expr}, %rdx")
            emit(f"    mov $1, %edi")
            emit(f"    mov $1, %eax")
            emit(f"    syscall")
        if op == 'SKRIV_NL':
            STRINGS.append("")
            idx = len(STRINGS) - 1
            emit(f"    lea msg_{idx}(%rip), %rsi")
            emit(f"    mov $1, %edx")
            emit(f"    mov $1, %edi")
            emit(f"    mov $1, %eax")
            emit(f"    syscall")

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
