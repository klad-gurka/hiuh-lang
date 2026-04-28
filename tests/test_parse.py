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
    assert ir[0][1] == ('x', '==', '0')

def test_if_less():
    """om x är mindre än 5"""
    src = """om x är mindre än 5
    skriv x"""
    lines = list(tokenize(src))
    ir = parse_tokens(lines)
    assert ir[0][1] == ('x', '<', '5')

def test_if_greater():
    """om x är större än 0"""
    src = """om x är större än 0
    skriv x"""
    lines = list(tokenize(src))
    ir = parse_tokens(lines)
    assert ir[0][1] == ('x', '>', '0')

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
    test_complex_program()
    print("Alla parse-tester OK!")
