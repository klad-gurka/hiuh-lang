#!/usr/bin/env python3
"""Tests for parse.py - IR generation with indentation-based blocks"""

import sys
sys.path.insert(0, 'src')

from hiuh.parse import parse_tokens
from hiuh.tokenize import tokenize

def test_set_integer():
    """sätt x till 5 → SET"""
    lines = list(tokenize("sätt x till 5"))
    ir = parse_tokens(lines)
    assert ir == [('SET', 'x', 5)], f"Got {ir}"

def test_set_plus():
    """sätt x till a pluss 3 → SET with expression"""
    lines = list(tokenize("sätt x till a pluss 3"))
    ir = parse_tokens(lines)
    assert ir == [('SET', 'x', ('+', 'a', 3))], f"Got {ir}"

def test_set_minus():
    """sätt x till a minus 3 → SET with expression"""
    lines = list(tokenize("sätt x till a minus 3"))
    ir = parse_tokens(lines)
    assert ir == [('SET', 'x', ('-', 'a', 3))], f"Got {ir}"

def test_set_times():
    """sätt x till a gånger 3 → SET with expression"""
    lines = list(tokenize("sätt x till a gånger 3"))
    ir = parse_tokens(lines)
    assert ir == [('SET', 'x', ('*', 'a', 3))], f"Got {ir}"

def test_set_div():
    """sätt x till a delat 3 → SET with expression"""
    lines = list(tokenize("sätt x till a delat 3"))
    ir = parse_tokens(lines)
    assert ir == [('SET', 'x', ('/', 'a', 3))], f"Got {ir}"

def test_set_number_plus():
    """sätt x till 5 pluss 3 → SET with number + number"""
    lines = list(tokenize("sätt x till 5 pluss 3"))
    ir = parse_tokens(lines)
    assert ir == [('SET', 'x', ('+', 5, 3))], f"Got {ir}"

def test_for_loop():
    """för x från 0 till 10"""
    src = """för x från 0 till 10
    skriv x"""
    lines = list(tokenize(src))
    ir = parse_tokens(lines)
    assert len(ir) == 1
    assert ir[0][0] == 'FOR'
    assert ir[0][1] == 'x'
    assert ir[0][2] == 0
    assert ir[0][3] == 10
    assert len(ir[0][4]) == 1  # body has 1 statement

def test_if_statement():
    """om x är 0"""
    src = """om x är 0
    skriv x"""
    lines = list(tokenize(src))
    ir = parse_tokens(lines)
    assert len(ir) == 1
    assert ir[0][0] == 'IF'
    assert ir[0][1] == ('x', 'likaMed', '0')

def test_if_less():
    """om x är mindre än 5"""
    src = """om x är mindre än 5
    skriv x"""
    lines = list(tokenize(src))
    ir = parse_tokens(lines)
    assert ir[0][1] == ('x', 'mindre', '5')

def test_if_greater():
    """om x är större än 0"""
    src = """om x är större än 0
    skriv x"""
    lines = list(tokenize(src))
    ir = parse_tokens(lines)
    assert ir[0][1] == ('x', 'större', '0')

def test_if_not():
    """om x är inte 0"""
    src = """om x är inte 0
    skriv x"""
    lines = list(tokenize(src))
    ir = parse_tokens(lines)
    assert ir[0][1] == ('x', 'inteLikaMed', '0')

def test_if_less_or_eq():
    """om x är mindre eller 5"""
    src = """om x är mindre eller 5
    skriv x"""
    lines = list(tokenize(src))
    ir = parse_tokens(lines)
    assert ir[0][1] == ('x', 'mindreLikaMed', '5')

def test_if_greater_or_eq():
    """om x är större eller 0"""
    src = """om x är större eller 0
    skriv x"""
    lines = list(tokenize(src))
    ir = parse_tokens(lines)
    assert ir[0][1] == ('x', 'störreLikaMed', '0')

def test_break():
    """bryt"""
    src = """om x är 0
    bryt"""
    lines = list(tokenize(src))
    ir = parse_tokens(lines)
    assert ir[0][2][0] == ('BREAK',)

def test_exit():
    """jag gå nu"""
    lines = list(tokenize("jag gå nu"))
    ir = parse_tokens(lines)
    assert ir == [('EXIT', 0)]

def test_read():
    """läs"""
    lines = list(tokenize("läs"))
    ir = parse_tokens(lines)
    assert ir == [('READ', 'input_buf')]

def test_skriv():
    """skriv x"""
    lines = list(tokenize("skriv x"))
    ir = parse_tokens(lines)
    assert ir == [('SKRIV', 'x')]

def test_skriv_nl():
    """skriv ny rad x"""
    lines = list(tokenize("skriv ny rad x"))
    ir = parse_tokens(lines)
    assert ir == [('SKRIV_NL', 'x')]

