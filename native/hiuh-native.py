#!/usr/bin/env python3
"""
HIUH Native Compiler - x86_64 assembly
Simple register-based variable allocation
"""

import sys
import subprocess
import tempfile
import os

def tokenize(src):
    tokens = []
    for line in src.split('\n'):
        stripped = line.lstrip()
        if not stripped:
            continue
        words = stripped.split()
        first = words[0]
        
        if first == 'Skriv':
            rest = ' '.join(words[1:])
            if rest.startswith('värdet av '):
                tokens.append(('SKRIV_VAR', words[-1]))
            else:
                tokens.append(('SKRIV', rest))
        elif first == 'Sätt' and len(words) >= 4:
            var = words[1]
            rest = ' '.join(words[3:])
            if 'pluss' in rest:
                parts = rest.split('pluss')
                left = parts[0].strip()
                right = parts[1].strip() if len(parts) > 1 else '0'
                tokens.append(('PLUS', var, left, right))
            else:
                tokens.append(('SET', var, rest))
        elif first == 'För':
            var = words[1] if len(words) > 1 else 'i'
            try:
                fi = words.index('från')
                ti = words.index('till')
                start = words[fi+1]
                end = words[ti+1]
            except:
                start, end = '0', '10'
            tokens.append(('FOR', var, start, end))
        elif first == 'Hejdå':
            tokens.append(('END',))
        elif first == 'JagMåsteGåNu':
            code = words[1] if len(words) > 1 and words[1].isdigit() else '0'
            tokens.append(('EXIT', code))
    return tokens

def parse(tokens):
    stmts = []
    i = 0
    while i < len(tokens):
        tok = tokens[i]
        if tok[0] == 'SKRIV':
            stmts.append(tok)
            i += 1
        elif tok[0] == 'SKRIV_VAR':
            stmts.append(tok)
            i += 1
        elif tok[0] == 'SET':
            stmts.append(tok)
            i += 1
        elif tok[0] == 'PLUS':
            stmts.append(tok)
            i += 1
        elif tok[0] == 'FOR':
            body = []
            i += 1
            while i < len(tokens) and tokens[i][0] != 'END':
                body.append(tokens[i])
                i += 1
            if i < len(tokens) and tokens[i][0] == 'END':
                i += 1  # skip END
            stmts.append(('FOR', tok[1], tok[2], tok[3], body))
        elif tok[0] == 'EXIT':
            stmts.append(tok)
            i += 1
        elif tok[0] == 'END':
            i += 1
        else:
            i += 1
    return stmts

