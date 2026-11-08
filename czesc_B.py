"""
Część B — sprowadzanie form w tekście angielskim (Hamlet, Project Gutenberg).
Punkt wyjścia: example_08.py, example_09.py

Uruchomienie:  python czesc_B.py
"""
import random
import re

import nltk
from nltk.stem import PorterStemmer, WordNetLemmatizer

import wspolne as w

w.tee("czesc_B")
w.nltk_dane("punkt_tab", "punkt", "wordnet", "omw-1.4",
            "averaged_perceptron_tagger_eng", "averaged_perceptron_tagger")

tekst = w.wczytaj_en()
print(f"Wczytano tekst angielski: {len(tekst)} znaków")
print("Początek:", tekst[:80].replace("\n", " "), "...")

# 2. wybór 5 zdań: pomijamy początek (spis treści), bierzemy zdania średniej długości
wszystkie = nltk.sent_tokenize(re.sub(r"\s+", " ", tekst), language="english")
kandydaci = [s for s in wszystkie[300:]
             if 8 <= len(s.split()) <= 18 and not s.isupper()
             and not re.search(r"[\[\]_()]|--|\bEnter\b|\bExit\b|\bExeunt\b", s)   # bez didaskaliów i przypisów
             and s[0].isupper() and s.rstrip()[-1] in ".?!"]
random.seed(2)
zdania = random.sample(kandydaci, 5)

w.naglowek("2. Wybrane zdania (seed=2, więc wynik jest powtarzalny)")
for i, s in enumerate(zdania, 1):
    print(f"{i}. {s}")

# 3. tokenizacja, stemming (Porter), lematyzacja (WordNet + część mowy)
porter = PorterStemmer()
lem = WordNetLemmatizer()
POS = {"J": "a", "V": "v", "N": "n", "R": "r"}  # tag Penn Treebank -> tag WordNet

wiersze = []
for s in zdania:
    tokeny = [t for t in nltk.word_tokenize(s) if t.isalpha()]
    for token, tag in nltk.pos_tag(tokeny):
        pos = POS.get(tag[0], "n")
        rdzen = porter.stem(token)
        lemat = lem.lemmatize(token.lower(), pos=pos)
        wiersze.append((token, tag, rdzen, lemat))

w.naglowek("4. Tabela: token -> rdzeń (Porter) -> lemat (WordNet)")
w.tabela(wiersze, ["token", "POS", "rdzeń", "lemat"], [16, 8, 16, 16])

# różnice stemming vs lematyzacja (porównujemy z małą literą)
inne = [(t, r, l) for t, _, r, l in wiersze if r != l.lower()]
unikalne = list(dict.fromkeys(inne))
w.naglowek("Słowa, dla których rdzeń różni się od lematu")
print(f"{len(unikalne)} unikalnych słów z {len(wiersze)} tokenów; przykłady:")
w.tabela(unikalne[:15], ["token", "rdzeń", "lemat"], [16, 16, 16])
print("\nUwaga do sprawozdania: wybierz z powyższej listy co najmniej trzy słowa i opisz,")
print("dlaczego wyniki się różnią (np. rdzeń nie musi być słowem, a lemat jest słowem ze słownika).")