def test_complex_program():
    """Complex program with multiple statements"""
    src = """
sätt x till 0
sätt y till 10
för i från 0 till 5
    om i är mindre än 3
        skriv ny rad i
"""
    lines = list(tokenize(src))
    ir = parse_tokens(lines)
    assert ir[0] == ('SET', 'x', 0)
    assert ir[1] == ('SET', 'y', 10)
    assert ir[2][0] == 'FOR'
    assert ir[2][4][0][0] == 'IF'

def test_list_create():
    """sätt x till lista → LIST_CREATE"""
    lines = list(tokenize("sätt x till lista"))
    ir = parse_tokens(lines)
    assert ir == [('LIST_CREATE', 'x')], f"Got {ir}"

def test_list_init():
    """sätt x till lista av 1, 2, 3 → LIST_INIT"""
    lines = list(tokenize("sätt x till lista av 1, 2, 3"))
    ir = parse_tokens(lines)
    assert ir == [('LIST_INIT', 'x', ['1', '2', '3'])], f"Got {ir}"

def test_list_append():
    """lägg till 1 till x → LIST_APPEND"""
    lines = list(tokenize("lägg till 1 till x"))
    ir = parse_tokens(lines)
    assert ir == [('LIST_APPEND', 'x', '1')], f"Got {ir}"

def test_list_len():
    """antal element i x → LIST_LEN"""
    lines = list(tokenize("antal element i x"))
    ir = parse_tokens(lines)
    assert ir == [('LIST_LEN', 'x')], f"Got {ir}"

def test_set_list_len():
    """sätt n till antal element i x → SET with LIST_LEN value"""
    lines = list(tokenize("sätt n till antal element i x"))
    ir = parse_tokens(lines)
    assert ir == [('SET', 'n', ('LIST_LEN', 'x'))], f"Got {ir}"

def test_file_open():
    """öppna X för läsning → FILE_OPEN"""
    lines = list(tokenize("öppna data.txt för läsning"))
    ir = parse_tokens(lines)
    assert ir == [('FILE_OPEN', 'data.txt', 'r')], f"Got {ir}"

def test_file_open_write():
    """öppna X för skrivning → FILE_OPEN"""
    lines = list(tokenize("öppna output.txt för skrivning"))
    ir = parse_tokens(lines)
    assert ir == [('FILE_OPEN', 'output.txt', 'w')], f"Got {ir}"

def test_file_write():
    """skriv till fil X → FILE_WRITE"""
    lines = list(tokenize("skriv till fil resultat.txt"))
    ir = parse_tokens(lines)
    assert ir == [('FILE_WRITE', 'resultat.txt', '')], f"Got {ir}"

def test_if_else():
    """om x är 5
        skriv hej
    annars
        skriv annat
    """
    src = """om x är 5
    skriv hej
annars
    skriv annat"""
    lines = list(tokenize(src))
    ir = parse_tokens(lines)
    assert len(ir) == 1
    assert ir[0][0] == 'IF'
    assert ir[0][1] == ('x', 'likaMed', '5')  # value is string, not int
    assert len(ir[0][2]) == 1      # true body has 1 statement
    assert ir[0][2][0] == ('SKRIV', 'hej')
    assert len(ir[0][3]) == 1      # false body has 1 statement
    assert ir[0][3][0] == ('SKRIV', 'annat')

def test_if_else_with_for():
    """om x är 5
        för i från 0 till 3
            skriv i
    annars
        skriv fallback
    """
    src = """om x är 5
    för i från 0 till 3
        skriv i
annars
    skriv fallback"""
    lines = list(tokenize(src))
    ir = parse_tokens(lines)
    assert ir[0][0] == 'IF'
    assert ir[0][2][0][0] == 'FOR'  # true body: FOR loop
    assert ir[0][3][0] == ('SKRIV', 'fallback')  # false body

if __name__ == '__main__':
    test_set_integer()
    test_set_plus()
    test_set_minus()
    test_set_times()
    test_set_div()
    test_set_number_plus()
    test_for_loop()
    test_if_statement()
    test_if_less()
    test_if_greater()
    test_if_not()
    test_if_less_or_eq()
    test_if_greater_or_eq()
    test_break()
    test_exit()
    test_read()
    test_skriv()
    test_skriv_nl()
    test_complex_program()
    test_list_create()
    test_list_append()
    test_list_len()
    test_set_list_len()
    test_file_open()
    test_file_open_write()
    test_file_write()
    test_if_else()
    test_if_else_with_for()
    print("Alla parse-tester OK!")

def test_skriv_expr_times():
    """skriv a gånger 2 → SKRIV with expression"""
    lines = list(tokenize("skriv a gånger 2"))
    ir = parse_tokens(lines)
    assert ir == [('SKRIV', ('*', 'a', 2))], f"Got {ir}"

def test_skriv_expr_minus():
    """skriv x minus 3 → SKRIV with expression"""
    lines = list(tokenize("skriv x minus 3"))
    ir = parse_tokens(lines)
    assert ir == [('SKRIV', ('-', 'x', 3))], f"Got {ir}"

def test_skriv_expr_plus():
    """skriv a pluss 4 → SKRIV with expression"""
    lines = list(tokenize("skriv a pluss 4"))
    ir = parse_tokens(lines)
    assert ir == [('SKRIV', ('+', 'a', 4))], f"Got {ir}"

