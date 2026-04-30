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
  test_integration.py  ← faktisk körning av HIUH-program
```

## IR-design

### Principer
- IR ska följa HIUH:s svenska språk så nära som möjligt
- Operatorer ska vara korta men läsbara svenska ord
- Tokenizern mappar svenska alias → IR operatorer
- Parse.py产出 enhetliga IR-namn, oavsett vilket keyword som användes

### Operatorer (Jämförelse)

| IR operator     | Source keywords               | Betydelse |
|----------------|------------------------------|-----------|
| `mindre`       | "är mindre än"               | a < b     |
| `mindreLikaMed`| "är mindre än eller lika med"| a <= b    |
| `större`        | "är större än"               | a > b     |
| `störreLikaMed`| "är större än eller lika med"| a >= b    |
| `likaMed`       | "är lika med"                | a == b    |
| `inteLikaMed`  | "är inte lika med"           | a != b    |

### IR-nod dokumentation

#### Satser (Statements)

| Språk-konstruktion              | IR nod                          | Parse impl | Parse test | X86 impl | X86 test | Integration |
|--------------------------------|---------------------------------|:---------:|:---------:|:--------:|:--------:|:-----------:|
| `sätt x till 5`                | `('SÄTT', name, expr)`          | ✅        | ✅        | ✅       | ✅       | ❌          |
| `för x från 0 till 10`          | `('FÖR', var, start, end, body)`| ✅        | ✅        | ❌       | ❌       | ❌          |
| `medan x är mindre än 5`       | `('MEDAN', expr, body)`          | ✅        | ✅        | ✅       | ✅       | ❌          |
| `om x är mindre än 5`          | `('OM', expr, true, false)`     | ✅        | ✅        | ✅       | ✅       | ❌          |
| `bryt`                         | `('BRYT',)`                     | ✅        | ✅        | ❌       | ❌       | ❌          |
| `hej då` / `jag gå nu`         | `('HEJDÅ',)`                    | ✅        | ✅        | ❌       | ❌       | ❌          |
| `skriv hello`                  | `('SKRIV', expr)`               | ✅        | ✅        | ❌       | ❌       | ❌          |
| `skriv värdet av x`            | `('SKRIV_VÄRDE', name)`         | ✅        | ✅        | ✅       | ❌       | ❌          |
| `läs rad till x`               | `('LÄS_RAD', name)`             | ✅        | ✅        | ❌       | ❌       | ❌          |
| `sätt funk till grej med a, b` | `('GREJ', params, body)`        | ✅        | ✅        | ❌       | ❌       | ❌          |
| `sätt a till funk med x, y`     | `('ANROPA', var, args)`         | ✅        | ✅        | ❌       | ❌       | ❌          |
| `ge x`                         | `('GE', expr)`                  | ✅        | ❌        | ❌       | ❌       | ❌          |
| `sätt a till ny lista`         | `('NY_LISTA', args)`            | ✅        | ✅        | ✅       | ❌       | ❌          |
| `sätt a till lista av 1, 2, 3` | `('LIST_INIT', name, items)`    | ✅        | ✅        | ❌       | ❌       | ❌          |
| `lägg till x i a`              | `('LÄGG_TILL', item, var)`     | ✅        | ✅        | ❌       | ❌       | ❌          |
| `ta bort apa från a`           | `('TA_BORT', val, var)`        | ✅        | ✅        | ❌       | ❌       | ❌          |
| `ta bort element 3 från a`     | `('TA_BORT_INDEX', var, idx)`   | ✅        | ❌        | ✅       | ❌       | ❌          |
| `sätt x till element 3 från a`  | `('HÄMTA_INDEX', var, idx)`    | ❌        | ❌        | ❌       | ❌       | ❌          |
| `byt ut element 3 från a till b`| `('BYT_UT', var, idx, expr)`   | ❌        | ❌        | ❌       | ❌       | ❌          |
| `antal element i lst`          | `('ANTAL', var)`                | ✅        | ✅        | ❌       | ❌       | ❌          |
| `skriv buf till hej.txt`       | `('SKRIV_FIL', path, buf)`     | ✅        | ✅        | ❌       | ❌       | ❌          |
| `läs från hej.txt till buf`    | `('LÄS_FIL', path, var)`        | ✅        | ✅        | ❌       | ❌       | ❌          |

#### Uttryck (Expressions)

| IR nod                      | Språk-konstruktion  | IR-exempel                | Parse impl | Parse test | X86 impl | X86 test | Integration |
|-----------------------------|---------------------|--------------------------|:----------:|:----------:|:--------:|:--------:|:-----------:|
| `('PLUSS', a, b)`           | `a pluss b`         | `('PLUSS', 'x', 1)`      | ✅         | ✅         | ✅       | ✅       | ❌          |
| `('MINUS', a, b)`           | `a minus b`         | `('MINUS', 'x', 1)`      | ✅         | ✅         | ✅       | ✅       | ❌          |
| `('DELA', a, b)`            | `a delat b`         | `('DELA', 'x', 2)`       | ✅         | ✅         | ✅       | ✅       | ❌          |
| `('GÅNGER', a, b)`          | `a gånger b`        | `('GÅNGER', 'x', 2)`     | ✅         | ✅         | ✅       | ✅       | ❌          |

## Nästa steg

### Hög prioritet
1. [x] **IF_ELSE** - parse.py stödjer OM med true_body och false_body
2. [x] **Uppdatera IR** - använd svenska operatorer (mindre, likaMed, etc)
3. [x] **Uppdatera x86 backend** - generera kod för OM (IF) med true/false body
4. [x] **Uppdatera tokenizer** - mappar svenska keywords → IR operatorer
5. [x] **Integrationstester** - test_integration.py med faktisk körning

### Medel prioritet
6. [x] **Fixa UT expression i x86 backend** (PLUSS/MINUS/GÅNGER/DELA i SKRIV funkar nu)
7. [x] **WHILE** - fungerar med samma struktur som IF
8. [ ] **FOR** - implementera x86 backend för för-loop
9. [ ] **SKRIV text** - implementera x86 backend för textutskrift
10. [ ] **Fixa parse-tester** för TA_BORT_INDEX och GE

### Låg prioritet
11. [ ] Självkompilering
12. [ ] HÄMTA_INDEX - implementera parser + x86
13. [ ] BYT_UT - implementera parser + x86

## Kända buggar/problem

- `i` är keyword `IN` → kan inte användas som variabelnamn

## Exempel: hur IR ser ut (ny design)

```python
# Sätt med uttryck
('SÄTT', 'n', ('PLUSS', 'n', 1))

# Om-sats med else
('OM', ('MINDRE', ('VARIABEL', 'x'), ('HELTAL', 5)),
    [('SKRIV', 'hej')],
    [('SKRIV', 'annat')])

# Medansloop
('MEDAN', ('MINDRE', ('VARIABEL', 'x'), ('HELTAL', 5)),
    [('SET', 'x', ('PLUSS', 'x', 1))])

# För-loop (ej implementerad i x86 än)
('FÖR', 'i', 0, 10, [('SKRIV', ('VARIABEL', 'i'))])
```
