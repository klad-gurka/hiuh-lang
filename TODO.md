# HIUH Självkompilering - TODO

## Mål
- [ ] HIUH kompilator skriven i HIUH som kan kompilera sig själv

## IR-nodstatus
För detaljer om varje nod (signatur, parametrar, exempel), se [NODES.md](NODES.md).

### Satser (Statements)
| IR nod | Parse impl | Parse test | X86 impl | X86 test | Integration |
|--------------------------------|:---------:|:---------:|:--------:|:--------:|:-----------:|
| SÄTT | ✅ | ✅ | ✅ | ✅ | ❌ |
| FÖR | ✅ | ✅ | ✅ | ✅ | ❌ |
| MEDAN | ✅ | ✅ | ✅ | ✅ | ❌ |
| OM | ✅ | ✅ | ✅ | ✅ | ❌ |
| BRYT | ✅ | ✅ | ❌ | ❌ | ❌ |
| HEJDÅ | ✅ | ✅ | ❌ | ❌ | ❌ |
| SKRIV | ✅ | ✅ | ❌ | ❌ | ❌ |
| SKRIV_VÄRDE | ✅ | ✅ | ✅ | ❌ | ❌ |
| LÄS_RAD | ✅ | ✅ | ❌ | ❌ | ❌ |
| GREJ | ✅ | ✅ | ❌ | ❌ | ❌ |
| ANROPA | ✅ | ✅ | ❌ | ❌ | ❌ |
| GE | ✅ | ❌ | ❌ | ❌ | ❌ |
| NY_LISTA | ✅ | ✅ | ✅ | ❌ | ❌ |
| LÄGG_TILL | ✅ | ✅ | ❌ | ❌ | ❌ |
| TA_BORT | ✅ | ✅ | ❌ | ❌ | ❌ |
| TA_BORT_INDEX | ✅ | ❌ | ✅ | ❌ | ❌ |
| HÄMTA_INDEX | ❌ | ❌ | ❌ | ❌ | ❌ |
| BYT_UT | ❌ | ❌ | ❌ | ❌ | ❌ |
| ANTAL | ✅ | ✅ | ❌ | ❌ | ❌ |
| SKRIV_FIL | ✅ | ✅ | ❌ | ❌ | ❌ |
| LÄS_FIL | ✅ | ✅ | ❌ | ❌ | ❌ |

### Uttryck (Expressions)
| IR nod | Parse impl | Parse test | X86 impl | X86 test | Integration |
|------------------------------|:----------:|:----------:|:--------:|:--------:|:-----------:|
| PLUSS | ✅ | ✅ | ✅ | ✅ | ❌ |
| MINUS | ✅ | ✅ | ✅ | ✅ | ❌ |
| DELA | ✅ | ✅ | ✅ | ✅ | ❌ |
| GÅNGER | ✅ | ✅ | ✅ | ✅ | ❌ |

### Jämförelseoperatorer
| IR nod | Parse impl | Parse test | X86 impl | X86 test | Integration |
|----------|:----------:|:----------:|:--------:|:--------:|:-----------:|
| mindre | ✅ | ✅ | ✅ | ✅ | ❌ |
| mindreLikaMed | ✅ | ✅ | ✅ | ✅ | ❌ |
| större | ✅ | ✅ | ✅ | ✅ | ❌ |
| störreLikaMed | ✅ | ✅ | ✅ | ✅ | ❌ |
| likaMed | ✅ | ✅ | ✅ | ✅ | ❌ |
| inteLikaMed | ✅ | ✅ | ✅ | ✅ | ❌ |

## Nästa steg

### Hög prioritet
1. [x] IF_ELSE, WHILE, Swedish IR operators, Integration tests, Swedish IR in x86

### Medel prioritet
2. [ ] FOR x86 backend
3. [ ] SKRIV text x86 backend
4. [ ] Parse-tester för TA_BORT_INDEX och GE
5. [ ] X86-tester för SKRIV_VÄRDE och NY_LISTA

### Låg prioritet
6. [ ] Självkompilering
7. [ ] HÄMTA_INDEX
8. [ ] BYT_UT

## Kända buggar/problem

- `i` är keyword `IN` → kan inte användas som variabelnamn

## Ändringslogg

### 2026-04-30
- [x] **FIX**: parse.py `parse_for`: body loop använde `child_indent < base_indent` för dedent-check vilket orsakade infinite loop när nästa rad har samma indent som FOR-linjen. Ändrad till `child_indent <= base_indent` (som redan fanns i WHILE och IF). Symptom: `sätt x till x pluss 1` i FOR-body gav `('SET', 'x', 'pluss')` istället för `('SET', 'x', ('PLUSS', 'x', 1))`.
- [x] **TEST**: Lade till `test_for_body_with_arithmetic` i tests/test_parse.py
- [x] **TEST**: Fixade `test_list_init` som felaktigt förväntade sig `LIST_INIT` istället för `NY_LISTA`
