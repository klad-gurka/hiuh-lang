# HIUH Självkompilering - TODO

## Mål
- [ ] HIUH kompilator skriven i HIUH som kan kompilera sig själv

## Arkitektur

```
src/
  frontend/
    tokenize.py   ← tokenizer (ren Python, pipeline-kompatibel)
    parse.py      ← parser → IR
  backend/
    x86.py        ← x86 asm backend
tools/
  hiuh-native.py   ← kompilator (Python)
  hiuh-tokenizer.hiuh  ← tokenizer källa (HIUH)
```

### IR-format
```python
('SET', 'x', 5)              # Sätt x till 5
('FOR', 'i', 0, 10, body)   # För i från 0 till 10
('IF', cmp, body)            # Om x är 0
('SKRIV_NL', expr)          # SkrivNyRad x
```

### Pipeline
```
källkod.hiuh
  → tokenize.py (tokens)
  → parse.py (IR)
  → backend/x86.py (x86 asm)
  → as + ld
  → körbar
```

## Nuvarande status (2026-04-28)
- [x] Tokenizer: src/frontend/tokenize.py ✅
- [x] Parser → IR: src/frontend/parse.py ✅
- [ ] Backend x86: src/backend/x86.py (enkel version funkar, behöver utökas)
- [ ] Självkompilering: PÅBÖRJAD

## Nästa steg
1. [ ] Utöka backend/x86.py med FOR, IF, SKRIV
2. [ ] Testa hela pipelinen: echo 'Sätt x till 5' | tokenize.py | parse.py | x86.py
3. [ ] Skriv hiuh-parser.hiuh (parser i HIUH)
4. [ ] Skriv HIUH-backend (backend i HIUH)
5. [ ] Självkompilera!

## IR-statements som behövs
- SET(var, value)
- FOR(var, start, end, body)
- IF(condition, body)
- BREAK
- EXIT(code)
- READ(buf)
- SKRIV(expr)
- SKRIV_NL(expr)
- STORE(buf, idx, val)
- LOAD(buf, idx)
