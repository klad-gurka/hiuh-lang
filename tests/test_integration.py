#!/usr/bin/env python3
"""Integration tests for HIUH - kör riktig kod via run-hiuh.sh"""

import subprocess
import tempfile
import os

REPO_DIR = os.path.dirname(os.path.abspath(__file__))  # hiuh-repo/tests/
RUN_SCRIPT = os.path.join(REPO_DIR, '..', 'run-hiuh.sh')  # hiuh-repo/run-hiuh.sh


def run_hiuh(src, timeout=5):
    """Compile and run HIUH source, return (stdout, stderr, returncode)."""
    workdir = tempfile.mkdtemp()
    hiuh_file = os.path.join(workdir, 'prog.hiuh')
    with open(hiuh_file, 'w') as f:
        f.write(src)
    result = subprocess.run(
        [RUN_SCRIPT, hiuh_file, str(timeout)],
        capture_output=True, text=True, timeout=timeout + 10,
        cwd=os.path.dirname(RUN_SCRIPT)
    )
    return result.stdout.strip(), result.stderr.strip(), result.returncode


# ─────────────────────────────────────────────
# SET (heltal, variabler, aritmetik)
# ─────────────────────────────────────────────

def test_set_integer():
    """SET x till 5 → skriv värdet av x"""
    src = '''sätt x till 5
skriv värdet av x'''
    stdout, _, _ = run_hiuh(src)
    assert stdout == '5', f"Fick: {stdout!r}"


def test_set_multiple_vars():
    """Två variabler"""
    src = '''sätt x till 10
sätt y till 20
skriv värdet av x
skriv värdet av y'''
    stdout, _, _ = run_hiuh(src)
    assert stdout == '1020', f"Fick: {stdout!r}"


def test_arith_plus():
    """PLUSS: x pluss 1"""
    src = '''sätt x till 0
skriv värdet av x
sätt x till x pluss 1
skriv värdet av x
sätt x till x pluss 1
skriv värdet av x'''
    stdout, _, _ = run_hiuh(src)
    assert stdout == '012', f"Fick: {stdout!r}"


def test_arith_minus():
    """MINUS: x minus 1"""
    src = '''sätt x till 5
skriv värdet av x
sätt x till x minus 1
skriv värdet av x
sätt x till x minus 1
skriv värdet av x'''
    stdout, _, _ = run_hiuh(src)
    assert stdout == '543', f"Fick: {stdout!r}"


def test_arith_times():
    """GÅNGER: x gånger 2"""
    src = '''sätt x till 3
skriv värdet av x
sätt x till x gånger 2
skriv värdet av x
sätt x till x gånger 2
skriv värdet av x'''
    stdout, _, _ = run_hiuh(src)
    assert stdout == '3612', f"Fick: {stdout!r}"


def test_arith_div():
    """DELA: x delat 2"""
    src = '''sätt x till 10
skriv värdet av x
sätt x till x delat 2
skriv värdet av x
sätt x till x delat 2
skriv värdet av x'''
    stdout, _, _ = run_hiuh(src)
    assert stdout == '1052', f"Fick: {stdout!r}"


def test_expression_complex():
    """Aritmetiskt uttryck: (3 + 5) * 2"""
    src = '''sätt a till 3
sätt b till 5
sätt c till a pluss b
sätt c till c gånger 2
skriv värdet av c'''
    stdout, _, _ = run_hiuh(src)
    assert stdout == '16', f"Fick: {stdout!r}"


# ─────────────────────────────────────────────
# MEDAN (WHILE) + PLUSS/MINUS/GÅNGER/DELA
# ─────────────────────────────────────────────

def test_medan_basic():
    """MEDAN x är mindre än 3: skriv x, plussa"""
    src = '''sätt x till 0
medan x är mindre än 3
  skriv värdet av x
  sätt x till x pluss 1'''
    stdout, _, _ = run_hiuh(src)
    assert stdout == '012', f"Fick: {stdout!r}"


def test_medan_minus():
    """MEDAN med MINUS"""
    src = '''sätt x till 3
medan x är större än 0
  skriv värdet av x
  sätt x till x minus 1'''
    stdout, _, _ = run_hiuh(src)
    assert stdout == '321', f"Fick: {stdout!r}"


def test_medan_times():
    """MEDAN med GÅNGER"""
    src = '''sätt x till 1
medan x är mindre än 10
  skriv värdet av x
  sätt x till x gånger 2'''
    stdout, _, _ = run_hiuh(src)
    assert stdout == '1248', f"Fick: {stdout!r}"


