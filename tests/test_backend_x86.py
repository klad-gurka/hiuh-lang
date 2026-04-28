#!/usr/bin/env python3
"""Tests for x86 backend - generates x86 Linux assembly from IR"""

import sys
import io
import contextlib
sys.path.insert(0, 'src')

from hiuh.backend.x86 import compile_ir, alloc_reg, new_label, REG_MAP, STRINGS, LABEL_CNT

def reset_state():
    """Reset global state before each test"""
    global REG_MAP, STRINGS, LABEL_CNT, NEXT_REG
    from hiuh.backend import x86
    x86.REG_MAP.clear()
    x86.STRINGS.clear()
    x86.LABEL_CNT = 0
    x86.NEXT_REG = 0

def capture_asm(ir):
    """Compile IR and capture assembly output"""
    reset_state()
    output = io.StringIO()
    with contextlib.redirect_stdout(output):
        compile_ir(ir)
    return output.getvalue()

def test_set_integer():
    """SET x 5 → mov $5, %r12"""
    asm = capture_asm([('SET', 'x', 5)])
    assert 'mov $5, %r12' in asm, f"Got: {asm}"

def test_set_multiple_vars():
    """Multiple SET statements"""
    asm = capture_asm([('SET', 'x', 5), ('SET', 'y', 10)])
    assert 'mov $5, %r12' in asm
    assert 'mov $10, %r13' in asm

def test_set_plus():
    """SET x ('+', 'a', 3) → mov a; add $3"""
    asm = capture_asm([('SET', 'x', ('+', 'a', 3))])
    assert 'mov' in asm
    assert 'add $3' in asm

def test_for_loop():
    """FOR i 0 10 body → loop with labels"""
    asm = capture_asm([('FOR', 'i', 0, 10, [])])
    assert '.L1:' in asm  # start label
    assert '.L2:' in asm  # end label
    assert 'mov $0' in asm  # init
    assert 'cmp $10' in asm  # comparison
    assert 'jge .L2' in asm  # exit if >= end
    assert 'jmp .L1' in asm  # loop back

def test_for_with_body():
    """FOR with SET in body"""
    asm = capture_asm([('FOR', 'i', 0, 3, [('SET', 'x', 5)])])
    assert '.L1:' in asm
    assert 'mov $5' in asm

def test_if_eq():
    """IF (x, '==', 0) → cmp + je"""
    asm = capture_asm([('IF', ('x', '==', '0'), [('SET', 'y', 1)])])
    assert 'cmp $0' in asm
    assert 'jne' in asm  # jump if NOT equal

def test_if_less():
    """IF (x, '<', 5)"""
    asm = capture_asm([('IF', ('x', '<', 5), [])])
    assert 'cmp $5' in asm

def test_if_greater():
    """IF (x, '>', 0)"""
    asm = capture_asm([('IF', ('x', '>', 0), [])])
    assert 'cmp $0' in asm

def test_exit():
    """EXIT → syscall"""
    asm = capture_asm([('EXIT', 0)])
    assert 'mov $60, %rax' in asm
    assert 'syscall' in asm

def test_break():
    """BREAK → jmp"""
    asm = capture_asm([('BREAK',)])
    assert 'jmp' in asm

def test_prologue():
    """Verify function prologue"""
    asm = capture_asm([('SET', 'x', 1)])
    assert 'push %r12' in asm
    assert 'push %r13' in asm
    assert 'push %rbp' in asm

def test_epilogue():
    """Verify function epilogue"""
    asm = capture_asm([('SET', 'x', 1)])
    assert 'xor %eax, %eax' in asm
    assert 'pop %rbp' in asm
    assert 'ret' in asm

def test_data_section():
    """Verify data section is generated"""
    asm = capture_asm([('SET', 'x', 1)])
    assert '.data' in asm
    assert '.bss' in asm
    assert 'input_buf: .skip 256' in asm

def test_multiple_for_loops():
    """Two FOR loops get different labels"""
    asm = capture_asm([
        ('FOR', 'i', 0, 5, []),
        ('FOR', 'j', 0, 10, [])
    ])
    # Should have 4 labels (2 starts, 2 ends)
    assert asm.count('.L') >= 4

def test_nested_if_in_for():
    """IF inside FOR"""
    asm = capture_asm([
        ('FOR', 'i', 0, 5, [
            ('IF', ('i', '==', 3), [('EXIT', 0)])
        ])
    ])
    # FOR generates loop with labels
    assert '.L' in asm
    assert 'jge' in asm  # exit condition
    assert 'cmp $3' in asm

def test_alloc_reg_different_vars():
    """Different variables get different registers"""
    reset_state()
    r1 = alloc_reg('x')
    r2 = alloc_reg('y')
    r3 = alloc_reg('z')
    assert r1 != r2
    assert r2 != r3
    assert r1 != r3

def test_alloc_reg_same_var():
    """Same variable gets same register"""
    reset_state()
    r1 = alloc_reg('x')
    r2 = alloc_reg('x')
    assert r1 == r2


def test_set_minus():
    """SET x ('-', 'a', 3) → mov a; sub $3"""
    from hiuh.backend import x86
    x86.REG_MAP.clear()
    x86.STRINGS.clear()
    x86.LABEL_CNT = 0
    x86.NEXT_REG = 0
    output = io.StringIO()
    with contextlib.redirect_stdout(output):
        compile_ir([('SET', 'x', ('-', 'a', 3))])
    asm = output.getvalue()
    assert 'sub $3' in asm, f"Got: {asm}"

def test_set_times():
    """SET x ('*', 'a', 2) → mov a; imul"""
    from hiuh.backend import x86
    x86.REG_MAP.clear()
    x86.STRINGS.clear()
    x86.LABEL_CNT = 0
    x86.NEXT_REG = 0
    output = io.StringIO()
    with contextlib.redirect_stdout(output):
        compile_ir([('SET', 'x', ('*', 'a', 2))])
    asm = output.getvalue()
    assert 'imul' in asm, f"Got: {asm}"

def test_set_div():
    """SET x ('/', 'a', 4) → mov a; idiv"""
    from hiuh.backend import x86
    x86.REG_MAP.clear()
    x86.STRINGS.clear()
    x86.LABEL_CNT = 0
    x86.NEXT_REG = 0
    output = io.StringIO()
    with contextlib.redirect_stdout(output):
        compile_ir([('SET', 'x', ('/', 'a', 4))])
    asm = output.getvalue()
    assert 'idiv' in asm, f"Got: {asm}"
if __name__ == '__main__':
    test_set_integer()
    test_set_multiple_vars()
    test_set_plus()
    test_set_minus()
    test_set_times()
    test_set_div()
    test_for_loop()
    test_for_with_body()
    test_if_eq()
    test_if_less()
    test_if_greater()
    test_exit()
    test_break()
    test_prologue()
    test_epilogue()
    test_data_section()
    test_multiple_for_loops()
    test_nested_if_in_for()
    test_alloc_reg_different_vars()
    test_alloc_reg_same_var()
    print("Alla x86 backend-tester OK!")
