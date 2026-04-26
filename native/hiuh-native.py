#!/usr/bin/env python3
"""
HIUH Native Compiler - Generate x86-64 assembly, assemble with `as` and `ld`
"""

import sys
import subprocess
import tempfile
import os

def compile_hiuh_to_asm(src: str) -> str:
    """Compile HIUH to x86-64 assembly"""
    
    lines = []
    lines.append(".text")
    lines.append(".globl _start")
    lines.append("_start:")
    
    msg_count = 0
    messages = []
    
    for line in src.split('\n'):
        stripped = line.lstrip()
        if not stripped:
            continue
        words = stripped.split()
        
        if words[0] == 'Skriv' and len(words) > 1:
            msg = ' '.join(words[1:]) + '\n'
            msg_label = f"msg_{msg_count}"
            messages.append((msg_label, msg.encode('utf-8')))
            
            # write(fd=1, msg, len)
            lines.append(f"    mov $1, %rax        # sys_write")
            lines.append(f"    mov $1, %rdi        # stdout")
            lines.append(f"    lea {msg_label}(%rip), %rsi")
            lines.append(f"    mov ${len(msg)}, %rdx")
            lines.append(f"    syscall")
            
            msg_count += 1
    
    # exit(0)
    lines.append("    mov $60, %rax       # sys_exit")
    lines.append("    mov $0, %rdi")
    lines.append("    syscall")
    
    # Data section
    lines.append(".data")
    for label, msg in messages:
        lines.append(f"{label}:")
        lines.append(f"    .ascii \"{msg.decode('utf-8', errors='replace').replace('\\n', '\\n').replace('\\0', '\\\\0')}\"")
    
    return '\n'.join(lines)

def assemble_and_link(asm_code: str, output: str) -> bool:
    """Assemble assembly to ELF executable using as + ld"""
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.s', delete=False) as f:
        f.write(asm_code)
        asm_file = f.name
    
    obj_file = asm_file + '.o'
    
    try:
        # Assemble
        r = subprocess.run(['as', '-o', obj_file, asm_file], capture_output=True)
        if r.returncode != 0:
            print(f"Assembler error: {r.stderr.decode()}")
            return False
        
        # Link
        r = subprocess.run(['ld', '-o', output, obj_file], capture_output=True)
        if r.returncode != 0:
            print(f"Linker error: {r.stderr.decode()}")
            return False
        
        return True
        
    finally:
        for f in [asm_file, obj_file]:
            if os.path.exists(f):
                os.unlink(f)

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 hiuh-native.py <input.hiuh> [output]")
        return
    
    src_file = sys.argv[1]
    output = sys.argv[2] if len(sys.argv) > 2 else 'hiuh-runner'
    
    with open(src_file) as f:
        src = f.read()
    
    asm = compile_hiuh_to_asm(src)
    
    if '--asm' in sys.argv:
        print(asm)
        return
    
    if assemble_and_link(asm, output):
        import stat
        os.chmod(output, os.stat(output).st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
        print(f"Kompilerade till {output}")
        print(f"Size: {os.path.getsize(output)} bytes")
    else:
        print("Kompilering misslyckades")

if __name__ == '__main__':
    main()