# Lab 2 — PJN: od tekstu do tokenów

## Instalacja (Windows, PowerShell)

```powershell
cd "...\PJN lab2\lab2"
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python -m spacy download pl_core_news_sm
```

## Uruchamianie

Teksty (`dane/pan-tadeusz.txt`, `dane/hamlet.txt`) pobierają się automatycznie przy pierwszym uruchomieniu.
Skrypty są niezależne, z jednym wyjątkiem: `czesc_I.py` potrzebuje `tokenizer_pl.json` z `czesc_H.py`

```powershell
python czesc_A.py   # n-gramy PL, histogramy                      (3.0)
python czesc_B.py   # token -> rdzeń -> lemat, EN                 (3.0)
python czesc_C.py   # Levenshtein: Ala ma kota / Ala posiada kota (3.0)
python czesc_D.py   # Porter vs Lancaster                         (4.0)
python czesc_E.py   # polski: spaCy, angielski stemmer na PL      (4.0)
python czesc_F.py   # Damerau, Jaro-Winkler, Jaccard              (4.0)
python czesc_G.py   # stop words, nazwy własne (regex)            (5.0)
python czesc_H.py   # własny BPE (1000/5000/30000) + porównanie   (5.0)
python czesc_I.py   # tabela porównawcza                          (5.0)
```

Wyniki (tekst, wykresy PNG, CSV) trafiają do `wyniki/`. Wytrenowany tokenizator: `tokenizer_pl.json`

