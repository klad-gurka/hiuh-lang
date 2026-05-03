# HIUH Självkompilering - TODO

## Mål
- [ ] HIUH kompilator skriven i HIUH som kan kompilera sig själv

---

## Självkompilering — Specificerade deluppgifter

### Fas 0: Utforska och planera (analys, inte kod)

- [ ] **0.1** Analysera nuvarande Python-kompilatorns arkitektur
  - Vilka Python-features används? (datastrukturer, string manipulation, syscalls, etc.)
  - Vilka begränsningar i HIUH hindrar direktöversättning?
  - Identifiera de Python-konstruktioner som kräver creative HIUH-lösningar

- [ ] **0.2** Bestäm översättningsstrategi
  - Fullständig HiUH-skriven kompilator? Eller minimal Python-bootstrap som läser HIUH-kod?
  - Definiera "självkompilerad": endast tokenizer+parse+x86, eller även standardbibliotek?

- [ ] **0.3** Skapa en plan för minimum viable self-hosting
  - Vilken minimal delmängd räcker för att kompilera resten?

### Fas 1: Språkfunktioner som behövs utöver dagens IR-nodstatus

- [ ] **1.1** VARIABEL-nod (IR): uttryck som refererar till en variabels värde
  - Existerar redan implicit? Behövs explicit nod?
  - Swedish alias: behövs `variabel` som IR-nod?

- [ ] **1.2** HELTAL-nod: literals för numeriska värden
  - Finns redan i parse? Behövs explicit nod?

- [ ] **1.3** FUNKTIONSANROP som uttryck (returvärde-användning)
  - `anropa` returnerar ett värde som kan användas i uttryck
  - Kräver att returvärdet lagras i ett register och används direkt

- [ ] **1.4** Strängliteraler i uttryck
  - Parser: `TEXT "hej"` eller `text "hej"` → strängliteral
  - Behövs för strängar i koden (filepath, etc.)

- [ ] **1.5** Logiska uttryck (AND/OR/NOT)
  - `OR` redan i keywords
  - Behövs för villkor i `OM`, `MEDAN`

- [ ] **1.6** Stringmanipulation (indexering, substring, length)
  - `HÄMTA_INDEX` fungerar för strängar?
  - Behövs?: `LÄNGD` (antal tecken), `DELSTR` (substring)

- [ ] **1.7** Typkonvertering
  - Heltal → Text: `text_av(x)` eller `ge_text(x)`
  - Text → Heltal: `heltal_av(x)` eller `ge_heltal(x)`
  - Krävs för att läsa filstorlekar, argument till syscall, etc.

### Fas 2: IR-noder som saknas för att uttrycka kompilatorlogik

- [ ] **2.1** INLINE ASSEMBLY eller SYSCALL-nod
  - För att anropa Linux-syscall direkt (read, write, open, close, mmap, mprotect)
  - Alternativ: HIUH-wrapper-funktioner i assembly som HIUH-koden anropar
  - Krävs för: fil-I/O (läs HIUH-källa), minnesallokering, process-creation

- [ ] **2.2**pekare/artimetik
  - Läsa minne vid adress: `MEMORY_READ(addr, size)` → `('MEMORY_READ', addr, size)`
  - Skriva minne: `MEMORY_WRITE(addr, value, size)`
  - Krävs för: JIT-kompilering (skriva maskinkod till minne), minnesallokering, function-pointers

- [ ] **2.3** Function pointers / dynamiska anrop
  - Kunna anropa en funktion vars adress lagrats i en variabel
  - Krävs för: att kompilera funktioner som genererar kod (compile_expr → anropa kodgenerator)

- [ ] **2.4** Villkorsuttryck (ternary eller explicit IF som uttryck)
  - `OM cond then else` som uttryck, inte bara som sats
  - Krävs för: kompakt kod, men kan simuleras med temporär variabel

- [ ] **2.5** Struct/composite types (för IR-nod representation)
  - För att representera tokens, AST-nodes, symboltable-entries
  - Kan använda listor (NY_LISTA) men behövs strong typing?

### Fas 3: Kompilatorstruktur att uttrycka i HIUH

- [ ] **3.1** Tokenizer skriven i HIUH
  - Input: sträng (HIUH-källa)
  - Output: lista av tokens (tokens med typ + värde)
  - Kräver: strängindexering, loop, villkor, funktioner

- [ ] **3.2** Parser skriven i HIUH
  - Input: tokenlista
  - Output: IR (lista av satser)
  - Kräver: rekursiv descent eller iterative parsing, lookahead