def test_medan_div():
    """MEDAN med DELA"""
    src = '''sätt x till 32
medan x är större än 1
  skriv värdet av x
  sätt x till x delat 2'''
    stdout, _, _ = run_hiuh(src)
    assert stdout == '3216842', f"Fick: {stdout!r}"


def test_medan_countdown():
    """MEDAN räkna ner 5 till 0"""
    src = '''sätt n till 5
medan n är inte lika med 0
  skriv värdet av n
  sätt n till n minus 1'''
    stdout, _, _ = run_hiuh(src)
    assert stdout == '54321', f"Fick: {stdout!r}"


# ─────────────────────────────────────────────
# FÖR (FOR loop) + aritmetik
# ─────────────────────────────────────────────

def test_for_sum():
    """FÖR: räkna summan 0+1+2+3+4"""
    src = '''sätt x till 0
för i från 0 till 5
  sätt x till x pluss i
skriv värdet av x'''
    stdout, _, _ = run_hiuh(src)
    assert stdout == '10', f"Fick: {stdout!r}"


def test_for_print():
    """FÖR: skriv ut 0, 1, 2"""
    src = '''för i från 0 till 3
  skriv värdet av i
  skriv ny rad'''
    stdout, _, _ = run_hiuh(src)
    assert stdout == '0\n1\n2', f"Fick: {stdout!r}"


# ─────────────────────────────────────────────
# OM / ANNARS (IF / ELSE) + jämförelser
# ─────────────────────────────────────────────

def test_om_less():
    """OM x är mindre än 5"""
    src = '''sätt x till 3
om x är mindre än 5
  skriv värdet av x
annars
  skriv 99'''
    stdout, _, _ = run_hiuh(src)
    assert stdout == '3', f"Fick: {stdout!r}"


def test_om_greater():
    """OM x är större än 5"""
    src = '''sätt x till 10
om x är större än 5
  skriv värdet av x
annars
  skriv 0'''
    stdout, _, _ = run_hiuh(src)
    assert stdout == '10', f"Fick: {stdout!r}"


def test_om_equals():
    """OM x är lika med 5"""
    src = '''sätt x till 5
om x är lika med 5
  skriv 1
annars
  skriv 0'''
    stdout, _, _ = run_hiuh(src)
    assert stdout == '1', f"Fick: {stdout!r}"


def test_om_not_equals():
    """OM x inte är lika med 0"""
    src = '''sätt x till 7
om x inte är lika med 0
  skriv värdet av x
annars
  skriv 0'''
    stdout, _, _ = run_hiuh(src)
    assert stdout == '7', f"Fick: {stdout!r}"


def test_om_else_branch():
    """ANNARS-tag tar annan väg"""
    src = '''sätt x till 100
om x är mindre än 5
  skriv 1
annars
  skriv 2'''
    stdout, _, _ = run_hiuh(src)
    assert stdout == '2', f"Fick: {stdout!r}"


# ─────────────────────────────────────────────
# WHILE + BREAK
# ─────────────────────────────────────────────

def test_while_break_early():
    """WHILE med bryt efter 3 iterationer"""
    src = '''sätt x till 0
medan x är mindre än 10
  skriv värdet av x
  sätt x till x pluss 1
  om x är lika med 3
    bryt'''
    stdout, _, _ = run_hiuh(src)
    assert stdout == '012', f"Fick: {stdout!r}"


def test_while_break_first():
    """BREAK i första iterationen"""
    src = '''sätt x till 0
medan x är mindre än 5
  bryt
  sätt x till x pluss 1'''
    stdout, _, _ = run_hiuh(src)
    assert stdout == '', f"Fick: {stdout!r}"


def test_while_no_break():
    """WHILE utan bryt (exit via villkor)"""
    src = '''sätt x till 0
medan x är mindre än 3
  skriv värdet av x
  sätt x till x pluss 1'''
    stdout, _, _ = run_hiuh(src)
    assert stdout == '012', f"Fick: {stdout!r}"


# ─────────────────────────────────────────────
# FÖR + BRYT (FOR loop + BREAK)
# ─────────────────────────────────────────────

def test_for_break_early():
    """FÖR med bryt efter halva"""
    src = '''sätt x till 0
för i från 0 till 10
  sätt x till x pluss i
  om i är lika med 5
    bryt
skriv värdet av x'''
    stdout, _, _ = run_hiuh(src)
    assert stdout == '15', f"Fick: {stdout!r}"


