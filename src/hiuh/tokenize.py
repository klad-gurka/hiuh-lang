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
    'inte': 'INTE', 'eller': 'OR',
    'större': 'GREATER', 'värdet': 'VAL', 'av': 'OF',
    'text': 'TEXT', 'i': 'IN', 'ge': 'RET',
    'medan': 'WHILE',
    # Function keywords
    'grej': 'GREJ',     # function definition
    'anropa': 'CALL',   # function call
    'kalla': 'CALL',    # alias for anropa
    # Space-friendly compound keywords
    'ny': 'SKRIV_NL',  # "skriv ny rad" = SKRIV + SKRIV_NL
    'rad': 'SKRIV_NL',
    'gå': 'EXIT',  # "jag gå nu" = EXIT
    'nu': 'EXIT',
}

def tokenize(src):
    """Tokenize source string, yield (indent_level, tokens) for each line"""
    prev_word = None
    last_token = None  # Track the last token added
    for line in src.split('\n'):
        # Calculate indentation level
        indent = len(line) - len(line.lstrip())
        stripped = line.strip()
        if not stripped:
            continue
        words = stripped.split()
        tokens = []
        i = 0
        while i < len(words):
            word = words[i].lower()
            
            # Handle "skriv värdet av x" → SKRIV_VAR x (print variable value)
            if word == 'skriv' and i + 3 < len(words):
                if words[i+1].lower() == 'värdet' and words[i+2].lower() == 'av':
                    tokens.append('SKRIV_VAR')
                    tokens.append(words[i+3])
                    last_token = 'SKRIV_VAR'
                    i += 4
                    continue
            
            # Handle "skriv ny rad" → SKRIV_NL (space-friendly)
            if word == 'skriv' and i + 2 < len(words):
                if words[i+1].lower() == 'ny' and words[i+2].lower() == 'rad':
                    tokens.append('SKRIV_NL')
                    last_token = 'SKRIV_NL'
                    i += 3
                    continue
            
            # After SKRIV_NL, next word is an argument (not a keyword)
            if last_token == 'SKRIV_NL':
                tokens.append(words[i])
                last_token = None
                i += 1
                continue
            
            # Handle "jag gå nu" → EXIT (space-friendly for JagMåsteGåNu)
            if word == 'jag' and i + 2 < len(words):
                if words[i+1].lower() == 'gå' and words[i+2].lower() == 'nu':
                    tokens.append('EXIT')
                    last_token = 'EXIT'
                    i += 3
                    continue
            
            # Handle "hej då" → EXIT (program exit)
            if word == 'hej' and i + 1 < len(words):
                if words[i+1].lower() == 'då':
                    tokens.append('EXIT')
                    last_token = 'EXIT'
                    i += 2
                    continue
            
            # 'i' after variable-taking keywords is a variable name, not IN keyword
            if word == 'i' and prev_word in ('för', 'sätt', 'om', 'skriv', 'lagra'):
                tokens.append(word)  # variable name
                last_token = word
            elif word in KEYWORDS:
                tokens.append(KEYWORDS[word])
                last_token = KEYWORDS[word]
            else:
                tokens.append(words[i])
                last_token = words[i]
            prev_word = word
            i += 1
        if tokens:
            yield (indent // 4, tokens)  # 4 spaces = 1 indent level

def tokenize_stream():
    """Read from stdin, output indent level + tokens"""
    for indent, tokens in tokenize(sys.stdin.read()):
        print(f"{indent} {' '.join(tokens)}")

if __name__ == '__main__':
    tokenize_stream()
