#!/usr/bin/env python3
"""
HIUH x86_64 Backend - generates x86 Linux assembly from IR
"""

import sys

REGISTERS = ['%r12', '%r13', '%r8', '%r9', '%r10', '%r11']
REG_MAP = {}
NEXT_REG = 0
VAR_TYPES = {}  # Track variable types: name -> 'int' or 'str'
STRINGS = []
STRING_PTRS = {}  # Maps register encoding -> (length, string_index) for string variables
FUNC_RETURN_TYPES = {}  # Maps func name -> ('str', text) for functions returning strings
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
    global REG_MAP, NEXT_REG, STRINGS, LABEL_CNT, BREAK_STACK, FUNC_LABELS, CURRENT_FUNC, FUNC_EPILOGUE_LABELS, LISTS, VAR_TYPES, STRING_PTRS, FUNC_RETURN_TYPES
    # Reset state for each compilation
    REG_MAP = {}
    NEXT_REG = 0
    STRINGS = []
    VAR_TYPES = {}
    STRING_PTRS = {}
    FUNC_RETURN_TYPES = {}

    emit(".text")
    if target == 'windows':
        emit(".globl main")
        emit("main:")
    elif target == 'gcc':
        # For gcc linking: just emit main, no _start
        emit(".globl main")
        emit("main:")
    else:
        # Standalone: _start calls main
        emit(".globl _start")
        emit("_start:")
        emit("    call main")
        emit("    xor %edi, %edi")
        emit("    mov $60, %rax")
        emit("    syscall")
        emit("main:")
    
    emit("    push %r12")
    emit("    push %r13")
    emit("    xor %r12, %r12   # initialize for use as HIUH variable storage")
    emit("    xor %r13, %r13")
    emit("    push %rbp")
    emit("    lea stack(%rip), %r14")
    
    # Collect function definitions first
    func_defs = []
    for stmt in ir:
        if stmt[0] == 'GREJ':
            func_defs.append(stmt)
    
    # Pre-scan function bodies to determine return types (strings vs integers)
    # This populates FUNC_RETURN_TYPES before main IR compilation
    for func_def in func_defs:
        func_name = func_def[1]
        body = func_def[3] if len(func_def) > 3 else []
        # Check if function body ends with GE TEXT (string return)
        for stmt in reversed(body) if body else []:
            if stmt[0] == 'GE' and isinstance(stmt[1], tuple) and stmt[1][0] == 'TEXT':
                FUNC_RETURN_TYPES[func_name] = ('str', stmt[1][1])
                break
    
    # First pass: compile non-function statements
    for stmt in ir:
        if stmt[0] != 'GREJ':
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
        emit(f'msg_{i}: .asciz "{escaped}"')
    emit("msg_nl: .ascii \"\\n\\0\"")
    emit("num_buf: .skip 8")
    emit("input_buf: .skip 256")
    # List data sections
    for list_name, list_info in LISTS.items():
        size = list_info.get('size', 64)
        emit(f"list_{list_name}: .skip {size}")
    emit(".bss")
    emit(".align 8")
    emit("file_buf: .skip 4096")
    emit("stack: .skip 4096")

def compile_func_def(stmt, target):
    """Compile a function definition"""
    global LABEL_CNT, FUNC_EPILOGUE_LABELS, REG_MAP, NEXT_REG, STRINGS, VAR_TYPES, STRING_PTRS
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
    
    # Inline compile-time constants for known string functions
    # Do this FIRST before any register saves or argument setup
    if func_name == 'str_length' and len(args) >= 1 and isinstance(args[0], str) and args[0].startswith('"'):
        literal = args[0]
        str_content = literal[1:-1]
        emit(f"    mov ${len(str_content)}, {target_reg}  # inline str_length literal")
        return
    if func_name == 'char_at' and len(args) >= 2 and isinstance(args[0], str) and args[0].startswith('"') and isinstance(args[1], int):
        literal = args[0]
        str_content = literal[1:-1]
        idx = args[1]
        if 0 <= idx < len(str_content):
            emit(f"    mov ${ord(str_content[idx])}, {target_reg}  # inline char_at literal")
        else:
            emit(f"    mov $0, {target_reg}  # inline char_at out-of-bounds")
        return
    
    # Save ALL caller-saved registers that the compiler uses (r12, r13, r8-r11)
    # before the call. They may contain live values even if not yet assigned to variables.
    for r in ['%r12', '%r13', '%r8', '%r9', '%r10', '%r11']:
        emit(f"    push {r}   # save caller-saved reg")
    
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
        elif isinstance(arg, str) and arg.startswith('"') and len(arg[1:-1]) == 1:
            # Single-character string: convert to ASCII code
            ascii_val = ord(arg[1:-1])
            emit(f"    mov ${ascii_val}, {arg_regs[j]}")
        else:
            arg_reg = alloc_reg(arg)
            emit(f"    mov {arg_reg}, {arg_regs[j]}")
    
    # Emit call
    func_lbl = f"func_{func_name}"
    emit(f"    call {func_lbl}")
    
    # Clean up stack arguments
    if len(stack_args) > 0:
        emit(f"    add ${len(stack_args) * 8}, %rsp")
    
    # Save return value to temp location (before pops restores old values)
    emit(f"    mov %rax, %r14  # temp save return value")
    
    # Restore saved registers (in reverse order)
    for r in reversed(['%r12', '%r13', '%r8', '%r9', '%r10', '%r11']):
        emit(f"    pop {r}   # restore caller-saved reg")
    
    # Move return value to target (after restores)
    emit(f"    mov %r14, {target_reg}")


