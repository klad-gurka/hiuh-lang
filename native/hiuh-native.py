#!/usr/bin/env python3
"""
HIUH Native Compiler - x86-64 med full WASI-paritet
"""

import sys
import subprocess
import tempfile
import os

def compile_hiuh_to_asm(src: str) -> str:
    """Compile HIUH to x86-64 assembly"""
    
    lines = []
    buffers = []
    has_exit = [False]
    exit_code = ['0']
    
    lines.append(".text")
    lines.append(".globl _start")
    lines.append("_start:")
    
    for line in src.split('\n'):
        stripped = line.lstrip()
        if not stripped:
            continue
        words = stripped.split()
        if not words:
            continue
        
        first = words[0]
        
        # SKRIV
        if first == 'Skriv' and len(words) > 1:
            msg = ' '.join(words[1:]) + '\n'
            buffers.append(msg.encode('utf-8'))
            idx = len(buffers) - 1
            lines.append(f"    mov $1, %rax        # write")
            lines.append(f"    mov $1, %rdi        # stdout")
            lines.append(f"    lea msg_{idx}(%rip), %rsi")
            lines.append(f"    mov ${len(msg)}, %rdx")
            lines.append(f"    syscall")
        
        # SÄTT x till ...
        elif first == 'Sätt' and len(words) >= 4:
            var = words[1]
            rest = ' '.join(words[3:])
            
            if 'input' in rest:
                lines.append(f"    mov $0, %rax        # read")
                lines.append(f"    xor %rdi, %rdi        # stdin")
                lines.append(f"    lea input_buf(%rip), %rsi")
                lines.append(f"    mov $256, %rdx")
                lines.append(f"    syscall")
            
            elif 'slumptal' in rest:
                lines.append(f"    mov $2, %rax        # open /dev/urandom")
                lines.append(f"    lea dev_urandom(%rip), %rdi")
                lines.append(f"    xor %rsi, %rsi")
                lines.append(f"    syscall")
                lines.append(f"    mov %rax, %r12        # save fd")
                lines.append(f"    mov $0, %rax        # read")
                lines.append(f"    mov %r12, %rdi")
                lines.append(f"    lea rand_buf(%rip), %rsi")
                lines.append(f"    mov $8, %rdx")
                lines.append(f"    syscall")
                lines.append(f"    mov %r12, %rdi")
                lines.append(f"    mov $3, %rax        # close")
                lines.append(f"    syscall")
                lines.append(f"    lea rand_buf(%rip), %rsi")
                lines.append(f"    mov (%rsi), %rax")
                lines.append(f"    mov $100, %rcx")
                lines.append(f"    xor %rdx, %rdx")
                lines.append(f"    div %rcx")
                # %rdx contains 0-99 random
        
        # JAG MÅSTE GÅ NU - exit
        elif first == 'JagMåsteGåNu':
            has_exit[0] = True
            if len(words) > 1 and words[1].isdigit():
                exit_code[0] = words[1]
            lines.append(f"    mov ${exit_code[0]}, %rdi        # exit code")
            lines.append(f"    mov $60, %rax        # sys_exit")
            lines.append(f"    syscall")
    
    # Implicit exit(0) if no explicit exit
    if not has_exit[0]:
        lines.append("    mov $60, %rax       # sys_exit")
        lines.append("    xor %rdi, %rdi        # exit(0)")
        lines.append("    syscall")
    
    lines.append(".data")
    lines.append("input_buf: .skip 256")
    lines.append("dev_urandom: .asciz \"/dev/urandom\"")
    for i, msg in enumerate(buffers):
        esc = msg.decode('utf-8', errors='replace').replace('\n', '\\n').replace('\\', '\\\\').replace('"', '\\"')
        lines.append(f"msg_{i}: .ascii \"{esc}\"")
    
    lines.append(".bss")
    lines.append(".align 8")
    lines.append("rand_buf: .skip 8")
    
    return '\n'.join(lines)

def assemble_and_link(asm_code: str, output: str) -> bool:
    with tempfile.NamedTemporaryFile(mode='w', suffix='.s', delete=False) as f:
        f.write(asm_code)
        asm_file = f.name
    
    obj = asm_file + '.o'
    
    try:
        r = subprocess.run(['as', '-o', obj, asm_file], capture_output=True)
        if r.returncode != 0:
            print(f"as error: {r.stderr.decode()}")
            return False
        
        r = subprocess.run(['ld', '-o', output, obj], capture_output=True)
        if r.returncode != 0:
            print(f"ld error: {r.stderr.decode()}")
            return False
        
        return True
    finally:
        for f in [asm_file, obj]:
            if os.path.exists(f):
                os.unlink(f)

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 hiuh-native.py <input.hiuh> [output]")
        return
    
    src = open(sys.argv[1]).read()
    output = sys.argv[2] if len(sys.argv) > 2 else 'hiuh-runner'
    
    asm = compile_hiuh_to_asm(src)
    
    if '--asm' in sys.argv:
        print(asm)
        return
    
    if assemble_and_link(asm, output):
        import stat
        os.chmod(output, os.stat(output).st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
        print(f"Kompilerade till {output}")
    else:
        print("Misslyckades")

if __name__ == '__main__':
    main()