#!/usr/bin/env python3
"""
HIUH Parser - converts tokens to IR (Intermediate Representation)

IR is a list of statements:
  ('SET', name, value)           # Sätt x till 5
  ('SET', name, ('+', a, b))   # Sätt x till a pluss b
  ('FOR', var, start, end, body) # För i från 0 till 10
  ('IF', cmp, body)             # Om x är 0
  ('IF', cmp, then_body, else_body)
  ('BREAK',)                    # Bryt
  ('EXIT', code)                # JagMåsteGåNu 0
  ('READ', buf)                 # Läs
  ('SKRIV', expr)              # Skriv x
  ('SKRIV_NL', expr)           # SkrivNyRad x
  ('STORE', buf, idx, val)     # Lagra vid i i buf
  ('LOAD', buf, idx)           # tecken i ur buf
  ('RETURN', val)               # ge x
"""

import sys

def parse_tokens(tokens):
    """Parse token list to IR"""
    ir = []
    i = 0
    while i < len(tokens):
        tok = tokens[i]
        if tok == 'SET':
            name = tokens[i+1]
            # Skip TILL keyword, get value after it
            val_tokens = []
            j = i + 2
            while j < len(tokens) and tokens[j] not in ('FOR', 'IF', 'END', 'SET', 'OM', 'HEJDÅ'):
                val_tokens.append(tokens[j])
                j += 1
            val = parse_value(val_tokens)
            ir.append(('SET', name, val))
            i = j
        elif tok == 'FOR':
            var = tokens[i+1]
            # tokens: FOR var FROM start TILL end ...
            # Find FRAN (FROM) and TILL
            j = i + 2
            # Skip FRAN keyword
            if tokens[j] == 'FRAN':
                j += 1
            start = int(tokens[j])
            j += 1
            # Skip TILL keyword
            if tokens[j] == 'TILL':
                j += 1
            end = int(tokens[j])
            j += 1
            # Parse body until END
            body, consumed = parse_block(tokens[j:], 'END')
            ir.append(('FOR', var, start, end, body))
            i = j + consumed + 1  # +1 to skip END
        elif tok == 'IF':
            cmp, skip = parse_cmp(tokens[i+1:])
            body, end_i = parse_block(tokens[i+1+skip:], 'END')
            ir.append(('IF', cmp, body))
            i = i + 1 + skip + end_i + 1
        elif tok == 'BREAK':
            ir.append(('BREAK',))
            i += 1
        elif tok == 'EXIT':
            code = int(tokens[i+1]) if i+1 < len(tokens) and tokens[i+1].isdigit() else 0
            ir.append(('EXIT', code))
            i += 2
        elif tok == 'READ':
            ir.append(('READ', 'input_buf'))
            i += 1
        elif tok in ('SKRIV', 'SKRIV_NL'):
            expr = tokens[i+1] if i+1 < len(tokens) else ''
            ir.append(('SKRIV_NL' if tok == 'SKRIV_NL' else 'SKRIV', expr))
            i += 2
        elif tok == 'STORE':
            # Lagra x vid i i buf -> STORE buf idx x
            # Token sequence: STORE idx VID var IN buf
            # Wait, HIUH is: "Lagra vid i i buf" -> "Lagra VID i I buf"
            # So tokens after STORE: VID idx I buf
            buf = tokens[i+4] if i+4 < len(tokens) else 'buf'
            idx = tokens[i+2] if i+2 < len(tokens) else 'i'
            ir.append(('STORE', buf, idx, idx))
            i += 5
        elif tok == 'CHAR':
            # tecken i ur buf -> CHAR idx BUF
            if i+3 < len(tokens) and tokens[i+2] == 'UR':
                idx = tokens[i+1]
                buf = tokens[i+3]
                ir.append(('LOAD', buf, idx))
                i += 4
            else:
                i += 1
        else:
            i += 1
    return ir

def parse_value(tokens):
    """Parse a value: number, identifier, or expression"""
    if not tokens:
        return 0
    # Skip TILL keyword
    if tokens[0] == 'TILL':
        tokens = tokens[1:]
    if not tokens:
        return 0
    tok = tokens[0]
    if tok.isdigit():
        return int(tok)
    # Check for a pluss b expression
    if len(tokens) >= 3 and tokens[1] == 'PLUS':
        return ('+', tok, int(tokens[2]))
    return tok

def parse_cmp(tokens):
    """Parse comparison: VAR [är] [mindre/större än] VALUE"""
    var = tokens[0]
    if len(tokens) >= 3:
        # är mindre än 5 OR mindre än 5
        if tokens[1] == 'LESS' or (tokens[1] == 'AR' and tokens[2] == 'LESS'):
            # är mindre än: tokens = [x, AR, LESS, THAN, val] -> skip 5
            # mindre än: tokens = [x, LESS, THAN, val] -> skip 4
            val = tokens[4] if tokens[1] == 'AR' else tokens[3]
            return (var, '<', val), 5 if tokens[1] == 'AR' else 4
        # är större än 5 OR större än 5
        elif tokens[1] == 'GREATER' or (tokens[1] == 'AR' and tokens[2] == 'GREATER'):
            val = tokens[4] if tokens[1] == 'AR' else tokens[3]
            return (var, '>', val), 5 if tokens[1] == 'AR' else 4
        # är X (equality)
        elif tokens[1] == 'AR':
            return (var, '==', tokens[2]), 3
    return (var, '!=', 0), 1

def parse_block(tokens, end_token='END'):
    """Parse a block until END. Returns (block, bytes_consumed)"""
    block = []
    i = 0
    while i < len(tokens):
        tok = tokens[i]
        if tok == end_token:
            return block, i
        elif tok == 'IF':
            cmp, skip = parse_cmp(tokens[i+1:])
            body, end_i = parse_block(tokens[i+1+skip:], 'END')
            block.append(('IF', cmp, body))
            i = i + 1 + skip + end_i + 1
        elif tok == 'FOR':
            var = tokens[i+1]
            # Skip FRAN
            j = i + 2
            if tokens[j] == 'FRAN':
                j += 1
            start = int(tokens[j])
            j += 1
            # Skip TILL
            if tokens[j] == 'TILL':
                j += 1
            end = int(tokens[j])
            j += 1
            body, end_i = parse_block(tokens[j:], 'END')
            block.append(('FOR', var, start, end, body))
            i = j + end_i + 1
        elif tok == 'SKRIV':
            expr = tokens[i+1] if i+1 < len(tokens) else ''
            block.append(('SKRIV', expr))
            i += 2
        elif tok == 'SKRIV_NL':
            expr = tokens[i+1] if i+1 < len(tokens) else ''
            block.append(('SKRIV_NL', expr))
            i += 2
        elif tok == 'BREAK':
            block.append(('BREAK',))
            i += 1
        else:
            i += 1
    return block, i

def parse_stream():
    """Read tokens from stdin, output IR as text"""
    tokens = [line.strip() for line in sys.stdin if line.strip()]
    ir = parse_tokens(tokens)
    for stmt in ir:
        print(stmt)

if __name__ == '__main__':
    parse_stream()