def compile_condition(cond, false_label, true_label=None):
    """
    Compile a condition (simple or compound AND/OR) to assembly.
    
    Args:
        cond: condition to compile (may be simple or compound AND/OR)
        false_label: label to jump to when condition is FALSE
        true_label: for OR conditions, label to jump to when TRUE (optional)
    
    cond can be:
    - Simple comparison tuple: (var, op, val)
    - AND compound: ('AND', cond1, cond2, ...)
    - OR compound: ('OR', cond1, cond2, ...)
    """
    if true_label is None:
        true_label = false_label  # backward compatibility
    if isinstance(cond, tuple) and cond[0] in ('AND', 'OR'):
        # Compound condition
        op = cond[0]
        sub_conds = cond[1:]
        if op == 'AND':
            # AND: if ANY sub-condition is FALSE, jump to false_label
            for sub in sub_conds:
                compile_condition(sub, false_label)
        else:  # OR
            # OR: if ANY sub-condition is TRUE, we take the TRUE path
            # If ALL sub-conditions are FALSE, we take the FALSE path
            skip_labels = [new_label() for _ in sub_conds[:-1]]
            true_lbl = true_label  # use the passed true_label for OR
            
            for i, sub in enumerate(sub_conds):
                var, sub_op, sub_val = sub
                reg = alloc_reg(var)
                try:
                    val_int = int(sub_val)
                except (ValueError, TypeError):
                    val_int = 0
                
                emit(f"    # OR sub-condition {i+1}/{len(sub_conds)}")
                emit(f"    cmp ${val_int}, {reg}")
                
                # If this sub-condition is TRUE, jump to TRUE body
                # If FALSE, fall through to check next condition (or to false_label if last)
                if sub_op == 'likaMed':
                    emit(f"    je .L{true_lbl}    # true, take TRUE path")
                elif sub_op == 'inteLikaMed':
                    emit(f"    jne .L{true_lbl}   # true, take TRUE path")
                elif sub_op == 'mindre':
                    emit(f"    jl .L{true_lbl}    # true, take TRUE path")
                elif sub_op == 'större':
                    emit(f"    jg .L{true_lbl}    # true, take TRUE path")
                elif sub_op == 'mindreLikaMed':
                    emit(f"    jle .L{true_lbl}    # true, take TRUE path")
                elif sub_op == 'störreLikaMed':
                    emit(f"    jge .L{true_lbl}    # true, take TRUE path")
                
                # If FALSE for non-last, fall through to next condition check
                if i < len(skip_labels):
                    emit(f".L{skip_labels[i]}:")
            
            # All sub-conditions were FALSE → jump to false_label
            emit(f"    jmp .L{false_label}")
        
        return false_label
    else:
        # Simple comparison: (var, op, val)
        var, op, val = cond
        
        # Handle implicit function call: (('ANROPA', func, args), op, 0)
        # When var itself is a function call result used as condition
        if isinstance(var, tuple) and var[0] == 'ANROPA':
            _, func_name, args = var
            # Compile the function call first, result in %rax
            compile_call(func_name, args, '%rax')
            # Compare %rax against 0
            emit(f"    cmp $0, %rax")
            if op == 'inteLikaMed':
                emit(f"    je .L{false_label}   # call result != 0 → true")
            elif op == 'likaMed':
                emit(f"    jne .L{false_label}  # call result == 0 → true")
            elif op == 'mindre':
                emit(f"    jge .L{false_label}  # call result >= 0")
            elif op == 'större':
                emit(f"    jle .L{false_label}  # call result <= 0")
            elif op == 'mindreLikaMed':
                emit(f"    jg .L{false_label}   # call result > 0")
            elif op == 'störreLikaMed':
                emit(f"    jl .L{false_label}   # call result < 0")
            return false_label
        
        reg = alloc_reg(var)
        # Check if val is a string variable (has known type) or a register reference
        val_is_string = False
        if isinstance(val, str) and val in VAR_TYPES and VAR_TYPES[val] == 'str':
            val_reg = alloc_reg(val)
            emit(f"    cmp {val_reg}, {reg}")
            val_is_string = True
        elif isinstance(val, str) and val.startswith('"'):
            # String literal in condition: if single char, get ASCII code
            text = val[1:-1]  # strip quotes
            if len(text) == 1:
                # Single character: use ASCII code
                val_int = ord(text)
                emit(f"    cmp ${val_int}, {reg}")
            else:
                # Multi-char string: compare pointers
                if text not in STRINGS:
                    STRINGS.append(text)
                idx = STRINGS.index(text)
                emit(f"    lea msg_{idx}(%rip), %r14")
                emit(f"    cmp %r14, {reg}")
                val_is_string = True
        else:
            try:
                val_int = int(val)
            except (ValueError, TypeError):
                val_int = 0
            emit(f"    cmp ${val_int}, {reg}")
        
        if op == 'likaMed':
            emit(f"    jne .L{false_label}")
        elif op == 'inteLikaMed':
            emit(f"    je .L{false_label}")
        elif op == 'mindre':
            emit(f"    jge .L{false_label}")
        elif op == 'större':
            emit(f"    jle .L{false_label}")
        elif op == 'mindreLikaMed':
            emit(f"    jg .L{false_label}")
        elif op == 'störreLikaMed':
            emit(f"    jl .L{false_label}")
        
        return false_label