- [ ] **3.3** IR-representation (mellanformat)
  - Hur representeras IR-noder? Som HIUH-liststruktur?
  - `('SÄTT', 'x', 5)` → måste kunna lagras i HIUH-lista

- [ ] **3.4** x86-code generator skriven i HIUH
  - Input: IR
  - Output: x86 assembly (sträng)
  - Kräver: strängbyggning, registrallocering, labelhantering

- [ ] **3.5** Fil-I/O för att läsa HIUH-källa
  - `LÄS_FIL` → läsa källfilen
  - `SKRIV_FIL` → skriva genererad assembly

- [ ] **3.6** Körbar generering (gcc-assemblera och linka)
  - Anropa gcc via syscall/CLI
  - Eller: generera maskedkod som körs direkt (JIT)

### Fas 4: Tekniska utmaningar

- [ ] **4.1** Självreferens i kompilatorn
  - Kompilatorn refererar till sig själv: `Sätt tokenizer till anropa skapa_tokenizer`
  - Hur hantera circular imports/definitions?

- [ ] **4.2** Minneshantering
  - HIUH har inga explicita pekare i användarsynlighet
  - Men kompilatorn behöver allokera minne för AST, symboltabeller, genererad kod
  - Lösning: använd lista som heap, eller `MMAP` för att reservera minne

- [ ] **4.3** Rekursion
  - Parser behöver rekursion (nestade uttryck)
  - Hur djupt? Finns stack-gräns?
  - Kräver: `GE` funktionsretur, `ANROPA` med rekursiva anrop

- [ ] **4.4** Bootstrapping-ordning
  - Vilken del av kompilatorn kompileras först?
  - Minsta möjliga HIUH-kompilator → används för att kompilera resten?

### Fas 5: Testning och validering

- [ ] **5.1** Kompilera tokenizer.hiuh med Python-kompilatorn → tokenizer.s
- [ ] **5.2** Kompilera tokenizer.s med gcc → tokenizer_binär
- [ ] **5.3** Köra tokenizer_binär på HIUH-källkod → tokens
- [ ] **5.4** Jämför utdata med Python-tokenizer: samma tokens?
- [ ] **5.5** Stegvis: kompilera hela kompilatorn med sig själv → identiskt resultat?

### Fas 6: Minimal proof-of-concept

- [ ] **6.1** Skriv minimal HIUH-tokenizer i HIUH (grundfunktion: tokenisera nyckelord + siffror)
- [ ] **6.2** Verifiera att den producerar samma tokens som Python-versionen
- [ ] **6.3** Utöka stegvis till full tokenizer
- [ ] **6.4** Integrera med resten av pipeline

---

## IR-nodstatus
För detaljer om varje nod (signatur, parametrar, exempel), se [NODES.md](NODES.md).

### Satser (Statements)
| IR nod | Parse impl | Parse test | X86 impl | X86 test | Integration |
|--------------------------------|:---------:|:---------:|:--------:|:--------:|:-----------:|
| SÄTT | ✅ | ✅ | ✅ | ✅ | ✅ |
| FÖR | ✅ | ✅ | ✅ | ✅ | ✅ |
| MEDAN | ✅ | ✅ | ✅ | ✅ | ✅ |
| OM | ✅ | ✅ | ✅ | ✅ | ✅ |
| BRYT | ✅ | ✅ | ✅ | ✅ | ✅ |
| HEJDÅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| SKRIV | ✅ | ✅ | ✅ | ✅ | ✅ |  # unified: text, variabel, uttryck, radbryt |
| LÄS_RAD | ✅ | ✅ | ✅ | ✅ | ✅ |  # +tokenizer + parse + x86 + tester |
| GREJ | ✅ | ✅ | ✅ | ✅ | ✅ |  # +x86 test + integration (fix: CURRENT_FUNC, return save) |
| ANROPA | ✅ | ✅ | ✅ | ✅ | ✅ |  # +x86 test + integration (fix: return value save) |
| GE | ✅ | ✅ | ✅ | ✅ | ✅ |  # +x86 test + integration (epilogue jump) |
| NY_LISTA | ✅ | ✅ | ✅ | ✅ | ✅ |
| LÄGG_TILL | ✅ | ✅ | ✅ | ✅ | ✅ |  # +x86 test + integration |
| TA_BORT | ✅ | ✅ | ✅ | ✅ | ✅ |  # +x86 test + integration |
| TA_BORT_INDEX | ✅ | ✅ | ✅ | ✅ | ✅ |  # +x86 test +integration (fix: movl 32-bit length) |
| HÄMTA_INDEX | ✅ | ✅ | ✅ | ✅ | ✅ |  # LIST_GET i SET + integration |
| BYT_UT | ✅ | ✅ | ✅ | ✅ | ✅ |  # Ny: tokenizer + parse + x86 + tester |
| ANTAL | ✅ | ✅ | ✅ | ✅ | ✅ |  # +x86 test + integration |
| SKRIV_FIL | ✅ | ✅ | ✅ | ✅ | ✅ |  # +x86 fix (open/write/close) + tester |
| LÄS_FIL | ✅ | ✅ | ✅ | ✅ | ✅ |  # +tokenizer + parse + x86 + tester |

