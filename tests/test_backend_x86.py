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
    asm = capture_asm([('SÄTT', 'x', 5)])
    assert 'mov $5, %r12' in asm, f"Got: {asm}"

def test_set_multiple_vars():
    """Multiple SET statements"""
    asm = capture_asm([('SÄTT', 'x', 5), ('SÄTT', 'y', 10)])
    assert 'mov $5, %r12' in asm
    assert 'mov $10, %r13' in asm

def test_set_plus():
    """SET x ('PLUSS', 'a', 3) → mov a; add $3"""
    asm = capture_asm([('SÄTT', 'x', ('PLUSS', 'a', 3))])
    assert 'mov' in asm
    assert 'add $3' in asm

def test_for_loop():
    """FOR i 0 10 body → loop with labels"""
    asm = capture_asm([('FÖR', 'i', 0, 10, [])])
    assert '.L1:' in asm  # start label
    assert '.L2:' in asm  # end label
    assert 'mov $0' in asm  # init
    assert 'cmp $10' in asm  # comparison
    assert 'jge .L2' in asm  # exit if >= end
    assert 'jmp .L1' in asm  # loop back

def test_for_with_body():
    """FOR with SET in body"""
    asm = capture_asm([('FÖR', 'i', 0, 3, [('SÄTT', 'x', 5)])])
    assert '.L1:' in asm
    assert 'mov $5' in asm

def test_if_eq():
    """IF (x, 'likaMed', 0) → cmp + jne"""
    asm = capture_asm([('OM', ('x', 'likaMed', '0'), [('SÄTT', 'y', 1)])])
    assert 'cmp $0' in asm
    assert 'jne' in asm  # jump if NOT equal

def test_if_less():
    """IF (x, 'mindre', 5)"""
    asm = capture_asm([('OM', ('x', 'mindre', 5), [])])
    assert 'cmp $5' in asm

def test_if_greater():
    """IF (x, 'större', 0)"""
    asm = capture_asm([('OM', ('x', 'större', 0), [])])
    assert 'cmp $0' in asm

def test_exit():
    """EXIT → syscall"""
    asm = capture_asm([('HEJDÅ',)])
    assert 'mov $60, %rax' in asm
    assert 'syscall' in asm

def test_break():
    """BREAK → jmp"""
    asm = capture_asm([('BRYT',)])
    assert 'jmp' in asm

def test_prologue():
    """Verify function prologue"""
    asm = capture_asm([('SÄTT', 'x', 1)])
    assert 'push %r12' in asm
    assert 'push %r13' in asm
    assert 'push %rbp' in asm

def test_epilogue():
    """Verify function epilogue"""
    asm = capture_asm([('SÄTT', 'x', 1)])
    assert 'xor %eax, %eax' in asm
    assert 'pop %rbp' in asm
    assert 'ret' in asm

def test_data_section():
    """Verify data section is generated"""
    asm = capture_asm([('SÄTT', 'x', 1)])
    assert '.data' in asm
    assert '.bss' in asm
    assert 'input_buf: .skip 256' in asm

def test_multiple_for_loops():
    """Two FOR loops get different labels"""
    asm = capture_asm([
        ('FÖR', 'i', 0, 5, []),
        ('FÖR', 'j', 0, 10, [])
    ])
    # Should have 4 labels (2 starts, 2 ends)
    assert asm.count('.L') >= 4

