# HIUH Självkompilering - TODO

## Mål
- [ ] HIUH kompilator skriven i HIUH som kan kompilera sig själv

## Status

### Python-kompilatorn (native/hiuh-native.py) - KLAR
- [x] Tokenizer - fungerar i Python
- [x] Parser - fungerar
- [x] Kodgenerator - genererar x86_64 assembly
- [x] Funktioner (lambda-style)
- [x] IF-ELSE i loopar
- [x] Nästlade loopar

### HIUH tokenizer (hiuh-tokenizer.hiuh) - DELVIS FIXAT
- Status: DELVIS FUNGERANDE (v74, 74fa61e - sista fungerande version)
- Kompileras med Python-native-hiuh → /tmp/tok (x86_64)
- Test: `printf "foo bar" | /tmp/tok` → ger "foo\n001" (bara första ordet + count)
- Bug: När space triggar word-end markering (klar=1), återställer nästa
  teckens ">32"-branch `klar=0` INNAN ordet processas → ordet glöms
- Kortlek: 153 HIUH-ord
- Fungerar korrekt för 1-ord input, tappar 2+ ord

## SJÄLVKOMPILERING - vägen dit

### Nuvarande flöde för självkompilering
1. hiuh-native.py (Python) tokenizerar hiuh-tokenizer.hiuh
2. Ger ord_lista: 153 ord
3. För att kompilera hiuh-tokenizer.hiuh med sig själv, behöver HIUH-ord-listan
   producera samma tokenström som Python-tokenizern

### Nästa steg (prioriterad ordning)
1. [ ] Fixa tokenizer-buggen (word-end detection med "klar"-flagga)
2. [ ] Bygg HIUH-parser i HIUH (för att bygga uttryck)
3. [ ] Bygg HIUH-kodgenerator i HIUH (för att generera asm)
4. [ ] Självkompilerad hiuh.exe som kan kompilera hiuh-tokenizer.hiuh

## Språkdesign — beslutade riktningar

### Typsystem (statisk typning, beslutad)
- [ ] Lägg till `var_type` dict parallellt med `var_reg` i kompilatorn
- [ ] Typer: `Heltal` (64-bit int), `Text` (sträng), `Sant/Falskt` (bool)
- [ ] Typinferens från första tilldelning — ingen explicit deklaration krävs
- [ ] Kompileringsfel vid typkonflikt (t.ex. tilldela Text till Heltal)
- [ ] Funktionssignaturer med returtyp: `ge Heltal` / `ge Text`
- Beslut: statisk typning, inferred från tilldelning, ingen pekare exponerad

### Funktionsanrop (verkliga call/ret, se parser.plan.md §4)
- [ ] Riktig prologue/epilogue per funktion
- [ ] Windows x64 ABI: argument i rcx/rdx/r8/r9, returvärde i rax
- [ ] `Anropa` / `Sätt x till Anropa` syntax
- [ ] Per-funktion variabelallokering (nollställ var_reg vid FUNC_DEF)

### Minnesmodell (beslutad — se DESIGN.md)
- Värdesemantik: tilldelning kopierar alltid, inga delade buffertar
- Text är 256 byte internt, kompilator-genererat namn (_text_0 etc)
- Overflow → runtime abort med tydligt felmeddelande, aldrig tyst trunkering

#### Implementera typsystem
- [ ] Lägg till `var_type` dict i `compile_to_asm` (parallellt med `var_reg`)
- [ ] Vid `SET`: härled typ från värdet (heltal-literal → Heltal, buf → Text)
- [ ] Vid `SET`: kontrollera att ny typ matchar befintlig, annars kompileringsfel
- [ ] `READ_RES` → typ Heltal (returvärde 0/1)
- [ ] `Läs` utan till → tilldelar till implicit Text-variabel `_las_buf`

#### Implementera Text-typ
- [ ] `alloc_text(var)` — genererar `_text_N`-buffert, registrerar i `text_bufs`
- [ ] Tilldelning Text→Text kompileras till `KopieraBuffer`
- [ ] Tilldelning strängliteral→Text kompileras till inline byte-copy
- [ ] `SkrivNyRad`/`Skriv` på Text-variabel → använder rätt buffert automatiskt
- [ ] `Jämför`/`JämförBuffer` på Text-variabler → slår upp buffertnamn automatiskt

#### Implementera overflow-skydd
- [ ] Efter varje `KopieraBuffer` / strängtilldelning: kontrollera att källan ≤ 256 byte
- [ ] Runtime-check: lägg till längdkoll i genererad assembly
- [ ] Felmeddelande: `FEL: Text overflow i variabel 'X'` + exit 1

## Kända buggar
- Tokenizer tappar ord 2+ när space markerar word-end men nästa char återställer klar-flaggan

## Test-kommandon
```bash
# Bygga tokenizer
python3 native/hiuh-native.py --asm hiuh-tokenizer.hiuh > /tmp/tok.asm && as -o /tmp/tok.o /tmp/tok.asm && ld -o /tmp/tok /tmp/tok.o

# Testa tokenizer
printf "foo bar" | /tmp/tok

# Testa ord_lista för självkompilering
python3 native/hiuh-native.py --ord-lista hiuh-tokenizer.hiuh 2>/dev/null | wc -w
```