def compile_stmt(stmt, target):
    global LABEL_CNT, CURRENT_FUNC, FUNC_EPILOGUE_LABELS, REG_MAP, NEXT_REG
    op = stmt[0]
    if op == 'SÄTT':
        name_expr, val = stmt[1], stmt[2]
        # Normalize: name may be raw string or ('VARIABEL', name_str)
        if isinstance(name_expr, tuple) and name_expr[0] == 'VARIABEL':
            name = name_expr[1]
        else:
            name = name_expr
        reg = alloc_reg(name)
        
        # Handle function call as value
        if isinstance(val, tuple) and val[0] == 'ANROPA':
            _, func_name, args = val
            compile_call(func_name, args, reg)
            # If function returns a string, register it so SKRIV VARIABEL can find it.
            if func_name in FUNC_RETURN_TYPES:
                ret_type, text = FUNC_RETURN_TYPES[func_name]
                if ret_type == 'str':
                    VAR_TYPES[name] = 'str'
                    # Add to STRINGS if not already present (pre-scan doesn't add to STRINGS)
                    if text not in STRINGS:
                        STRINGS.append(text)
                    str_idx = STRINGS.index(text)
                    _reg_num = int(reg.replace('%r', ''))
                    STRING_PTRS[_reg_num] = (len(text), str_idx)
            return
        
        # Handle TEXT: store string pointer
        if isinstance(val, tuple) and val[0] == 'TEXT':
            _, text = val
            VAR_TYPES[name] = 'str'
            # Reuse existing string index if already in STRINGS
            if text in STRINGS:
                idx = STRINGS.index(text)
            else:
                STRINGS.append(text)
                idx = len(STRINGS) - 1
            emit(f"    lea msg_{idx}(%rip), {reg}")
            # Register this pointer so SKRIV VARIABEL can print as string
            _reg_num = int(reg.replace('%r', ''))
            STRING_PTRS[_reg_num] = (len(text), idx)
            return
        
        if isinstance(val, int):
            emit(f"    mov ${val}, {reg}")
        elif isinstance(val, tuple) and val[0] in ('+', 'PLUSS'):
            _, a, b = val
            # Load left operand (a) into its register
            if isinstance(a, int):
                reg_a = alloc_reg(a)
                emit(f"    mov ${a}, {reg_a}")
            else:
                reg_a = alloc_reg(a)
            # Now move to target register and add second operand
            emit(f"    mov {reg_a}, {reg}")
            try:
                b_int = int(b)
                emit(f"    add ${b_int}, {reg}")
            except (ValueError, TypeError):
                reg_b = alloc_reg(b)
                emit(f"    add {reg_b}, {reg}")
        elif isinstance(val, tuple) and val[0] in ('-', 'MINUS'):
            _, a, b = val
            if isinstance(a, int):
                reg_a = alloc_reg(a)
                emit(f"    mov ${a}, {reg_a}")
            else:
                reg_a = alloc_reg(a)
            emit(f"    mov {reg_a}, {reg}")
            try:
                b_int = int(b)
                emit(f"    sub ${b_int}, {reg}")
            except (ValueError, TypeError):
                reg_b = alloc_reg(b)
                emit(f"    sub {reg_b}, {reg}")
        elif isinstance(val, tuple) and val[0] in ('*', 'GÅNGER'):
            _, a, b = val
            if isinstance(a, int):
                reg_a = alloc_reg(a)
                emit(f"    mov ${a}, {reg_a}")
            else:
                reg_a = alloc_reg(a)
            emit(f"    mov {reg_a}, %rax")
            try:
                b_int = int(b)
                emit(f"    imul ${b_int}, %rax")
            except (ValueError, TypeError):
                reg_b = alloc_reg(b)
                emit(f"    imul {reg_b}, %rax")
            emit(f"    mov %rax, {reg}")
        elif isinstance(val, tuple) and val[0] in ('/', 'DELA'):
            _, a, b = val
            if isinstance(a, int):
                reg_a = alloc_reg(a)
                emit(f"    mov ${a}, {reg_a}")
            else:
                reg_a = alloc_reg(a)
            emit(f"    mov {reg_a}, %rax")
            emit(f"    xor %edx, %edx")
            try:
                b_int = int(b)
                emit(f"    mov ${b_int}, %rcx")
            except (ValueError, TypeError):
                reg_b = alloc_reg(b)
                emit(f"    mov {reg_b}, %rcx")
            emit(f"    idiv %rcx")
            emit(f"    mov %rax, {reg}")
        elif isinstance(val, tuple) and val[0] == 'ANTAL':
            _, list_name = val
            list_reg = alloc_reg(list_name)
            emit(f"    # SET n = ANTAL {list_name}")
            emit(f"    movl 4({list_reg}), {reg}d  # 32-bit length, zero-extended to full reg")
        elif isinstance(val, tuple) and val[0] == 'HÄMTA_INDEX':
            _, list_name, idx = val
            list_reg = alloc_reg(list_name)
            emit(f"    # SET x = HÄMTA_INDEX {list_name}[{idx}]")
            # Get index
            if isinstance(idx, int):
                emit(f"    mov ${idx}, %rcx")
            else:
                idx_reg = alloc_reg(idx)
                emit(f"    mov {idx_reg}, %rcx")
            # Load element (elements at offset 8+idx*8)
            emit(f"    lea 8({list_reg}), %rax")
            emit(f"    mov (%rax, %rcx, 8), %rax")
            emit(f"    mov %rax, {reg}")
        else:
            reg_v = alloc_reg(val)
            emit(f"    mov {reg_v}, {reg}")
    elif op == 'FÖR':
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
    elif op == 'OM':
        cond, body = stmt[1], stmt[2]
        false_body = stmt[3] if len(stmt) > 3 else []
        skip_label = new_label()  # skip false body
        end_label = new_label()   # merge point after entire IF
        true_label = new_label()  # TRUE body for OR short-circuit
        
        # Evaluate condition (may be simple or compound AND/OR)
        compile_condition(cond, skip_label, true_label)
        
        # TRUE body - only reached if condition is TRUE
        emit(f".L{true_label}:")
        for s in body:
            compile_stmt(s, target)
        # Always skip FALSE body after TRUE body
        emit(f"    jmp .L{end_label}")
        
        # FALSE body
        emit(f".L{skip_label}:")
        if false_body:
            for s in false_body:
                compile_stmt(s, target)
        emit(f".L{end_label}:")
    elif op == 'MEDAN':
        cond, body = stmt[1], stmt[2]
        start_lbl = new_label()
        end_lbl = new_label()
        BREAK_STACK.append(end_lbl)
        emit(f".L{start_lbl}:")
        
        # Evaluate condition (may be simple or compound AND/OR)
        # Returns label to jump to if condition is FALSE
        false_jump_target = compile_condition(cond, end_lbl)
        
        for s in body:
            compile_stmt(s, target)
        emit(f"    jmp .L{start_lbl}")
        emit(f".L{end_lbl}:")
        BREAK_STACK.pop()
    elif op == 'BRYT':
        end_lbl = BREAK_STACK[-1] if BREAK_STACK else 'end'
        emit(f"    jmp .L{end_lbl}")
    elif op == 'HEJDÅ':
        emit("    xor %edi, %edi")
        emit("    mov $60, %rax")
        emit("    syscall")
    elif op == 'GREJ':
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
        saved_current_func = CURRENT_FUNC
        REG_MAP.clear()
        NEXT_REG = 0
        
        param_regs = ['%rdi', '%rsi']
        for j, param in enumerate(params[:2]):
            REG_MAP[param] = param_regs[j]
        
        # Set CURRENT_FUNC so GE knows to generate epilogue jump
        CURRENT_FUNC = func_name
        
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
        CURRENT_FUNC = saved_current_func
    elif op == 'ANROPA':
        func_name, args = stmt[1], stmt[2]
        # Compile call as statement (result in rax, discarded)
        compile_call(func_name, args, '%rax')
    elif op == 'GE':
        val = stmt[1]
        # Compile expression into rax
        if isinstance(val, int):
            emit(f"    mov ${val}, %rax")
        elif isinstance(val, str):
            if val.startswith('"'):
                # String literal: strip quotes, add to data section, return pointer
                text = val[1:-1]  # remove surrounding quotes
                STRINGS.append(text)
                idx = len(STRINGS) - 1
                emit(f"    lea msg_{idx}(%rip), %rax")
            else:
                # Variable name
                ret_reg = alloc_reg(val)
                emit(f"    mov {ret_reg}, %rax")
        elif isinstance(val, tuple) and val[0] == 'TEXT':
            _, text = val
            # Reuse existing string index if already in STRINGS
            if text in STRINGS:
                idx = STRINGS.index(text)
            else:
                STRINGS.append(text)
                idx = len(STRINGS) - 1
            emit(f"    lea msg_{idx}(%rip), %rax")
            # Register as string pointer for STRING_PTRS tracking
            _ge_reg_num = 0  # result in rax
            STRING_PTRS[_ge_reg_num] = (len(text), idx)
        elif isinstance(val, tuple) and val[0] == 'ANROPA':
            _, func_name, args = val
            compile_call(func_name, args, '%rax')
            # ANROPA returning a string: register rax as string pointer
            # We need to know the string index - parse from STRINGS after call
            # Since GE doesn't know the func's return type, we rely on GE TEXT being added first
        elif isinstance(val, tuple) and val[0] in ('PLUSS', '+'):
            _, a, b = val
            if isinstance(a, int):
                emit(f"    mov ${a}, %rax")
            else:
                reg_a = alloc_reg(a)
                emit(f"    mov {reg_a}, %rax")
            if isinstance(b, int):
                emit(f"    add ${b}, %rax")
            else:
                reg_b = alloc_reg(b)
                emit(f"    add {reg_b}, %rax")
        elif isinstance(val, tuple) and val[0] in ('MINUS', '-'):
            _, a, b = val
            if isinstance(a, int):
                emit(f"    mov ${a}, %rax")
            else:
                reg_a = alloc_reg(a)
                emit(f"    mov {reg_a}, %rax")
            if isinstance(b, int):
                emit(f"    sub ${b}, %rax")
            else:
                reg_b = alloc_reg(b)
                emit(f"    sub {reg_b}, %rax")
        elif isinstance(val, tuple) and val[0] in ('GÅNGER', '*'):
            _, a, b = val
            if isinstance(a, int):
                emit(f"    mov ${a}, %rax")
            else:
                reg_a = alloc_reg(a)
                emit(f"    mov {reg_a}, %rax")
            if isinstance(b, int):
                emit(f"    imul ${b}, %rax")
            else:
                reg_b = alloc_reg(b)
                emit(f"    imul {reg_b}, %rax")
        elif isinstance(val, tuple) and val[0] in ('DELA', '/'):
            _, a, b = val
            if isinstance(a, int):
                emit(f"    mov ${a}, %rax")
            else:
                reg_a = alloc_reg(a)
                emit(f"    mov {reg_a}, %rax")
            emit(f"    xor %edx, %edx")
            if isinstance(b, int):
                emit(f"    mov ${b}, %rcx")
            else:
                reg_b = alloc_reg(b)
                emit(f"    mov {reg_b}, %rcx")
            emit(f"    idiv %rcx")
        else:
            emit(f"    mov $0, %rax")
        # Jump to epilogue if in a function
        if CURRENT_FUNC and CURRENT_FUNC in FUNC_EPILOGUE_LABELS:
            emit(f"    jmp .L{FUNC_EPILOGUE_LABELS[CURRENT_FUNC]}")
        else:
            # In main context, just continue (or could error)
            pass
    elif op == 'SKRIV':
        expr = stmt[1] if len(stmt) > 1 else ''
        
        # Handle RADBRYT (newline)
        if isinstance(expr, tuple) and expr[0] == 'RADBRYT':
            emit(f"    lea msg_nl(%rip), %rsi")
            emit(f"    mov $1, %rdx")
            emit(f"    mov $1, %edi")
            emit(f"    mov $1, %eax")
            emit(f"    syscall")
            return  # RADBRYT done, don't fall through
        elif expr:
            # Handle tuple expressions: VARIABEL, TEXT, PLUSS, MINUS, GÅNGER, DELA
            if isinstance(expr, tuple) and len(expr) >= 2:
                if expr[0] == 'VARIABEL':
                    name = expr[1]
                    reg = alloc_reg(name)
                    ptr = int(reg.replace('%r', '0x').replace('12', 'c').replace('13', 'd').replace('8', '8').replace('9', '9').replace('10', 'a').replace('11', 'b'), 0)
                    if ptr in STRING_PTRS:
                        str_len, str_idx = STRING_PTRS[ptr]
                        emit(f"    # Print string variable {name} (pointer to msg_{str_idx})")
                        emit(f"    lea msg_{str_idx}(%rip), %rsi")
                        emit(f"    mov ${str_len}, %rdx")
                        emit(f"    mov $1, %edi")
                        emit(f"    mov $1, %eax")
                        emit(f"    syscall")
                    else:
                        emit(f"    # Print variable {name}")
                        emit(f"    mov {reg}, %rax")
                        emit(f"    xor %edx, %edx  # clear for div")
                        emit(f"    lea num_buf(%rip), %rsi")
                        lbl_s = new_label()
                        lbl_d = new_label()
                        emit(f"    cmp $10, %rax")
                        emit(f"    jb .Ls{lbl_s}")
                        emit(f"    mov $10, %rcx")
                        emit(f"    div %rcx  # al=quotient, dl=remainder")
                        emit(f"    push %rax")
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
                elif expr[0] == 'HELTAL':
                    value = expr[1]
                    emit(f"    # Print integer literal {value}")
                    emit(f"    mov ${value}, %rax")
                    emit(f"    xor %edx, %edx")
                    emit(f"    lea num_buf(%rip), %rsi")
                    lbl_s = new_label()
                    lbl_d = new_label()
                    emit(f"    cmp $10, %rax")
                    emit(f"    jb .Ls{lbl_s}")
                    emit(f"    mov $10, %rcx")
                    emit(f"    div %rcx")
                    emit(f"    push %rax")
                    emit(f"    add $48, %dl")
                    emit(f"    movb %dl, 1(%rsi)")
                    emit(f"    pop %rax")
                    emit(f"    add $48, %al")
                    emit(f"    movb %al, (%rsi)")
                    emit(f"    mov $2, %rdx")
                    emit(f"    mov $1, %edi")
                    emit(f"    mov $1, %eax")
                    emit(f"    syscall")
                    emit(f"    jmp .Ld{lbl_d}")
                    emit(f".Ls{lbl_s}:")
                    emit(f"    add $48, %rax")
                    emit(f"    movb %al, (%rsi)")
                    emit(f"    mov $1, %rdx")
                    emit(f"    mov $1, %edi")
                    emit(f"    mov $1, %eax")
                    emit(f"    syscall")
                    emit(f".Ld{lbl_d}:")
                elif expr[0] == 'TEXT':
                    text = expr[1] + '\n'  # Add newline to text
                    # Reuse existing string index if already in STRINGS
                    if text in STRINGS:
                        idx = STRINGS.index(text)
                    else:
                        STRINGS.append(text)
                        idx = len(STRINGS) - 1
                    emit(f"    lea msg_{idx}(%rip), %rsi")
                    emit(f"    mov ${len(text)}, %rdx")
                    emit(f"    mov $1, %edi")
                    emit(f"    mov $1, %eax")
                    emit(f"    syscall")
                elif expr[0] == 'ANTAL':
                    # SKRIV ANTAL lst → print list length
                    list_name = expr[1]
                    list_reg = alloc_reg(list_name)
                    emit(f"    # SKRIV ANTAL {list_name}")
                    emit(f"    movl 4({list_reg}), %eax  # 32-bit length")
                    # Now print %rax (same as HELTAL path)
                    lbl_s = new_label()
                    lbl_d = new_label()
                    emit(f"    xor %edx, %edx")
                    emit(f"    lea num_buf(%rip), %rsi")
                    emit(f"    cmp $10, %rax")
                    emit(f"    jb .Ls{lbl_s}")
                    emit(f"    mov $10, %rcx")
                    emit(f"    div %rcx")
                    emit(f"    push %rax")
                    emit(f"    add $48, %dl")
                    emit(f"    movb %dl, 1(%rsi)")
                    emit(f"    pop %rax")
                    emit(f"    add $48, %al")
                    emit(f"    movb %al, (%rsi)")
                    emit(f"    mov $2, %rdx")
                    emit(f"    mov $1, %edi")
                    emit(f"    mov $1, %eax")
                    emit(f"    syscall")
                    emit(f"    jmp .Ld{lbl_d}")
                    emit(f".Ls{lbl_s}:")
                    emit(f"    add $48, %rax")
                    emit(f"    movb %al, (%rsi)")
                    emit(f"    mov $1, %rdx")
                    emit(f"    mov $1, %edi")
                    emit(f"    mov $1, %eax")
                    emit(f"    syscall")
                    emit(f".Ld{lbl_d}:")
                elif expr[0] in ('PLUSS', 'MINUS', 'GÅNGER', 'DELA'):
                    _, a, b = expr
                    op_sym = expr[0]
                    if isinstance(a, int):
                        emit(f"    mov ${a}, %rax")
                    else:
                        reg_a = alloc_reg(a)
                        emit(f"    mov {reg_a}, %rax")
                    if op_sym == 'PLUSS':
                        if isinstance(b, int):
                            emit(f"    add ${b}, %rax")
                        else:
                            reg_b = alloc_reg(b)
                            emit(f"    add {reg_b}, %rax")
                    elif op_sym == 'MINUS':
                        if isinstance(b, int):
                            emit(f"    sub ${b}, %rax")
                        else:
                            reg_b = alloc_reg(b)
                            emit(f"    sub {reg_b}, %rax")
                    elif op_sym == 'GÅNGER':
                        if isinstance(b, int):
                            emit(f"    imul ${b}, %rax")
                        else:
                            reg_b = alloc_reg(b)
                            emit(f"    imul {reg_b}, %rax")
                    elif op_sym == 'DELA':
                        emit(f"    xor %edx, %edx")
                        if isinstance(b, int):
                            emit(f"    mov ${b}, %rcx")
                        else:
                            reg_b = alloc_reg(b)
                            emit(f"    mov {reg_b}, %rcx")
                        emit(f"    idiv %rcx")
                    # Now print %rax
                    lbl_s = new_label()
                    lbl_d = new_label()
                    emit(f"    xor %edx, %edx")
                    emit(f"    lea num_buf(%rip), %rsi")
                    emit(f"    cmp $10, %rax")
                    emit(f"    jb .Ls{lbl_s}")
                    emit(f"    mov $10, %rcx")
                    emit(f"    div %rcx")
                    emit(f"    push %rax")
                    emit(f"    add $48, %dl")
                    emit(f"    movb %dl, 1(%rsi)")
                    emit(f"    pop %rax")
                    emit(f"    add $48, %al")
                    emit(f"    movb %al, (%rsi)")
                    emit(f"    mov $2, %rdx")
                    emit(f"    mov $1, %edi")
                    emit(f"    mov $1, %eax")
                    emit(f"    syscall")
                    emit(f"    jmp .Ld{lbl_d}")
                    emit(f".Ls{lbl_s}:")
                    emit(f"    add $48, %rax")
                    emit(f"    movb %al, (%rsi)")
                    emit(f"    mov $1, %rdx")
                    emit(f"    mov $1, %edi")
                    emit(f"    mov $1, %eax")
                    emit(f"    syscall")
                    emit(f".Ld{lbl_d}:")
            elif isinstance(expr, str) and not expr.isdigit():
                reg = alloc_reg(expr)
                lbl_s = new_label()
                lbl_d = new_label()
                emit(f"    # Print variable {expr}")
                emit(f"    mov {reg}, %rax")
                emit(f"    xor %edx, %edx  # clear for div")
                emit(f"    lea num_buf(%rip), %rsi")
                emit(f"    cmp $10, %rax")
                emit(f"    jb .Ls{lbl_s}")
                emit(f"    mov $10, %rcx")
                emit(f"    div %rcx  # al=quotient, dl=remainder")
                emit(f"    push %rax")
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
            elif isinstance(expr, int):
                emit(f"    # Print integer {expr}")
                emit(f"    mov ${expr}, %rax")
                emit(f"    xor %edx, %edx")
                emit(f"    lea num_buf(%rip), %rsi")
                lbl_s = new_label()
                lbl_d = new_label()
                emit(f"    cmp $10, %rax")
                emit(f"    jb .Ls{lbl_s}")
                emit(f"    mov $10, %rcx")
                emit(f"    div %rcx")
                emit(f"    push %rax")
                emit(f"    add $48, %dl")
                emit(f"    movb %dl, 1(%rsi)")
                emit(f"    pop %rax")
                emit(f"    add $48, %al")
                emit(f"    movb %al, (%rsi)")
                emit(f"    mov $2, %rdx")
                emit(f"    mov $1, %edi")
                emit(f"    mov $1, %eax")
                emit(f"    syscall")
                emit(f"    jmp .Ld{lbl_d}")
                emit(f".Ls{lbl_s}:")
                emit(f"    add $48, %rax")
                emit(f"    movb %al, (%rsi)")
                emit(f"    mov $1, %rdx")
                emit(f"    mov $1, %edi")
                emit(f"    mov $1, %eax")
                emit(f"    syscall")
                emit(f".Ld{lbl_d}:")
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

    elif op == 'SKAPA_LISTA':
        list_name = stmt[1]
        # Allocate list: store pointer to list buffer and length=0
        reg = alloc_reg(list_name)
        LISTS[list_name] = {'size': 256}
        emit(f"    # LIST_CREATE {list_name}")
        emit(f"    lea list_{list_name}(%rip), %rax")
        emit(f"    mov %rax, {reg}")
        emit(f"    movl $0, 4(%rax)  # length = 0")
    
    elif op == 'NY_LISTA':
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
        emit(f"    # NY_LISTA {list_name} with {len(items)} items: {items}")
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

    elif op == 'LÄGG_TILL':
        list_name, item = stmt[1], stmt[2]
        list_reg = alloc_reg(list_name)
        emit(f"    # LIST_APPEND {item} -> {list_name}")
        # Get length from offset 4 (stored as 32-bit with movl)
        emit(f"    movl 4({list_reg}), %ecx  # length (zero-extended to rcx)")
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
        emit(f"    movl %ecx, 4({list_reg})  # store 32-bit length")

    elif op == 'HÄMTA_INDEX':
        list_name, idx = stmt[1], stmt[2]
        list_reg = alloc_reg(list_name)
        emit(f"    # HÄMTA_INDEX {list_name}[{idx}]")
        # Get index
        if isinstance(idx, int):
            emit(f"    mov ${idx}, %rcx")
        else:
            idx_reg = alloc_reg(idx)
            emit(f"    mov {idx_reg}, %rcx")
        # Load element (elements at offset 8+idx*8)
        emit(f"    lea 8({list_reg}), %rax")
        emit(f"    mov (%rax, %rcx, 8), %rax")

    elif op == 'ANTAL':
        list_name = stmt[1]
        list_reg = alloc_reg(list_name)
        emit(f"    # LIST_LEN {list_name}")
        emit(f"    mov 4({list_reg}), %rax")

    elif op == 'TA_BORT_INDEX':
        list_name, idx = stmt[1], stmt[2]
        list_reg = alloc_reg(list_name)
        lbl_skip = new_label()
        lbl_done = new_label()
        emit(f"    # TA_BORT_INDEX {list_name}[{idx}]")
        # Get length
        emit(f"    movl 4({list_reg}), %ecx  # length (zero-extended to rcx)")
        # Check bounds: if idx >= length, skip
        if isinstance(idx, int):
            emit(f"    cmp ${idx}, %rcx")
        else:
            idx_reg = alloc_reg(idx)
            emit(f"    mov {idx_reg}, %r8")
            emit(f"    cmp %r8, %rcx")
        emit(f"    jle .L{lbl_skip}  # idx >= length, nothing to remove")
        # Compute byte offset: elements start at offset 8, each element is 8 bytes
        if isinstance(idx, int):
            offset = (idx + 1) * 8
            emit(f"    lea {offset}({list_reg}), %rax  # address of element[{idx}]")
        else:
            idx_reg = alloc_reg(idx)
            emit(f"    lea 8({list_reg}), %rax")
            emit(f"    mov {idx_reg}, %r9")
            emit(f"    shl $3, %r9  # idx * 8")
            emit(f"    add %r9, %rax  # address of element[{idx}]")
        # Shift elements down: for i = idx+1 to length-1: element[i-1] = element[i]
        emit(f"    # Shift elements down")
        emit(f"    mov %rcx, %r10  # length")
        emit(f"    dec %r10  # length - 1 (last index)")
        emit(f"    shl $3, %r10  # (length-1) * 8")
        emit(f"    lea 8({list_reg}), %r11  # base of elements")
        emit(f"    add %r10, %r11  # address of last element")
        emit(f".L{lbl_done}_shift:")
        emit(f"    cmp %r11, %rax  # current >= last?")
        emit(f"    jge .L{lbl_done}_shift_end")
        emit(f"    mov 8(%rax), %rbx  # next element")
        emit(f"    mov %rbx, (%rax)  # copy to current")
        emit(f"    add $8, %rax  # next position")
        emit(f"    jmp .L{lbl_done}_shift")
        emit(f".L{lbl_done}_shift_end:")
        # Decrement length
        emit(f"    dec %rcx")
        emit(f"    movl %ecx, 4({list_reg})  # store 32-bit length")
        emit(f".L{lbl_skip}:")

    elif op == 'BYT_UT':
        list_name, idx, new_val = stmt[1], stmt[2], stmt[3]
        list_reg = alloc_reg(list_name)
        emit(f"    # BYT_UT {list_name}[{idx}] = {new_val}")
        # Get index
        if isinstance(idx, int):
            emit(f"    mov ${idx}, %rcx")
        else:
            idx_reg = alloc_reg(idx)
            emit(f"    mov {idx_reg}, %rcx")
        # Compute address of element at index: 8 + idx * 8
        emit(f"    lea 8({list_reg}), %rax")
        emit(f"    shl $3, %rcx  # idx * 8")
        emit(f"    add %rcx, %rax  # address of element[{idx}]")
        # Compute new value
        try:
            val_int = int(new_val)
            emit(f"    mov ${val_int}, %rbx")
        except (ValueError, TypeError):
            val_reg = alloc_reg(new_val)
            emit(f"    mov {val_reg}, %rbx")
        # Store new value at element address
        emit(f"    mov %rbx, (%rax)")

    elif op == 'ÖPPNA_FIL':
        filename, mode = stmt[1], stmt[2]
        emit(f"    # FILE_OPEN {filename} mode={mode}")
        # Create filename string label (uses msg_ labels)
        STRINGS.append(filename)
        fname_idx = len(STRINGS) - 1
        emit(f"    lea msg_{fname_idx}(%rip), %rdi")
        if mode == 'r':
            emit(f"    xor %rsi, %rsi  # O_RDONLY = 0")
        else:
            emit(f"    mov $0x241, %rsi  # O_WRONLY|O_CREAT|O_TRUNC")
        emit(f"    mov $0644, %rdx  # mode=rw-r--r--")
        emit(f"    mov $2, %rax  # sys_open")
        emit(f"    syscall")
        emit(f"    # file descriptor now in %rax")

    elif op == 'SKRIV_FIL':
        filename, data = stmt[1], stmt[2]
        emit(f"    # FILE_WRITE {filename} data={data}")
        # Add filename to data section
        STRINGS.append(filename)
        fname_idx = len(STRINGS) - 1
        # Open file: syscall open(path, O_WRONLY|O_CREAT|O_TRUNC, 0644)
        emit(f"    lea msg_{fname_idx}(%rip), %rdi")
        emit(f"    mov $0x241, %rsi  # O_WRONLY|O_CREAT|O_TRUNC")
        emit(f"    mov $0644, %rdx")
        emit(f"    mov $2, %rax  # sys_open")
        emit(f"    syscall")
        emit(f"    mov %rax, %r15  # save fd in callee-saved register")
        # Write data string
        STRINGS.append(data)
        data_idx = len(STRINGS) - 1
        emit(f"    lea msg_{data_idx}(%rip), %rsi  # data string")
        emit(f"    mov ${len(data)}, %rdx  # length")
        emit(f"    mov %r15, %rdi  # fd")
        emit(f"    mov $1, %rax  # sys_write")
        emit(f"    syscall")
        # Close file
        emit(f"    mov %r15, %rdi")
        emit(f"    mov $3, %rax  # sys_close")
        emit(f"    syscall")

    elif op == 'LÄS_FIL':
        filepath, var_name = stmt[1], stmt[2]
        emit(f"    # FILE_READ {filepath} -> {var_name}")
        # Add filepath to data section
        STRINGS.append(filepath)
        fname_idx = len(STRINGS) - 1
        # Open file: syscall open(path, O_RDONLY, 0)
        emit(f"    lea msg_{fname_idx}(%rip), %rdi")
        emit(f"    xor %rsi, %rsi  # O_RDONLY = 0")
        emit(f"    xor %rdx, %rdx  # mode = 0")
        emit(f"    mov $2, %rax  # sys_open")
        emit(f"    syscall")
        emit(f"    mov %rax, %r15  # save fd in callee-saved register")
        # Read file into buffer
        emit(f"    lea file_buf(%rip), %rsi")
        emit(f"    mov $4096, %rdx  # max bytes")
        emit(f"    mov %r15, %rdi  # fd")
        emit(f"    mov $0, %rax  # sys_read")
        emit(f"    syscall")
        # Store bytes read in variable
        reg = alloc_reg(var_name)
        emit(f"    mov %rax, {reg}  # store byte count in {var_name}")
        # Close file
        emit(f"    mov %r15, %rdi")
        emit(f"    mov $3, %rax  # sys_close")
        emit(f"    syscall")

    elif op == 'LÄS_RAD':
        var_name = stmt[1]
        lbl_s = new_label()
        emit(f"    # READ_LINE {var_name}")
        emit(f"    lea input_buf(%rip), %rsi")
        emit(f"    mov $256, %rdx")
        emit(f"    mov $0, %edi  # stdin")
        emit(f"    mov $0, %rax  # sys_read")
        emit(f"    syscall")
        emit(f"    # Null-terminate at newline or end")
        emit(f"    mov $0, %rcx  # index = 0")
        emit(f"    mov $10, %r8b   # newline = 10 (byte)")
        emit(f".Ls{lbl_s}_scan_newline:")
        emit(f"    cmp $255, %rcx  # max 255")
        emit(f"    jge .Ls{lbl_s}_scan_end")
        emit(f"    movb (%rsi,%rcx), %al")
        emit(f"    cmp $0, %al  # null terminator?")
        emit(f"    je .Ls{lbl_s}_scan_end")
        emit(f"    cmp %r8b, %al  # newline?")
        emit(f"    je .Ls{lbl_s}_scan_end")
        emit(f"    inc %rcx")
        emit(f"    jmp .Ls{lbl_s}_scan_newline")
        emit(f".Ls{lbl_s}_scan_end:")
        emit(f"    movb $0, (%rsi,%rcx)  # null terminate")
        emit(f"    mov %rsi, %rax  # buffer address")
        reg = alloc_reg(var_name)
        emit(f"    mov %rax, {reg}  # store buffer address in {var_name}")

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
