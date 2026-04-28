# HIUH Självkompilering - TODO

## Mål
- [ ] HIUH kompilator skriven i HIUH som kan kompilera sig själv

## Arkitektur (2026-04-28)

### Frontend / Backend-split
HIUH-kompilatorn delas i två delar:

**Frontend:**
- Tokenizer (hiuh-tokenizer.hiuh) ✅ KLAR - self-tokenizes correctly
- Parser → producerar IR
- IR = plattformsoberoende representation

**IR-format:**
```
SET(var, value)          # Sätt x till 5
FOR(var, start, end)     # För x från 0 till 10
IF(condition, body)      # Om x är 0
READ(buf)                # Läs
SKRIV(buf)               # Skriv
SKRIV_NYRAD(buf)         # SkrivNyRad
STORE(buf, idx, val)     # Lagra vid i i buf
LOAD(buf, idx)           # Läs tecken i ur buf
JAMFOR(a, op, b)        # Jämför
EXIT                    # JagMåsteGåNu
BREAK                   # Bryt
RETURN(value)           # ge value
```

**Backends:**
- [x] x86_64 Linux backend ✅ (native/hiuh-native.py)
- [ ] x86_64 Windows backend
- [ ] WASM backend (för webben!)
- [ ] x86_64 Linux backend i HIUH (självkompilerbar)

### Pipeline
```
källkod.hiuh 
  → Frontend (Tokenizer → Parser)
  → IR 
  → Backend (x86-Linux / x86-Windows / WASM / ...)
  → platformkod (.s / .wasm)
  → as + ld / wasm-interpreter
  → körbar
```

### Nuvarande status (2026-04-28)
- Tokenizer: KLAR (hiuh-tokenizer.hiuh, fungerar, self-tokenizes correctly)
- Parser: hiuh-parser.hiuh SKRIVEN men BRUTEN - parsern tar token-input men outputter 0 rader
  - Bug: "tilli" istället för "till i" i källkoden → "till" och "i" blir separata tokens → state-machine trasig
- Frontend i Python: fungerar (hiuh-native.py)
- Backend x86-Linux: fungerar
- Självkompilering: PÅBÖRJAD

### Nästa steg
1. [ ] Fixa "tilli" buggen i hiuh-parser.hiuh (rad ~49-50: "Sätt i till i pluss 1" → tokenizer ger "tilli")
2. [ ] Fixa parser state-machine så den hanterar tok_buf utan mellanslag
3. [ ] Testa parser med tokenizer-output (förväntat: 658 rader → IR-rader)
4. [ ] Bygg HIUH-backend som tar IR → x86 asm
5. [ ] Självkompilera: HIUH-parser + HIUH-backend → kompilerar sig själv

### Tokens som parsern behöver
Från tokenizer:
- SET, x, TILL, 5
- FOR, i, FRAN, 0, TILL, 10
- OM, x, AR, 0
- SKRIV, x
- SKRIV_NYRAD, x
- osv.

### Kända buggar
- **tilli bug**: hiuh-parser.hiuh har "Sätt i till i pluss 1" där "till i" blir "tilli" via compound-word hack i tokenizer. Men tokenizer känner INTE igen "tilli" som keyword, så det blir två separata ord. State-maskinen i parsern blir förvirrad.