def test_skriv_expr_div():
    """skriv b delat 2 → SKRIV with expression"""
    lines = list(tokenize("skriv b delat 2"))
    ir = parse_tokens(lines)
    assert ir == [('SKRIV', ('/', 'b', 2))], f"Got {ir}"

def test_skriv_expr_with_for():
    """för i från 0 till 3\n    skriv i gånger 2"""
    src = """för i från 0 till 3
    skriv i gånger 2"""
    lines = list(tokenize(src))
    ir = parse_tokens(lines)
    assert ir[0][4][0] == ('SKRIV', ('*', 'i', 2)), f"Got {ir}"

def test_while_basic():
    """medan x är mindre än 5 → WHILE"""
    src = """medan x är mindre än 5
    skriv x"""
    lines = list(tokenize(src))
    ir = parse_tokens(lines)
    assert ir[0][0] == 'WHILE'
    assert ir[0][1] == ('x', 'mindre', '5')
    assert len(ir[0][2]) == 1  # body has 1 statement

def test_while_body():
    """WHILE with body statements"""
    src = """medan x är mindre än 5
    sätt x till x pluss 1
    skriv x"""
    lines = list(tokenize(src))
    ir = parse_tokens(lines)
    assert ir[0][0] == 'WHILE'
    assert len(ir[0][2]) == 2

def test_while_break():
    """WHILE with BREAK in body"""
    src = """medan x är mindre än 10
    om x är 5
        bryt
    sätt x till x pluss 1"""
    lines = list(tokenize(src))
    ir = parse_tokens(lines)
    while_stmt = ir[0]
    assert while_stmt[0] == 'WHILE'
    assert while_stmt[2][0] == ('IF', ('x', 'likaMed', '5'), [('BREAK',), ('SET', 'x', ('+', 'x', 1))], [])

def test_while_greater():
    """medan x är större än 0"""
    src = """medan x är större än 0
    sätt x till x minus 1"""
    lines = list(tokenize(src))
    ir = parse_tokens(lines)
    assert ir[0][1] == ('x', 'större', '0')

def test_while_less_or_eq():
    """medan x är mindre eller 5"""
    src = """medan x är mindre eller 5
    skriv x"""
    lines = list(tokenize(src))
    ir = parse_tokens(lines)
    assert ir[0][1] == ('x', 'mindreLikaMed', '5')

def test_while_greater_or_eq():
    """medan x är större eller 0"""
    src = """medan x är större eller 0
    skriv x"""
    lines = list(tokenize(src))
    ir = parse_tokens(lines)
    assert ir[0][1] == ('x', 'störreLikaMed', '0')

def test_while_not_eq():
    """medan x är inte 0"""
    src = """medan x är inte 0
    skriv x"""
    lines = list(tokenize(src))
    ir = parse_tokens(lines)
    assert ir[0][1] == ('x', 'inteLikaMed', '0')

def test_grej_simple():
    """grej hello → FUNC_DEF"""
    src = """grej hej världen
  skriv hello
slut"""
    lines = list(tokenize(src))
    ir = parse_tokens(lines)
    assert ir[0] == ('FUNC_DEF', 'hej', ['världen'], [('SKRIV', 'hello')]), f"Got {ir}"

def test_call_anropa():
    """anropa func med 1 → CALL"""
    src = """anropa hej med 1"""
    lines = list(tokenize(src))
    ir = parse_tokens(lines)
    assert ir[0] == ('CALL', 'hej', ['1']), f"Got {ir}"

def test_call_in_set():
    """sätt resultat till anropa func med 1 → SET with CALL"""
    src = """sätt resultat till anropa hej med 1"""
    lines = list(tokenize(src))
    ir = parse_tokens(lines)
    assert ir[0] == ('SET', 'resultat', ('CALL', 'hej', ['1'])), f"Got {ir}"

def test_call_with_func_def():
    """Full GREJ def + CALL: grej dubbla x ... sätt b till dubbla a"""
    src = """grej dubbla x
  sätt resultat till x gånger 2
  ge resultat
slut

sätt a till 5
sätt b till dubbla a"""
    lines = list(tokenize(src))
    ir = parse_tokens(lines)
    assert ir[0] == ('FUNC_DEF', 'dubbla', ['x'], [('SET', 'resultat', ('*', 'x', 2)), ('RETURN', 'resultat')]), f"Got {ir[0]}"
    assert ir[1] == ('SET', 'a', 5), f"Got {ir[1]}"
    assert ir[2] == ('SET', 'b', ('CALL', 'dubbla', ['a'])), f"Got {ir[2]}"

def test_call_kalla():
    """sätt resultat till kalla func med 1 → SET with CALL"""
    src = """sätt resultat till kalla hej med 1"""
    lines = list(tokenize(src))
    ir = parse_tokens(lines)
    assert ir[0] == ('SET', 'resultat', ('CALL', 'hej', ['1'])), f"Got {ir}"
