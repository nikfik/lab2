"""
Część I — porównanie wszystkich metod na tym samym fragmencie polskiego tekstu.

Uruchomienie:  python czesc_I.py      (najpierw uruchom czesc_H.py — potrzebny tokenizer_pl.json)
Wymaga:        pip install spacy stop-words tokenizers + model pl_core_news_sm
"""
import csv
import sys

from stop_words import get_stop_words
from tokenizers import Tokenizer

import wspolne as w

w.tee("czesc_I")

sciezka_tok = w.KATALOG / "tokenizer_pl.json"
if not sciezka_tok.exists():
    sys.exit("Brak tokenizer_pl.json — uruchom najpierw: python czesc_H.py")
tok = Tokenizer.from_file(str(sciezka_tok))

try:
    import spacy
    nlp = spacy.load("pl_core_news_sm", disable=["parser", "ner"])
except Exception as e:
    sys.exit(f"Brak spaCy lub modelu ({e}). python -m spacy download pl_core_news_sm")

surowy = w.wczytaj_pl()
start = surowy.find("Litwo! Ojczyzno moja")
if start < 0:
    sys.exit("Nie znaleziono początku Inwokacji w tekście.")
fragment = " ".join(surowy[start:start + 20000].split())   # białe znaki zwinięte (bez tokenów nowej linii)
print(f"fragment: {len(fragment)} znaków (od 'Litwo! Ojczyzno moja!')")

stop = set(get_stop_words("polish"))

# 1) same wyrazy
wyrazy = w.wyrazy(w.oczysc(fragment))
# 2) wyrazy po lematyzacji (spaCy; lematyzujemy tekst z zachowaniem wielkich liter i interpunkcji)
doc = nlp(fragment)
lematy = [t.lemma_.lower() for t in doc if t.is_alpha]
# 3) wyrazy bez stop words
bez_stop = [s for s in wyrazy if s not in stop]
# 4) tokeny podsłowowe z naszego tokenizatora (wariant 5000)
podslowa = tok.encode(fragment).tokens

warianty = [
    ("same wyrazy", wyrazy),
    ("lematy (spaCy)", lematy),
    ("bez stop words", bez_stop),
    ("tokeny BPE (V=5000)", podslowa),
]

w.naglowek("1–2. Liczba jednostek i rozmiar słownika")
baza_j, baza_v = len(wyrazy), len(set(wyrazy))
wiersze = []
for nazwa, jedn in warianty:
    n, v = len(jedn), len(set(jedn))
    wiersze.append((nazwa, n, v, f"{100 * n / baza_j:.0f}%", f"{100 * v / baza_v:.0f}%", f"{n / v:.1f}"))
w.tabela(wiersze, ["wariant", "jednostek", "słownik (unikalne)", "jednostek vs wyrazy", "słownik vs wyrazy", "średnie użycie"],
         [24, 12, 20, 22, 20, 16])

w.naglowek("Próbka: pierwsze 12 jednostek każdego wariantu")
for nazwa, jedn in warianty:
    probka = jedn[:12] if nazwa != "tokeny BPE (V=5000)" else [t.replace("Ġ", "▁") for t in jedn[:16]]
    print(f"{nazwa:22} {probka}")

with open(w.WYNIKI / "I_porownanie.csv", "w", encoding="utf-8", newline="") as f:
    cw = csv.writer(f)
    cw.writerow(["wariant", "jednostek", "slownik"])
    for nazwa, jedn in warianty:
        cw.writerow([nazwa, len(jedn), len(set(jedn))])


