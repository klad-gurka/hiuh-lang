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
```

## IR-design

### Principer
- IR ska följa HIUH:s svenska språk så nära som möjligt
- Operatorer ska vara korta men läsbara svenska ord
- Tokenizern mappar svenska alias → IR operatorer
- Parse.py产出 enhetliga IR-namn, oavsett vilket keyword som användes

### Operatorer (Jämförelse)

| IR operator     | Source keywords               | Betydelse |
|-----------------|-------------------------------|-----------|
| `mindre`        | "är mindre än"                | a < b     |
| `mindreLikaMed` | "är mindre än eller lika med" | a <= b    |
| `större`        | "är större än"                | a > b     |
| `störreLikaMed` | "är större än eller lika med" | a >= b    |
| `likaMed`       | "är lika med"                 | a == b    |
| `inteLikaMed`   | "är inte lika med"            | a != b    |

### IR-nod dokumentation

#### Satser (Statements)

| Språk-konstruktion                 | IR nod                                | IR-exempel                                                                                 | X86 | WASM |
|------------------------------------|---------------------------------------|--------------------------------------------------------------------------------------------|-----|------|
| `sätt x till 5`                    | `('SÄTT', name, expr)`                | `('SÄTT', 'x', ('HELTAL', 5))`                                                             | ❌   | ❌    |
| `för x från 0 till 10`             | `('FÖR', var, start, end, body)`      | `('FÖR', 'x', 0, 10, [body])`                                                              | ❌   | ❌    |
| `medan x är mindre än 5`           | `('MEDAN', expr, body)`               | `('MEDAN', ('MINDRE', ('VARIABEL', 'x'), ('HELTAL', 5)), [body])`                          | ❌   | ❌    |
| `om x är mindre än 5`              | `('OM', expr, true_body, false_body)` | `('OM', ('MINDRE', ('VARIABEL', 'x'), ('HELTAL', 5)), [...], [...])`                       | ❌   | ❌    |
| `bryt`                             | `('BRYT',)`                           | `('BRYT',)`                                                                                | ❌   | ❌    |
| `hej då` / `jag gå nu`             | `('HEJDÅ',)`                          | `('HEJDÅ',)`                                                                               | ❌   | ❌    |
| `skriv hello`                      | `('SKRIV', expr)`                     | `('SKRIV', ('TEXT', 'hello'))`                                                             | ❌   | ❌    |
| `skriv radbryt`                    | `('SKRIV', expr)`                     | `('SKRIV', ('RADBRYT',))`                                                                  | ❌   | ❌    |
| `skriv värdet av x`                | `('SKRIV_VÄRDE', name)`               | `('SKRIV', ('VARIABEL', 'x'))`                                                             | ❌   | ❌    |
| `läs rad till x`                   | `('LÄS_RAD', name)`                   | `('LÄS_RAD', 'x')`                                                                         | ❌   | ❌    |
| `sätt funk till grej med a, b`     | `('GREJ', params, body)`              | `('SÄTT', 'funk', ('GREJ', ['a', 'b'], [body])`                                            | ❌   | ❌    |
| `sätt a till funk med x, y`        | `('ANROPA', var, args)`               | `('SÄTT', 'x', ('ANROPA', 'funk', [('VARIABEL', 'x'), ('VARIABEL', 'y')])`                 | ❌   | ❌    |
| `ge x`                             | `('GE', expr)`                        | `('GE', ('VARIABEL', 'x'))`                                                                | ❌   | ❌    |
| `sätt a till ny lista`             | `('NY_LISTA', args)`                  | `('SÄTT', ('VARIABEL', 'a'), ('NY_LISTA', []))`                                            | ❌   | ❌    |
| `sätt a till ny lista med 1, 2, 3` | `('NY_LISTA', args)`                  | `('SÄTT', ('VARIABEL', 'a'), ('NY_LISTA', [('HELTAL', 1), ('HELTAL', 2), ('HELTAL', 3)]))` | ❌   | ❌    |
| `lägg till x i a`                  | `('LÄGG_TILL', expr, var)`            | `('LÄGG_TILL', ('VARIABEL', x'), 'a')`                                                     | ❌   | ❌    |
| `ta bort apa från a`               | `('TA_BORT', expr, var)`              | `('TA_BORT', ('TEXT', 'apa'), 'a')`                                                        | ❌   | ❌    |
| `ta bort element 3 från a`         | `('TA_BORT_INDEX', index, var)`       | `('TA_BORT_INDEX', 3, 'a')`                                                                | ❌   | ❌    |
| `sätt x till element 3 från a`     | `('HÄMTA_INDEX', index, var)`         | `('SÄTT', 'x', ('HÄMTA_INDEX', 3, 'a'))`                                                   | ❌   | ❌    |
| `byt ut element 3 från a till b`   | `('BYT_UT', index, var, expr)`        | `('BYT_UT', 3, 'a', ('VARIABEL', 'b'))`                                                    | ❌   | ❌    |
| `antal element i lst`              | `('ANTAL', var)`                      | `('ANTAL', 'lst')`                                                                         | ❌   | ❌    |
| `skriv buf till hej.txt`           | `('SKRIV_FIL', text, path)`           | `('SKRIV_VAR', 'buf', 'hej.txt')`                                                          | ❌   | ❌    |
| `läs från hej.txt till buf`        | `('LÄS_FIL', path, var)`              | `('LÄS', ('TEXT', 'hej.txt'), 'buf'))`                                                     | ❌   | ❌    |

TODO: uppdatera tabell ovan med korrekt x86-status

#### Uttryck (Expressions)

| IR nod             | Språk-konstruktion | IR-exempel           | X86 | WASM |
|--------------------|--------------------|----------------------|-----|------|
| `('PLUSS', a, b)`  | `a pluss b`        | `('PLUSS', 'x', 1)`  | ✅ | ❌ |
| `('MINUS', a, b)`  | `a minus b`        | `('MINUS', 'x', 1)`  | ❌ | ❌ |
| `('DELA', a, b)`   | `a delat b`        | `('DELA', 'x', 2)`   | ❌ | ❌ |
| `('GÅNGER', a, b)` | `a gånger b`       | `('GÅNGER', 'x', 2)` | ❌ | ❌ |

## Nästa steg

### Hög prioritet
1. [x] **IF_ELSE** - parse.py stödjer OM med true_body och false_body
2. [ ] **Uppdatera IR** - använd svenska operatorer (mindre, likaMed, etc)
3. [ ] **Uppdatera x86 backend** - generera kod för OM (IF) med true/false body
4. [ ] **Uppdatera tokenizer** - mappar svenska keywords → IR operatorer

### Medel prioritet
5. [ ] **Fixa UT expression i x86 backend** (PLUS ok, MINUS/GENOM saknas)
6. [ ] **Implementera WHILE med OM-format** (nuvarande WHILE är annorlunda)

### Låg prioritet
7. [ ] WASM backend
8. [ ] Självkompilering

## Kända buggar/problem

- `i` är keyword `IN` → kan inte användas som variabelnamn

## Exempel: hur IR ser ut (ny design)

```python
# Om-sats med else
('OM', ('MINDRE', ('VARIABEL', 'x'), ('HELTAL', '5')),
    [('SKRIV', 'hej')],
    [('SKRIV', 'annat')])

# För-loop med body
('FÖR', 'i', '0', '10',
    [('SKRIV', 'i')])

# Sätt med uttryck
('SÄTT', 'n', ('PLUS', 'n', '1'))
```