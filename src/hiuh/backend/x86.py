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
FUNC_LABELS = {}  # Maps func names to labels
CURRENT_FUNC = None  # Current function being compiled
FUNC_EPILOGUE_LABELS = {}  # func name -> epilogue label
LISTS = {}  # Track list definitions: name -> {'size': N, 'items': [...]}

# Calling convention: args in %rdi, %rsi; return in %rax
# Caller saves: r12, r13 (used for HIUH variables)
# Callee saves: rbp, rbx, r14, r15

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
    
    # First pass: collect function definitions
    func_defs = []
    for stmt in ir:
        if stmt[0] == 'FUNC_DEF':
            func_defs.append(stmt)
        else:
            compile_stmt(stmt, target)
    
    emit("    xor %eax, %eax")
    emit("    pop %rbp")
    emit("    pop %r13")
    emit("    pop %r12")
    emit("    ret")
    
    # Emit function definitions AFTER main returns
    for func_def in func_defs:
        compile_func_def(func_def, target)
    
    # Data section
    emit(".data")
    for i, s in enumerate(STRINGS):
        escaped = s.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n')
        emit(f'msg_{i}: .ascii "{escaped}\\n\\0"')
    emit("msg_nl: .ascii \"\\n\\0\"")
    emit("num_buf: .skip 8")
    emit("input_buf: .skip 256")
    # List data sections
    for list_name, list_info in LISTS.items():
        size = list_info.get('size', 64)
        emit(f"list_{list_name}: .skip {size}")
    emit(".bss")
    emit(".align 8")
    emit("stack: .skip 4096")

def compile_func_def(stmt, target):
    """Compile a function definition"""
    global LABEL_CNT, FUNC_EPILOGUE_LABELS, REG_MAP, NEXT_REG
    func_name, params, body = stmt[1], stmt[2], stmt[3]
    func_lbl = f"func_{func_name}"
    epilog_lbl = new_label()
    FUNC_EPILOGUE_LABELS[func_name] = epilog_lbl
    
    # Emit function label
    emit(f"{func_lbl}:")
    
    # Function prologue
    emit("    push %rbp")
    emit("    mov %rsp, %rbp")
    emit("    sub $16, %rsp   # shadow space + alignment")
    emit("    push %r12")
    emit("    push %r13")
    
    # Map parameters to registers (rdi=param0, rsi=param1)
    saved_reg_map = dict(REG_MAP)
    saved_next_reg = NEXT_REG
    REG_MAP.clear()
    NEXT_REG = 0
    
    param_regs = ['%rdi', '%rsi']
    for j, param in enumerate(params[:2]):
        REG_MAP[param] = param_regs[j]
    
    # Compile function body
    for s in body:
        compile_stmt(s, target)
    
    # Function epilogue
    emit(f".L{epilog_lbl}:")
    emit("    add $16, %rsp")
    emit("    pop %r13")
    emit("    pop %r12")
    emit("    pop %rbp")
    emit("    ret")
    
    # Restore global register map for main
    REG_MAP.clear()
    REG_MAP.update(saved_reg_map)
    NEXT_REG = saved_next_reg