def compile_to_asm(stmts):
    code = []
    data = []
    strings = []
    
    # Simple register allocation: r12, r13, r14, r15 for user vars
    # rax, rcx, rdx, rsi, rdi, rbp used for temp
    var_reg = {}
    next_reg = 0
    reg_names = ['%r12', '%r13', '%r14', '%r15']
    labels = [0]
    
    def alloc_var(v):
        nonlocal next_reg
        if v not in var_reg:
            var_reg[v] = reg_names[next_reg % 4]
            next_reg += 1
        return var_reg[v]
    
    def new_label():
        labels[0] += 1
        return f'L{labels[0]}'
    
    def resolve(v):
        """Get register or immediate for value"""
        try:
            return f'${int(v)}'
        except:
            # It's a variable - get its register directly
            if v in var_reg:
                return var_reg[v]
            # Unknown variable, use r12
            return '%r12'
    
    def compile_stmt(stmt):
        op = stmt[0]
        
        if op == 'SKRIV':
            s = stmt[1]
            strings.append(s)
            idx = len(strings) - 1
            code.append(f"    lea msg_{idx}(%rip), %rsi")
            code.append(f"    mov ${len(s)}, %edx")
            code.append(f"    mov $1, %edi")
            code.append(f"    mov $1, %eax")
            code.append(f"    syscall")
        
        elif op == 'SKRIV_VAR':
            # For now, just print a newline
            strings.append(".")
            idx = len(strings) - 1
            code.append(f"    lea msg_{idx}(%rip), %rsi")
            code.append(f"    mov $1, %edx")
            code.append(f"    mov $1, %edi")
            code.append(f"    mov $1, %eax")
            code.append(f"    syscall")
            code.append(f"    mov $5, %edx  # placeholder len")
            code.append(f"    mov $1, %edi")
            code.append(f"    mov $1, %eax")
            code.append(f"    syscall")
        
        elif op == 'SET':
            var = stmt[1]
            val = stmt[2]
            reg = alloc_var(var)
            r = resolve(val)
            code.append(f"    mov {r}, {reg}  # {var} = {val}")
        
        elif op == 'PLUS':
            var = stmt[1]
            left = stmt[2]
            right = stmt[3]
            reg = alloc_var(var)
            r1 = resolve(left)
            r2 = resolve(right)
            # Use rcx as temp, then store to destination
            code.append(f"    mov {r1}, %rcx  # {var} = {left} + {right}")
            code.append(f"    add {r2}, %rcx")
            code.append(f"    mov %rcx, {reg}")
        
        elif op == 'FOR':
            var = stmt[1]
            start = stmt[2]
            end = stmt[3]
            body = stmt[4]
            
            reg = alloc_var(var)
            loop_start = new_label()
            loop_end = new_label()
            
            # Initialize
            code.append(f"    mov ${start}, {reg}  # for {var}")
            code.append(f"{loop_start}:")
            code.append(f"    cmp ${end}, {reg}")
            code.append(f"    jge {loop_end}")
            
            # Loop body
            for s in body:
                compile_stmt(s)
            
            code.append(f"    inc {reg}")
            code.append(f"    jmp {loop_start}")
            code.append(f"{loop_end}:")
        
        elif op == 'EXIT':
            code.append(f"    mov ${stmt[1]}, %edi")
            code.append(f"    mov $60, %eax")
            code.append(f"    syscall")
    
    # Compile all
    for stmt in stmts:
        compile_stmt(stmt)
    
    # Default exit if not present
    if not any(s[0] == 'EXIT' for s in stmts):
        code.append(f"    mov $0, %edi")
        code.append(f"    mov $60, %eax")
        code.append(f"    syscall")
    
    # Data section
    data.append(".data")
    for i, s in enumerate(strings):
        escaped = s.replace('\\', '\\\\').replace('\n', '\\n').replace('"', '\\"')
        data.append(f"msg_{i}: .ascii \"{escaped}\\n\\0\"")
    
    # Output
    out = []
    out.append(".text")
    out.append(".globl _start")
    out.append("_start:")
    out.extend(code)
    out.append("")
    out.extend(data)
    
    return '\n'.join(out)

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 hiuh-native.py <input.hiuh> [output]")
        return
    
    if sys.argv[1] == '-' or sys.argv[1] == '--stdin':
        src = sys.stdin.read()
    else:
        src = open(sys.argv[1]).read()
    
    tokens = tokenize(src)
    stmts = parse(tokens)
    asm = compile_to_asm(stmts)
    
    if '--asm' in sys.argv:
        print(asm)
        return
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.s', delete=False) as f:
        f.write(asm)
        asm_file = f.name
    
    obj_file = asm_file + '.o'
    output = sys.argv[2] if len(sys.argv) > 2 else './hiuh-runner'
    
    try:
        r = subprocess.run(['as', '-o', obj_file, asm_file], capture_output=True, text=True)
        if r.returncode != 0:
            print(f"as error:\n{r.stderr}")
            return
        
        r = subprocess.run(['ld', '-o', output, obj_file], capture_output=True, text=True)
        if r.returncode != 0:
            print(f"ld error:\n{r.stderr}")
            return
        
        import stat
        os.chmod(output, os.stat(output).st_mode | stat.S_IXUSR)
        print(f"Kompilerade till {output}")
    finally:
        for f in [asm_file, obj_file]:
            if os.path.exists(f):
                os.unlink(f)

if __name__ == '__main__':
    main()