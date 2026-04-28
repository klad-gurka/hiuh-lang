# HIUH Självkompilering - TODO

## Mål
- [ ] HIUH kompilator skriven i HIUH som kan kompilera sig själv

## Arkitektur

```
src/hiuh/
  tokenize.py   ← tokenizer (ren Python)
  parse.py      ← parser → IR
  backend/
    x86.py     ← x86 asm backend
tests/
  test_tokenize.py
  test_parse.py
  test_backend_x86.py
tools/
  hiuh-native.py    ← kompilator (Python)
```

### IR-format
```python
('SET', 'x', 5)              # Sätt x till 5
('SET', 'x', ('+', 'a', 3))  # Sätt x till a pluss 3
('FOR', 'i', 0, 10, body)   # För i från 0 till 10
('IF', cmp, body)            # Om x är 0
```

## Keyword-implementationstatus

| Keyword | IR | X86 | WASM | Kommentar |
|---------|----|-----|------|-----------|
| `Sätt x till 5` | ✅ | ✅ | ❌ | SET med integer |
| `Sätt x till a pluss 3` | ✅ | ✅ | ❌ | SET med uttryck |
| `För x från 0 till 10` | ✅ | ✅ | ❌ | FOR-loop |
| `Om x är 0` | ✅ | ✅ | ❌ | IF med == |
| `Om x är mindre än 0` | ✅ | ✅ | ❌ | IF med < |
| `Om x är större än 0` | ✅ | ✅ | ❌ | IF med > |
| `Om x är inte 0` | ❌ | ❌ | ❌ | IF med != |
| `Om x är större eller 0` | ❌ | ❌ | ❌ | IF med >= |
| `Om x är mindre eller 0` | ❌ | ❌ | ❌ | IF med <= |
| `Hejdå` | ✅ | ✅ | ❌ | END (blockavslut) |
| `Annars` | ❌ | ❌ | ❌ | ELSE-branch |
| `Bryt` | ✅ | ✅ | ❌ | BREAK |
| `Medan` | ❌ | ❌ | ❌ | WHILE-loop |
| `Skriv x` | ✅ | ✅ | ❌ | SKRIV (text) |
| `Skriv värdet av x` | ❌ | ❌ | ❌ | SKRIV (variabel) |
| `skriv ny rad` | ✅ | ✅ | ❌ | SKRIV_NL |
| `Läs` | ✅ | ❌ | ❌ | READ (IR klart, x86 ej) |
| `Lagra vid i i buf` | ✅ | ❌ | ❌ | STORE |
| `tecken i ur buf` | ✅ | ❌ | ❌ | LOAD |
| `Sätt x till a minus b` | ❌ | ❌ | ❌ | MINUS |
| `Sätt x till a gånger b` | ❌ | ❌ | ❌ | TIMES |
| `Sätt x till a delat b` | ❌ | ❌ | ❌ | DIV |
| `Jag gå nu` | ✅ | ✅ | ❌ | EXIT |
| `Grej namn` | ❌ | ❌ | ❌ | FUNC_DEF |
| `Anropa namn med` | ❌ | ❌ | ❌ | CALL |
| `ge x` | ❌ | ❌ | ❌ | RETURN |
| `Sätt x till lista` | ❌ | ❌ | ❌ | LIST_CREATE |
| `Lägg till x till lista` | ❌ | ❌ | ❌ | LIST_APPEND |
| `element i ur lista` | ❌ | ❌ | ❌ | LIST_GET |
| `antal element i lista` | ❌ | ❌ | ❌ | LIST_LEN |
| `a sammanfogat med b` | ❌ | ❌ | ❌ | CONCAT |
| `Öppna fil för läsning` | ❌ | ❌ | ❌ | FILE_OPEN |
| `SkrivTillFil` | ❌ | ❌ | ❌ | FILE_WRITE |

## Nästa steg

### Hög prioritet
1. [ ] **Läs input** - x86 syscall för read()
2. [ ] **minus, gånger, delat** - aritmetik i tokenizer + x86
3. [ ] **!=, >=, <=** - jämförelseoperatorer
4. [ ] **Skriv värdet av x** - variabel-output

### Medel prioritet
5. [ ] **WHILE-loop** - Medan x är 0
6. [ ] **ANNARS** - else-branch i IF
7. [ ] **Funktioner** - Grej/Anropa/ge
8. [ ] **Listor** - Sätt x till lista, element ur

### Låg prioritet
9. [ ] File I/O
10. [ ] WASM backend

## Kända buggar/problem

- `i` är keyword `IN` → kan inte användas som variabelnamn
- READ syscall är inte implementerad i x86.py