def compile_call(func_name, args, target_reg):
    """Compile a function call, result goes to target_reg"""
    global REG_MAP, NEXT_REG
    
    # Save registers that caller-saved registers we'll clobber
    saved_regs = []
    for r in ['%r12', '%r13']:
        for var, reg in REG_MAP.items():
            if reg == r:
                emit(f"    push {r}   # save caller reg {r} for {var}")
                saved_regs.append(r)
                break
    
    # Prepare arguments: first 2 args in rdi, rsi
    # Remaining args on stack (pushed in reverse order)
    arg_regs = ['%rdi', '%rsi']
    
    # Stack arguments (if more than 2)
    stack_args = args[2:]
    for j, arg in enumerate(reversed(stack_args)):
        if isinstance(arg, int):
            emit(f"    push ${arg}   # stack arg {j}")
        else:
            arg_reg = alloc_reg(arg)
            emit(f"    push {arg_reg}   # stack arg {arg}")
    
    # Register arguments
    for j, arg in enumerate(args[:2]):
        if isinstance(arg, int):
            emit(f"    mov ${arg}, {arg_regs[j]}")
        else:
            arg_reg = alloc_reg(arg)
            emit(f"    mov {arg_reg}, {arg_regs[j]}")
    
    # Emit call
    func_lbl = f"func_{func_name}"
    emit(f"    call {func_lbl}")
    
    # Clean up stack arguments
    if len(stack_args) > 0:
        emit(f"    add ${len(stack_args) * 8}, %rsp")
    
    # Move return value to target
    emit(f"    mov %rax, {target_reg}")
    
    # Restore saved registers
    for r in reversed(saved_regs):
        emit(f"    pop {r}   # restore caller reg {r}")