def test_nested_if_in_for():
    """IF inside FOR"""
    asm = capture_asm([
        ('FÖR', 'i', 0, 5, [
            ('OM', ('i', 'likaMed', 3), [('HEJDÅ',)])
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


def test_if_not_eq():
    """IF (x, 'inteLikaMed', 0)"""
    asm = capture_asm([('OM', ('x', 'inteLikaMed', 0), [])])
    assert 'cmp $0' in asm
    assert 'je' in asm  # jump if equal (condition failed)

def test_if_less_or_eq():
    """IF (x, 'mindreLikaMed', 5)"""
    asm = capture_asm([('OM', ('x', 'mindreLikaMed', 5), [])])
    assert 'cmp $5' in asm
    assert 'jg' in asm  # jump if greater → exit condition if NOT <=

def test_if_greater_or_eq():
    """IF (x, 'störreLikaMed', 0)"""
    asm = capture_asm([('OM', ('x', 'störreLikaMed', 0), [])])
    assert 'cmp $0' in asm
    assert 'jl' in asm  # jump if less → exit condition if NOT >=

def test_set_minus():
    """SET x ('MINUS', 'a', 3) → mov a; sub $3"""
    from hiuh.backend import x86
    x86.REG_MAP.clear()
    x86.STRINGS.clear()
    x86.LABEL_CNT = 0
    x86.NEXT_REG = 0
    output = io.StringIO()
    with contextlib.redirect_stdout(output):
        compile_ir([('SÄTT', 'x', ('MINUS', 'a', 3))])
    asm = output.getvalue()
    assert 'sub $3' in asm, f"Got: {asm}"

def test_set_times():
    """SET x ('GÅNGER', 'a', 2) → mov a; imul"""
    from hiuh.backend import x86
    x86.REG_MAP.clear()
    x86.STRINGS.clear()
    x86.LABEL_CNT = 0
    x86.NEXT_REG = 0
    output = io.StringIO()
    with contextlib.redirect_stdout(output):
        compile_ir([('SÄTT', 'x', ('GÅNGER', 'a', 2))])
    asm = output.getvalue()
    assert 'imul' in asm, f"Got: {asm}"

def test_set_div():
    """SET x ('DELA', 'a', 4) → mov a; idiv"""
    from hiuh.backend import x86
    x86.REG_MAP.clear()
    x86.STRINGS.clear()
    x86.LABEL_CNT = 0
    x86.NEXT_REG = 0
    output = io.StringIO()
    with contextlib.redirect_stdout(output):
        compile_ir([('SÄTT', 'x', ('DELA', 'a', 4))])
    asm = output.getvalue()
    assert 'idiv' in asm, f"Got: {asm}"

def test_file_open():
    """FILE_OPEN filename 'r' → sys_open call"""
    asm = capture_asm([('ÖPPNA_FIL', 'data.txt', 'r')])
    assert 'sys_open' in asm or 'mov $2, %rax' in asm, f"Got: {asm}"

def test_file_write():
    """FILE_WRITE filename data → sys_write call"""
    asm = capture_asm([('SKRIV_FIL', 'resultat.txt', '')])
    assert 'sys_write' in asm or 'mov $1, %rax' in asm, f"Got: {asm}"

def test_file_read():
    """FILE_READ filepath var → sys_open + sys_read + sys_close"""
    asm = capture_asm([('LÄS_FIL', 'data.txt', 'buf')])
    assert 'sys_open' in asm or 'mov $2, %rax' in asm, f"Got: {asm}"
    assert 'sys_read' in asm or 'mov $0, %rax' in asm, f"Got: {asm}"
    assert 'sys_close' in asm or 'mov $3, %rax' in asm, f"Got: {asm}"

def test_read_line():
    """READ_LINE var → sys_read into input_buf"""
    asm = capture_asm([('LÄS_RAD', 'namn')])
    assert 'sys_read' in asm or 'mov $0, %rax' in asm, f"Got: {asm}"
    assert 'input_buf' in asm, f"Got: {asm}"

def test_skriv_radbryt():
    """SKRIV ('RADBRYT',) → newline via msg_nl"""
    asm = capture_asm([('SKRIV', ('RADBRYT',))])
    assert 'msg_nl' in asm
    assert 'syscall' in asm

def test_skriv_variabel():
    """SKRIV ('VARIABEL', 'x') → print variable value"""
    asm = capture_asm([('SKRIV', ('VARIABEL', 'x'))])
    assert 'syscall' in asm
    assert 'num_buf' in asm

def test_skriv_heltal():
    """SKRIV ('HELTAL', 42) → print integer literal"""
    asm = capture_asm([('SKRIV', ('HELTAL', 42))])
    assert 'mov $42, %rax' in asm
    assert 'syscall' in asm

def test_skriv_text():
    """SKRIV ('TEXT', 'hej') → print string"""
    asm = capture_asm([('SKRIV', ('TEXT', 'hej'))])
    assert 'msg_0' in asm
    assert 'syscall' in asm

def test_skriv_pluss():
    """SKRIV ('PLUSS', 'x', 1) → compute and print expression"""
    asm = capture_asm([('SKRIV', ('PLUSS', 'x', 1))])
    assert 'add' in asm
    assert 'syscall' in asm

def test_skriv_minus():
    """SKRIV ('MINUS', 'x', 1)"""
    asm = capture_asm([('SKRIV', ('MINUS', 'x', 1))])
    assert 'sub' in asm
    assert 'syscall' in asm

def test_skriv_ganger():
    """SKRIV ('GÅNGER', 'x', 2)"""
    asm = capture_asm([('SKRIV', ('GÅNGER', 'x', 2))])
    assert 'imul' in asm
    assert 'syscall' in asm

def test_skriv_dela():
    """SKRIV ('DELA', 'x', 2)"""
    asm = capture_asm([('SKRIV', ('DELA', 'x', 2))])
    assert 'idiv' in asm
    assert 'syscall' in asm

def test_skriv_radbryt_only():
    """SKRIV with RADBRYT generates newline syscall only"""
    asm = capture_asm([('SKRIV', ('RADBRYT',))])
    assert 'msg_nl' in asm
    # RADBRYT does NOT use num_buf - it just prints the newline string
    # num_buf is for integer printing
    assert 'lea num_buf(%rip), %rsi' not in asm

def test_skriv_text_with_expr():
    """Multiple SKRIV statements with different expr types"""
    asm = capture_asm([
        ('SÄTT', 'x', 5),
        ('SKRIV', ('VARIABEL', 'x')),
        ('SKRIV', ('TEXT', 'hej')),
        ('SKRIV', ('RADBRYT',)),
    ])
    assert 'syscall' in asm

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
    test_if_not_eq()
    test_if_less_or_eq()
    test_if_greater_or_eq()
    test_exit()
    test_break()
    test_prologue()
    test_epilogue()
    test_data_section()
    test_multiple_for_loops()
    test_nested_if_in_for()
    test_alloc_reg_different_vars()
    test_alloc_reg_same_var()
    test_file_open()
    test_file_write()
    test_file_read()
    test_read_line()
    test_skriv_radbryt()
    test_skriv_variabel()
    test_skriv_heltal()
    test_skriv_text()
    test_skriv_pluss()
    test_skriv_minus()
    test_skriv_ganger()
    test_skriv_dela()
    test_skriv_radbryt_only()
    test_skriv_text_with_expr()
    print("Alla x86 backend-tester OK!")

def test_while_basic():
    """WHILE (x, 'mindre', 5) → loop with cmp + jge"""
    asm = capture_asm([('MEDAN', ('x', 'mindre', 5), [])])
    assert '.L1:' in asm  # start label
    assert '.L2:' in asm  # end label
    assert 'cmp $5' in asm
    assert 'jge .L2' in asm  # exit if >= 5

def test_while_with_body():
    """WHILE with SET in body"""
    asm = capture_asm([('MEDAN', ('x', 'mindre', 3), [('SÄTT', 'x', ('+', 'x', 1))])])
    assert '.L1:' in asm
    assert '.L2:' in asm
    assert 'add $1' in asm

def test_while_break():
    """WHILE with BREAK generates BREAK label in stack"""
    import io, contextlib
    import hiuh.backend.x86 as x86
    x86.REG_MAP.clear()
    x86.STRINGS.clear()
    x86.LABEL_CNT = 0
    x86.NEXT_REG = 0
    x86.BREAK_STACK.clear()
    output = io.StringIO()
    with contextlib.redirect_stdout(output):
        x86.compile_ir([('MEDAN', ('x', 'mindre', 10), [('BRYT',)])])
    asm = output.getvalue()
    assert 'jmp .L2' in asm  # BREAK jumps to end label

def test_while_nested_if():
    """WHILE with IF+BREAK inside"""
    asm = capture_asm([
        ('MEDAN', ('x', 'mindre', 10), [
            ('OM', ('x', 'likaMed', 5), [('BRYT',)])
        ])
    ])
    assert '.L1:' in asm
    assert 'jge' in asm

def test_while_eq():
    """WHILE (x, 'likaMed', 0)"""
    asm = capture_asm([('MEDAN', ('x', 'likaMed', 0), [])])
    assert 'cmp $0' in asm
    assert 'jne .L' in asm

def test_func_def_basic():
    """FUNC_DEF: function definition generates function label"""
    asm = capture_asm([
        ('GREJ', 'dubbla', ['x'], [
            ('SÄTT', 'resultat', ('*', 'x', 2)),
            ('GE', 'resultat')
        ])
    ])
    assert 'func_dubbla:' in asm
    assert 'ret' in asm

def test_call_basic():
    """CALL: function call generates call instruction"""
    asm = capture_asm([
        ('SÄTT', 'b', ('ANROPA', 'dubbla', ['a']))
    ])
    assert 'call func_dubbla' in asm

def test_func_def_and_call():
    """FUNC_DEF + CALL end-to-end"""
    asm = capture_asm([
        ('GREJ', 'dubbla', ['x'], [
            ('SÄTT', 'resultat', ('*', 'x', 2)),
            ('GE', 'resultat')
        ]),
        ('SÄTT', 'a', 5),
        ('SÄTT', 'b', ('ANROPA', 'dubbla', ['a']))
    ])
    assert 'func_dubbla:' in asm
    assert 'call func_dubbla' in asm

def test_list_get():
    """LIST_GET: load element at index from list"""
    asm = capture_asm([('HÄMTA_INDEX', 'lst', 0)])
    assert 'HÄMTA_INDEX' in asm
    assert '%rax' in asm  # loads into %rax

def test_list_get_with_idx_var():
    """LIST_GET with variable index"""
    asm = capture_asm([('HÄMTA_INDEX', 'lst', 'i')])
    assert 'HÄMTA_INDEX' in asm

def test_set_list_get():
    """SET x = LIST_GET lst 0 → load element into register"""
    asm = capture_asm([('SÄTT', 'x', ('HÄMTA_INDEX', 'lst', 0))])
    assert 'HÄMTA_INDEX' in asm
    assert 'mov' in asm

def test_byt_ut():
    """BYT_UT: replace element at index"""
    asm = capture_asm([('BYT_UT', 'lst', 0, '99')])
    assert 'BYT_UT' in asm
    assert 'mov' in asm

def test_byt_ut_with_var_index():
    """BYT_UT with variable index"""
    asm = capture_asm([('BYT_UT', 'lst', 'i', '42')])
    assert 'BYT_UT' in asm

def test_ta_bort_index():
    """TA_BORT_INDEX: remove element at index"""
    asm = capture_asm([('TA_BORT_INDEX', 'lst', 0)])
    assert 'TA_BORT_INDEX' in asm
    assert 'mov' in asm
