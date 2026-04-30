# AGENTS.md - För HIUH-utvecklare

## Viktigt: Använd alltid `run-hiuh.sh` för att köra HIUH-program!

När du testar HIUH-kod (kompilera och köra), använd **ALDRIG** direktkörning av Python eller kompilerade binaries — de kan ha buggar som gör att processen loopar forever.

### Kör HIUH-program
```bash
./run-hiuh.sh <fil.hiuh> [timeout-i-sekunder]
```
Default timeout är 5 sekunder. Om programmet tar längre än så avbryts det.

### Exempel
```bash
./run-hiuh.sh test-program.hiuh 10   # 10 sekunders timeout
./run-hiuh.sh min-fil.hiuh           # 5 sekunders timeout (default)
```

### Om timeout händer
- Programmet har troligtvis en loop, rekursion, eller annan bugg
- Fixa buggen och testa igen
- Öka INTE timeouten för att "lösa" problemet

## Testning
Kör tester med:
```bash
pytest tests/ -v
```

## Arkitektur
- `src/hiuh/tokenize.py` — tokenizer
- `src/hiuh/parse.py` — parser → IR
- `src/hiuh/backend/x86.py` — x86 assembly backend

## IR-noddokumentation

Alla IR-noder ska följa specifikationen i [NODES.md](NODES.md). Innan du implementerar en ny nod eller ändrar en befintlig, läs NODES.md.

### Håll TODO.md i synk
När du implementerar något nytt eller ändrar status på en nod:
1. Uppdatera checkbox-statusen i TODO.md
2. Committa både kodändringen OCH TODO.md i samma commit

### När du lägger till nya IR-noder
1. Lägg till noden i NODES.md med signatur och exempel
2. Lägg till noden i TODO.md med status-kolumner
3. Skriv tester för noden (parse-test + x86-test + integrationstest)