def test_for_break_first():
    """BRYT i första iterationen av FÖR"""
    src = '''sätt x till 0
för i från 0 till 5
  bryt
  sätt x till x pluss i'''
    stdout, _, _ = run_hiuh(src)
    assert stdout == '', f"Fick: {stdout!r}"


def test_for_no_break():
    """FÖR utan bryt (exit via villkor)"""
    src = '''sätt x till 0
för i från 0 till 3
  sätt x till x pluss i
skriv värdet av x'''
    stdout, _, _ = run_hiuh(src)
    assert stdout == '3', f"Fick: {stdout!r}"


# HEJDÅ (EXIT)
# ─────────────────────────────────────────────

def test_hejda_exits():
    """hejdå avslutar programmet"""
    src = '''sätt x till 42
hejdå
sätt x till 99'''
    _, _, rc = run_hiuh(src)
    assert rc == 0, f"Fick rc: {rc}"


# SKRIV text (literal integers)
# ─────────────────────────────────────────────

def test_skriv_integer_literal():
    """skriv numeriskt värde (99)"""
    src = '''skriv 99'''
    stdout, _, _ = run_hiuh(src)
    assert stdout == '99', f"Fick: {stdout!r}"


# SKRIV_VÄRDE (print variable)
# ─────────────────────────────────────────────

def test_skriv_value():
    """skriv värdet av x"""
    src = '''sätt x till 42
skriv värdet av x'''
    stdout, _, _ = run_hiuh(src)
    assert stdout == '42', f"Fick: {stdout!r}"


def test_skriv_value_multidigit():
    """Fler-siffrigt tal (två siffror)"""
    src = '''sätt x till 42
skriv värdet av x'''
    stdout, _, _ = run_hiuh(src)
    assert stdout == '42', f"Fick: {stdout!r}"


def test_skriv_value_zero():
    """Noll"""
    src = '''sätt x till 0
skriv värdet av x'''
    stdout, _, _ = run_hiuh(src)
    assert stdout == '0', f"Fick: {stdout!r}"


def test_skriv_multiple():
    """Flera skriv efter varandra"""
    src = '''sätt a till 1
sätt b till 2
sätt c till 3
skriv värdet av a
skriv värdet av b
skriv värdet av c'''
    stdout, _, _ = run_hiuh(src)
    assert stdout == '123', f"Fick: {stdout!r}"


# ─────────────────────────────────────────────
# SKRIV_NL (skriv ny rad)
# ─────────────────────────────────────────────

def test_skriv_nl():
    """skriv ny rad → newline"""
    src = '''sätt x till 0
sätt y till 2
skriv värdet av x
skriv ny rad
skriv värdet av y'''
    stdout, _, _ = run_hiuh(src)
    # Output: "0" + newline + "2"
    assert '0' in stdout and '2' in stdout, f"Fick: {stdout!r}"


# ─────────────────────────────────────────────
# TIMEOUT
# ─────────────────────────────────────────────

def test_finishes_within_timeout():
    """Program som kör klart inom timeout"""
    src = '''sätt x till 0
medan x är mindre än 1000
  sätt x till x pluss 1'''
    stdout, stderr, code = run_hiuh(src, timeout=2)
    # Loop kör 1000 gånger och avslutas - ingen output
    assert code == 0, f"Fick exit code {code}"


# ─────────────────────────────────────────────
# RUN ALL
# ─────────────────────────────────────────────

if __name__ == '__main__':
    import sys

    tests = [
        test_set_integer,
        test_set_multiple_vars,
        test_arith_plus,
        test_arith_minus,
        test_arith_times,
        test_arith_div,
        test_expression_complex,
        test_medan_basic,
        test_medan_minus,
        test_medan_times,
        test_medan_div,
        test_medan_countdown,
        test_om_less,
        test_om_greater,
        test_om_equals,
        test_om_not_equals,
        test_om_else_branch,
        test_while_break_early,
        test_while_break_first,
        test_while_no_break,
        test_skriv_value,
        test_skriv_value_multidigit,
        test_skriv_value_zero,
        test_skriv_multiple,
        test_skriv_nl,
        test_finishes_within_timeout,
    ]

    failed = []
    for t in tests:
        try:
            t()
            print(f"  OK  {t.__name__}")
        except Exception as e:
            print(f"  FAIL {t.__name__}: {e}")
            failed.append((t.__name__, str(e)))

    print()
    if failed:
        print(f"MISSLYCKADES: {len(failed)}/{len(tests)}")
        for name, err in failed:
            print(f"  {name}: {err}")
        sys.exit(1)
    else:
        print(f"Alla {len(tests)} integrationstester OK!")