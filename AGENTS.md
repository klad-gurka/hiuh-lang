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
