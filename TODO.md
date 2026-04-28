# HIUH Självkompilering - TODO

## Mål
- [ ] HIUH kompilator skriven i HIUH som kan kompilera sig själv

## Arkitektur (2026-04-28)

### Frontend / Backend-split
HIUH-kompilatorn delas i två delar:

**Frontend:**
- Tokenizer (hiuh-tokenizer.hiuh) ✅ KLAR
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
- Tokenizer: KLAR (hiuh-tokenizer.hiuh, fungerar)
- Frontend i Python: fungerar (hiuh-native.py)
- Backend x86-Linux: fungerar
- Självkompilering: PÅBÖRJAD

### Nästa steg
1. [ ] Definiera IR-formatet ordentligt (hur ser IR ut som text?)
2. [ ] Bygg HIUH-parser som producerar IR (hiuh-parser.hiuh)
3. [ ] Backend x86-Linux i HIUH (kan använda befintliga keywords)
4. [ ] Självkompilera: HIUH-parser + HIUH-backend → kompilerar sig själv

### IR som text
IR behöver vara läsbart som text (för självkompilering):
```
SET x till 5
FÖR i FRÅN 0 TILL 10
  SKRIV_NYRAD i
FOR_SLUT
```

### Tokens som parsern behöver
Från tokenizer:
- SET, x, TILL, 5
- FOR, i, FRAN, 0, TILL, 10
- OM, x, AR, 0
- SKRIV, x
- SKRIV_NYRAD, x
- osv.

