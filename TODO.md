# HIUH Självkompilering - TODO

## Mål
- [ ] HIUH kompilator skriven i HIUH som kan kompilera sig själv

## IR-nodstatus
För detaljer om varje nod (signatur, parametrar, exempel), se [NODES.md](NODES.md).

### Satser (Statements)
| IR nod | Parse impl | Parse test | X86 impl | X86 test | Integration |
|--------------------------------|:---------:|:---------:|:--------:|:--------:|:-----------:|
| SÄTT | ✅ | ✅ | ✅ | ✅ | ❌ |
| FÖR | ✅ | ✅ | ❌ | ❌ | ❌ |
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
