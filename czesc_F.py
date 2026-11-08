"""
Część F — więcej miar podobieństwa (textdistance).
Punkt wyjścia: example_18.py

Uruchomienie:  python czesc_F.py
"""
import textdistance as td

import wspolne as w

w.tee("czesc_F")

MIARY = {
    "Levenshtein": td.levenshtein,
    "Damerau-Lev.": td.damerau_levenshtein,
    "Jaro-Winkler": td.jaro_winkler,
    "Jaccard (bigramy)": td.Jaccard(qval=2),
}

PARY = [
    ("Ala ma kota", "Ala posiada kota"),     # para z zadania: podmiana słowa
    ("kot", "kto"),                          # przestawione litery
    ("tokenizacja", "tokenziacja"),          # literówka: przestawienie sąsiednich liter
    ("język", "jezyk"),                      # tylko diakrytyk
    ("Ala ma kota", "kota ma Ala"),          # te same słowa, inna kolejność
    ("kot", "pies"),                         # zupełnie różne
]

w.naglowek("Opis miar")
print("""Levenshtein        — minimalna liczba wstawień, usunięć i zamian pojedynczych znaków.
Damerau-Levenshtein — jak Levenshtein, ale dodatkowo przestawienie dwóch sąsiednich znaków
                      to JEDNA operacja (typowa literówka: 'kto' zamiast 'kot').
Jaro-Winkler       — podobieństwo 0..1: liczy znaki wspólne leżące blisko siebie i przestawienia,
                      a Winkler dodaje premię za zgodny początek napisu (przedrostek do 4 znaków).
Jaccard (bigramy)  — |A ∩ B| / |A ∪ B| dla ZBIORÓW bigramów znakowych; nie zależy od kolejności
                      bigramów w napisie, tylko od tego, które w ogóle występują.""")

w.naglowek("Odległości surowe (Levenshtein, Damerau-Levenshtein)")
w.tabela([(f"{a} / {b}", td.levenshtein(a, b), td.damerau_levenshtein(a, b)) for a, b in PARY],
         ["para", "Lev.", "Dam.-Lev."], [38, 8, 10])

w.naglowek("Podobieństwo znormalizowane 0..1 (1 = identyczne)")
wiersze, rozrzuty = [], []
for a, b in PARY:
    wart = [m.normalized_similarity(a, b) for m in MIARY.values()]
    wiersze.append((f"{a} / {b}", *[f"{v:.3f}" for v in wart], f"{max(wart) - min(wart):.3f}"))
    rozrzuty.append((max(wart) - min(wart), a, b, dict(zip(MIARY, wart))))
w.tabela(wiersze, ["para", *MIARY, "rozrzut"], [38, 14, 14, 14, 20, 10])

rozrzuty.sort(reverse=True)
r, a, b, wart = rozrzuty[0]
w.naglowek("Para, dla której miary różnią się najbardziej")
print(f"{a!r} / {b!r}: rozrzut {r:.3f}")
for n, v in wart.items():
    print(f"  {n:20} {v:.3f}")
print("""
Do sprawozdania wyjaśnij przyczynę na podstawie opisu miar (np. wrażliwość na kolejność znaków,
premia Jaro-Winklera za wspólny początek, ignorowanie kolejności przez Jaccarda).""")
