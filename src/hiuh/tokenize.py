#!/usr/bin/env python3
"""HIUH Tokenizer - pure Python, works correctly with pipelines"""

import sys

# Keywords (lowercase for case-insensitive matching)
KEYWORDS = {
    # Core keywords
    'sätt': 'SET', 'för': 'FOR', 'om': 'IF', 'hejdå': 'END',
    'annars': 'ELSE', 'läs': 'READ', 'skriv': 'SKRIV', 'skrivnyrad': 'SKRIV_NL',
    'lagra': 'STORE', 'jämför': 'CMP',
    'jämförbuffer': 'CMP_BUF', 'jagmåstegånu': 'EXIT',
    'bryt': 'BREAK', 'till': 'TILL', 'från': 'FRAN',
    'är': 'AR', 'pluss': 'PLUS', 'minus': 'MINUS',
    'gånger': 'TIMES', 'delat': 'DIV',
    'ur': 'UR', 'vid': 'VID', 'med': 'MED',
    'tecken': 'CHAR', 'än': 'THAN', 'mindre': 'LESS',
    'större': 'GREATER', 'värdet': 'VAL', 'av': 'OF',
    'text': 'TEXT', 'i': 'IN', 'ge': 'RET',
    # Space-friendly compound keywords
    'ny': 'SKRIV_NL',  # "skriv ny rad" = SKRIV + SKRIV_NL
    'rad': 'SKRIV_NL',
    'gå': 'EXIT',  # "jag gå nu" = EXIT
    'nu': 'EXIT',
}

def tokenize(src):
    """Tokenize source string, yield tokens (case-insensitive)"""
    prev_word = None
    for line in src.split('\n'):
        line = line.strip()
        if not line:
            continue
        words = line.split()
        i = 0
        while i < len(words):
            word = words[i].lower()
            
            # Handle "skriv ny rad" → SKRIV_NL (space-friendly)
            if word == 'skriv' and i + 2 < len(words):
                if words[i+1].lower() == 'ny' and words[i+2].lower() == 'rad':
                    yield 'SKRIV_NL'
                    i += 3
                    continue
            
            # Handle "jag gå nu" → EXIT (space-friendly for JagMåsteGåNu)
            if word == 'jag' and i + 2 < len(words):
                if words[i+1].lower() == 'gå' and words[i+2].lower() == 'nu':
                    yield 'EXIT'
                    i += 3
                    continue
            
            # 'i' after variable-taking keywords is a variable name, not IN keyword
            if word == 'i' and prev_word in ('för', 'sätt', 'om', 'skriv', 'lagra'):
                yield word  # variable name
            elif word in KEYWORDS:
                yield KEYWORDS[word]
            else:
                yield words[i]
            prev_word = word
            i += 1

def tokenize_stream():
    """Read from stdin, output one token per line"""
    for tok in tokenize(sys.stdin.read()):
        print(tok)

if __name__ == '__main__':
    tokenize_stream()