def compile_stmt(stmt, target):
    global LABEL_CNT, CURRENT_FUNC, FUNC_EPILOGUE_LABELS, REG_MAP, NEXT_REG
    op = stmt[0]
    if op == 'SET':
        name, val = stmt[1], stmt[2]
        reg = alloc_reg(name)
        
        # Handle function call as value
        if isinstance(val, tuple) and val[0] == 'CALL':
            _, func_name, args = val
            compile_call(func_name, args, reg)
            return
        
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
        elif isinstance(val, tuple) and val[0] == 'LIST_LEN':
            _, list_name = val
            list_reg = alloc_reg(list_name)
            emit(f"    # SET n = LIST_LEN {list_name}")
            emit(f"    mov 4({list_reg}), {reg}")
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
    elif op == 'FUNC_DEF':
        # Handled in compile_func_def, which is called after main returns
        pass
    elif op == 'FUNC_DEF':
        func_name, params, body = stmt[1], stmt[2], stmt[3]
        func_lbl = f"func_{func_name}"
        epilog_lbl = new_label()
        FUNC_EPILOGUE_LABELS[func_name] = epilog_lbl
        
        # Emit function label
        emit(f"{func_lbl}:")
        
        # Function prologue
        emit("    push %rbp")
        emit("    mov %rsp, %rbp")
        emit("    sub $16, %rsp   # shadow space + alignment")
        emit("    push %r12")
        emit("    push %r13")
        
        # Map parameters to registers (rdi=param0, rsi=param1)
        saved_reg_map = dict(REG_MAP)
        saved_next_reg = NEXT_REG
        REG_MAP.clear()
        NEXT_REG = 0
        
        param_regs = ['%rdi', '%rsi']
        for j, param in enumerate(params[:2]):
            REG_MAP[param] = param_regs[j]
        
        # Compile function body
        for s in body:
            compile_stmt(s, target)
        
        # Function epilogue
        emit(f".L{epilog_lbl}:")
        emit("    add $16, %rsp")
        emit("    pop %r13")
        emit("    pop %r12")
        emit("    pop %rbp")
        emit("    ret")
        
        # Restore global register map for main
        REG_MAP.clear()
        REG_MAP.update(saved_reg_map)
        NEXT_REG = saved_next_reg
    elif op == 'CALL':
        func_name, args = stmt[1], stmt[2]
        # Compile call as statement (result in rax, discarded)
        compile_call(func_name, args, '%rax')
    elif op == 'RETURN':
        val = stmt[1]
        # Compile expression into rax
        if isinstance(val, int):
            emit(f"    mov ${val}, %rax")
        elif isinstance(val, str):
            ret_reg = alloc_reg(val)
            emit(f"    mov {ret_reg}, %rax")
        elif isinstance(val, tuple) and val[0] == 'CALL':
            _, func_name, args = val
            compile_call(func_name, args, '%rax')
        else:
            emit(f"    mov $0, %rax")
        # Jump to epilogue if in a function
        if CURRENT_FUNC and CURRENT_FUNC in FUNC_EPILOGUE_LABELS:
            emit(f"    jmp .L{FUNC_EPILOGUE_LABELS[CURRENT_FUNC]}")
        else:
            # In main context, just continue (or could error)
            pass
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
                emit(f"    mov $1, %rdx")
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
        emit(f"    mov $1, %rdx")
        emit(f"    mov $1, %edi")
        emit(f"    mov $1, %eax")
        emit(f"    syscall")
        emit(f".LV{lbl_d}:")
    elif op == 'READ':
        var_name = stmt[1] if len(stmt) > 1 else 'input_buf'
        lbl_loop = new_label()
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

    elif op == 'LIST_CREATE':
        list_name = stmt[1]
        # Allocate list: store pointer to list buffer and length=0
        reg = alloc_reg(list_name)
        LISTS[list_name] = {'size': 256}
        emit(f"    # LIST_CREATE {list_name}")
        emit(f"    lea list_{list_name}(%rip), %rax")
        emit(f"    mov %rax, {reg}")
        emit(f"    movl $0, 4(%rax)  # length = 0")
    
    elif op == 'LIST_INIT':
        list_name = stmt[1]
        items = stmt[2] if len(stmt) > 2 else []
        reg = alloc_reg(list_name)
        # Pre-compute item values
        item_vals = []
        for item in items:
            try:
                item_vals.append(int(item))
            except:
                item_vals.append(None)  # variable reference
        LISTS[list_name] = {'size': 256, 'items': item_vals}
        emit(f"    # LIST_INIT {list_name} with {len(items)} items: {items}")
        emit(f"    lea list_{list_name}(%rip), %rax")
        emit(f"    mov %rax, {reg}")
        # Store length
        emit(f"    movl ${len(items)}, 4(%rax)")
        # Store each item at offset 8, 16, 24... (offset 0 is length)
        for j, (item, val) in enumerate(zip(items, item_vals)):
            off = (j + 1) * 8
            if val is not None:
                emit(f"    movq ${val}, {off}(%rax)  # item {j}")
            else:
                item_reg = alloc_reg(item)
                emit(f"    mov {item_reg}, %rbx")
                emit(f"    mov %rbx, {off}(%rax)  # item {j}")

    elif op == 'LIST_APPEND':
        list_name, item = stmt[1], stmt[2]
        list_reg = alloc_reg(list_name)
        emit(f"    # LIST_APPEND {item} -> {list_name}")
        # Get length from offset 4
        emit(f"    mov 4({list_reg}), %rcx  # length")
        # Compute item value - try as integer first
        try:
            item_val = int(item)
            emit(f"    mov ${item_val}, %rbx")
        except:
            item_reg = alloc_reg(item)
            emit(f"    mov {item_reg}, %rbx")
        # Store item at index (elements start at offset 8)
        emit(f"    lea 8({list_reg}), %rax")
        emit(f"    mov %rbx, (%rax, %rcx, 8)")
        # Increment length
        emit(f"    inc %rcx")
        emit(f"    mov %rcx, 4({list_reg})")

    elif op == 'LIST_GET':
        list_name, idx = stmt[1], stmt[2]
        list_reg = alloc_reg(list_name)
        emit(f"    # LIST_GET {list_name}[{idx}]")
        # Get index
        if isinstance(idx, int):
            emit(f"    mov ${idx}, %rcx")
        else:
            idx_reg = alloc_reg(idx)
            emit(f"    mov {idx_reg}, %rcx")
        # Load element (elements at offset 8+idx*8)
        emit(f"    lea 8({list_reg}), %rax")
        emit(f"    mov (%rax, %rcx, 8), %rax")

    elif op == 'LIST_LEN':
        list_name = stmt[1]
        list_reg = alloc_reg(list_name)
        emit(f"    # LIST_LEN {list_name}")
        emit(f"    mov 4({list_reg}), %rax")

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
