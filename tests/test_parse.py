#!/usr/bin/env python3
"""Tests for parse.py - IR generation"""

import sys
sys.path.insert(0, 'src')

from hiuh.parse import parse_tokens, parse_stream
from hiuh.tokenize import tokenize

def test_set_integer():
    """Sätt x till 5 → SET"""
    tokens = list(tokenize("Sätt x till 5"))
    ir = parse_tokens(tokens)
    assert ir == [('SET', 'x', 5)], f"Got {ir}"

def test_set_plus():
    """Sätt x till a pluss b → SET with expression"""
    tokens = list(tokenize("Sätt x till a pluss 3"))
    ir = parse_tokens(tokens)
    assert ir == [('SET', 'x', ('+', 'a', 3))], f"Got {ir}"

def test_for_loop():
    """För i från 0 till 10"""
    src = "För x från 0 till 10\nSkrivNyRad x\nHejdå"
    tokens = list(tokenize(src))
    ir = parse_tokens(tokens)
    assert len(ir) == 2
    assert ir[0][0] == 'FOR'
    assert ir[0][1] == 'x'
    assert ir[0][2] == 0
    assert ir[0][3] == 10

def test_if_statement():
    """Om x är 0"""
    src = "Om x är 0\nSkrivNyRad x\nHejdå"
    tokens = list(tokenize(src))
    ir = parse_tokens(tokens)
    assert len(ir) == 1
    assert ir[0][0] == 'IF'
    assert ir[0][1] == ('x', '==', '0')

def test_if_less():
    """Om x är mindre än 5"""
    src = "Om x är mindre än 5\nSkrivNyRad x\nHejdå"
    tokens = list(tokenize(src))
    ir = parse_tokens(tokens)
    assert ir[0][1] == ('x', '<', '5')

def test_if_greater():
    """Om x är större än 0"""
    src = "Om x är större än 0\nSkrivNyRad x\nHejdå"
    tokens = list(tokenize(src))
    ir = parse_tokens(tokens)
    assert ir[0][1] == ('x', '>', '0')

def test_break():
    """Bryt"""
    src = "Om x är 0\nBryt\nHejdå"
    tokens = list(tokenize(src))
    ir = parse_tokens(tokens)
    assert ir[0][2][0] == ('BREAK',)

def test_exit():
    """JagMåsteGåNu 0"""
    tokens = list(tokenize("JagMåsteGåNu 0"))
    ir = parse_tokens(tokens)
    assert ir == [('EXIT', 0)]

def test_read():
    """Läs"""
    tokens = list(tokenize("Läs"))
    ir = parse_tokens(tokens)
    assert ir == [('READ', 'källa')]

def test_skriv():
    """Skriv x"""
    tokens = list(tokenize("Skriv x"))
    ir = parse_tokens(tokens)
    assert ir == [('SKRIV', 'x')]

def test_skriv_nl():
    """SkrivNyRad x"""
    tokens = list(tokenize("SkrivNyRad x"))
    ir = parse_tokens(tokens)
    assert ir == [('SKRIV_NL', 'x')]

def test_store():
    """Lagra vid n i buf"""
    # Tokens: STORE VID n IN buf
    # We want: STORE(buf, idx, val) = STORE(buf, n, n)
    tokens = list(tokenize("Lagra vid n i buf"))
    ir = parse_tokens(tokens)
    # IR should be STORE with 4 args: buf=buf, idx=n, val=n
    assert len(ir) == 1
    assert ir[0][0] == 'STORE'

def test_load():
    """tecken n ur buf"""
    # Tokens: CHAR n UR buf
    tokens = list(tokenize("tecken n ur buf"))
    ir = parse_tokens(tokens)
    assert ir == [('LOAD', 'buf', 'n')]

def test_complex_program():
    """Complex program with multiple statements"""
    src = """
Sätt x till 0
Sätt y till 10
För i från 0 till 5
    Om i är mindre än 3
        SkrivNyRad i
    Hejdå
Hejdå
"""
    tokens = list(tokenize(src))
    ir = parse_tokens(tokens)
    assert ir[0] == ('SET', 'x', 0)
    assert ir[1] == ('SET', 'y', 10)
    assert ir[2][0] == 'FOR'
    assert ir[2][4][0][0] == 'IF'

if __name__ == '__main__':
    test_set_integer()
    test_set_plus()
    test_for_loop()
    test_if_statement()
    test_if_less()
    test_if_greater()
    test_break()
    test_exit()
    test_read()
    test_skriv()
    test_skriv_nl()
    test_store()
    test_load()
    test_complex_program()
    print("Alla parse-tester OK!")