### Uttryck (Expressions)
| IR nod | Parse impl | Parse test | X86 impl | X86 test | Integration |
|------------------------------|:----------:|:----------:|:--------:|:--------:|:-----------:|
| PLUSS | ✅ | ✅ | ✅ | ✅ | ✅ |
| MINUS | ✅ | ✅ | ✅ | ✅ | ✅ |
| DELA | ✅ | ✅ | ✅ | ✅ | ✅ |
| GÅNGER | ✅ | ✅ | ✅ | ✅ | ✅ |

### Jämförelseoperatorer
| IR nod | Parse impl | Parse test | X86 impl | X86 test | Integration |
|----------|:----------:|:----------:|:--------:|:--------:|:-----------:|
| mindre | ✅ | ✅ | ✅ | ✅ | ✅ |
| mindreLikaMed | ✅ | ✅ | ✅ | ✅ | ✅ |
| större | ✅ | ✅ | ✅ | ✅ | ✅ |
| störreLikaMed | ✅ | ✅ | ✅ | ✅ | ✅ |
| likaMed | ✅ | ✅ | ✅ | ✅ | ✅ |
| inteLikaMed | ✅ | ✅ | ✅ | ✅ | ✅ |

## Nästa steg

### Hög prioritet
1. [x] IF_ELSE, WHILE, Swedish IR operators, Integration tests, Swedish IR in x86
2. [x] FOR integrationstest (x86 impl ✅, saknar integrationstest)
3. [x] SKRIV text x86 backend
4. [x] Parse-tester för TA_BORT_INDEX och GE
5. [x] X86-tester för SKRIV_VÄRDE och NY_LISTA
6. [x] HEJDÅ x86 backend

### Låg prioritet
7. [ ] Självkompilering (se Fas 0–6 ovan)
8. [x] HÄMTA_INDEX (LIST_GET i SET + TA_BORT_INDEX x86 test + integration)
9. [x] BYT_UT (ny: tokenizer + parse + x86 + tester)

## Kända buggar/problem

- `i` är keyword `IN` → kan inte användas som variabelnamn (DELVIS FIXAT: `i` efter operatorer som `FÖR`, `PLUSS`, etc. behandlas nu som variabel, men `i` som variabel i andra sammanhang kan fortfarande kollidera med `IN`-nyckelordet)

- **UTF-8 byte-räkning**: `Skriv`-satser med svenska tecken (t.ex. `ö`) kan producera trasig output eftersom `len(text)` returnerar Unicode-tecken-antal istället för byte-antal. Backend använder `len(text)` men x86 syscalls behöver byte-count. (Ej fixat ännu.)

## Fixade buggar (2026-05-03)

- **IF-ELSE-i-FOR bug**: `Sätt i till i + 1` (med `+`) producerade `Sätt i till i` (ingen inkrementering) eftersom `+` inte var i KEYWORDS. Fix: lade till `'+': 'PLUSS'` etc. i tokenizer KEYWORDS.
  - Commit: `81936d6` fixade redan parse_if som använde `base_indent` istället för `indent` vid ELSE-detektering
  - Tokenizer-fix: `+`, `-`, `*`, `/` → PLUSS, MINUS, GÅNGER, DELA

- **`Skriv <bare_word>` som text literal**: `Skriv Större` behandlades som variabel-referens (`VARIABEL`) istället för text. Fix: `parse_skriv_expr` returnerar nu `('TEXT', token)` för bare words. `Skriv värdet av x` ger variabel-värde.

- **`i` efter operatorer**: `i` efter `FÖR`, `PLUSS`, `MINUS`, etc. behandlades som `IN`-keyword istället för variabel. Fix: uppdaterade tokenizer-logiken för `i`-efter-operator-kontroll med `prev_word.lower()` och lagt till `+`, `-`, `*`, `/` i tuple.

- **`skriv värdet av x`**: tokenizer producerade `SKRIV` + variabel istället för `SKRIV_VAR`. Fix: ändrade till `SKRIV_VAR`-token som explicit markerar variabel-värde-utskrift.