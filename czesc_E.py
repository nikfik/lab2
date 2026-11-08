"""
Część E — polszczyzna wymaga innych narzędzi (spaCy pl_core_news_sm).
Punkt wyjścia: example_08.py, example_09.py

Uruchomienie:  python czesc_E.py
Wymaga:        python -m spacy download pl_core_news_sm
Opcjonalnie:   pip install pystempel   (stemmer dla polskiego)
"""
import sys

from nltk.stem import SnowballStemmer

import wspolne as w

w.tee("czesc_E")

try:
    import spacy
    nlp = spacy.load("pl_core_news_sm")
except Exception as e:
    sys.exit(f"Brak spaCy lub modelu ({e}).\nZainstaluj: pip install spacy && python -m spacy download pl_core_news_sm")

surowy = w.wczytaj_pl()
start = surowy.find("Litwo! Ojczyzno moja")
fragment = " ".join(surowy[max(start, 0):max(start, 0) + 420].split())
print("Fragment:", fragment)

doc = nlp(fragment)

# ---- 1. tokenizacja i lematyzacja spaCy (+ opcjonalnie stemming Stempel)
stemmer_pl = None
try:
    from stempel import StempelStemmer
    stemmer_pl = StempelStemmer.default()
except Exception:
    print("\n(pystempel niedostępny — kolumna 'stem PL' będzie pusta; pip install pystempel)")

w.naglowek("1. Tokenizacja, lematyzacja (spaCy) i stemming (Stempel) — fragment polski")
wiersze = []
for t in doc:
    if t.is_punct or t.is_space:
        continue
    stem = (stemmer_pl.stem(t.text.lower()) if stemmer_pl else "—") or "—"
    wiersze.append((t.text, t.lemma_, t.pos_, stem))
w.tabela(wiersze, ["token", "lemat (spaCy)", "część mowy", "stem PL"], [18, 18, 12, 14])
print(f"\nliczba tokenów (bez interpunkcji): {len(wiersze)}")

# ---- 2. angielski stemmer na polskich słowach
snow_en = SnowballStemmer("english")
PL = ["kotami", "przetłumaczalny", "Ojczyzno", "zdrowie", "pięknością", "książkami", "biegałem", "łące"]
w.naglowek("2. Angielski stemmer (Snowball 'english') na polskich słowach")
lem_pl = {t.text.lower(): t.lemma_ for t in nlp(" ".join(PL))}
w.tabela([(s, snow_en.stem(s), lem_pl.get(s.lower(), "?")) for s in PL],
         ["słowo PL", "angielski stem", "lemat (spaCy)"], [18, 18, 16])
print("""
Skomentuj: angielski stemmer zna angielskie końcówki (-ing, -ed, -s, -ly ...). Polskie końcówki
(-ami, -ości, -ą, -ie ...) są mu obce, więc słowa zostają prawie nietknięte albo tracą przypadkową końcówkę;
formy tego samego wyrazu (np. 'kotami', 'kota') nie schodzą się do wspólnego rdzenia.""")

# ---- 3. języki Snowballa
w.naglowek("3. Języki obsługiwane przez SnowballStemmer")
print(", ".join(SnowballStemmer.languages))
print("\nczy jest polski?", "polish" in SnowballStemmer.languages)
print("""
Komentarz: polskiego brak. Polszczyzna ma bogatą fleksję (7 przypadków, rodzaje, liczby, aspekt, alternacje
w temacie typu 'ręka/ręce', 'pies/psa'), więc proste obcinanie końcówek za pomocą kilku reguł nie wystarcza —
potrzebny jest słownik fleksyjny albo model (spaCy, Morfeusz, Stempel uczony na parach forma–rdzeń).""")
