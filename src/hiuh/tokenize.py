#!/usr/bin/env python3
"""HIUH Tokenizer - pure Python, works correctly with pipelines"""

import sys

# Keywords
KEYWORDS = {
    'Sätt': 'SET', 'För': 'FOR', 'Från': 'FROM', 'Om': 'IF', 'Hejdå': 'END',
    'Annars': 'ELSE', 'Läs': 'READ', 'SkrivNyRad': 'SKRIV_NL',
    'Skriv': 'SKRIV', 'Lagra': 'STORE', 'Jämför': 'CMP',
    'JämförBuffer': 'CMP_BUF', 'JagMåsteGåNu': 'EXIT',
    'Bryt': 'BREAK', 'till': 'TILL', 'från': 'FRAN',
    'är': 'AR', 'pluss': 'PLUS', 'ur': 'UR', 'vid': 'VID',
    'med': 'MED', 'tecken': 'CHAR', 'än': 'THAN',
    'mindre': 'LESS', 'större': 'GREATER', 'värdet': 'VAL',
    'av': 'OF', 'text': 'TEXT', 'i': 'IN', 'ge': 'RET',
}

def tokenize(src):
    """Tokenize source string, yield tokens"""
    prev_word = None  # Track original word before keyword conversion
    for line in src.split('\n'):
        line = line.strip()
        if not line:
            continue
        for word in line.split():
            # Special case: 'i' as variable name after keywords that take variable names
            # Use original word (before keyword lookup) for context
            if word == 'i' and prev_word in ('För', 'Sätt', 'Om', 'Lagra', 'Skriv', 'SkrivNyRad'):
                yield word  # variable name 'i', not keyword IN
            elif word in KEYWORDS:
                yield KEYWORDS[word]
            else:
                yield word
            prev_word = word

def tokenize_stream():
    """Read from stdin, output one token per line"""
    for tok in tokenize(sys.stdin.read()):
        print(tok)

if __name__ == '__main__':
    tokenize_stream()