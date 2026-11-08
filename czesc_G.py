"""
Część G — stop words i nazwy własne (Pan Tadeusz).

Uruchomienie:  python czesc_G.py
Wymaga:        pip install stop-words
"""
import re
from collections import Counter

from stop_words import get_stop_words

import wspolne as w

w.tee("czesc_G")

surowy = w.wczytaj_pl()
czysty = w.oczysc(surowy)
slowa = w.wyrazy(czysty)

# ---- 1. usunięcie stop words
stop = set(get_stop_words("polish"))
bez = [s for s in slowa if s not in stop]
w.naglowek("1. Usunięcie stop words")
print(f"lista stop words (biblioteka stop-words): {len(stop)} wyrazów, np. {sorted(stop)[:12]}")
print(f"wyrazów przed: {len(slowa)}, po: {len(bez)} (usunięto {100 * (1 - len(bez) / len(slowa)):.1f}%)")
print(f"unikalnych przed: {len(set(slowa))}, po: {len(set(bez))}")

# ---- 2. n-gramy po usunięciu stop words
w.naglowek("2. n-gramy po usunięciu stop words")
wyniki = {}
for n, nazwa in ((1, "unigramy"), (2, "bigramy"), (3, "trigramy")):
    z = Counter(w.ngramy(slowa, n))
    b = Counter(w.ngramy(bez, n))
    wyniki[n] = (z, b)
    print(f"\n{nazwa}: 15 najczęstszych BEZ stop words")
    for g, v in b.most_common(15):
        print(f"  {v:5}  {' '.join(g)}")
    w.wykres_top(b, f"10 najczęstszych: {nazwa} (bez stop words)", f"G_{nazwa}_bez_stopwords.png")

# ---- 3. porównanie wariantów
w.naglowek("3. Porównanie: z stop words i bez")
wiersze = []
for n, nazwa in ((1, "unigramy"), (2, "bigramy"), (3, "trigramy")):
    z, b = wyniki[n]
    top_z = {g for g, _ in z.most_common(10)}
    top_b = {g for g, _ in b.most_common(10)}
    wiersze.append((nazwa, sum(z.values()), len(z), sum(b.values()), len(b),
                    f"{100 * sum(v for _, v in z.most_common(10)) / sum(z.values()):.2f}%",
                    f"{100 * sum(v for _, v in b.most_common(10)) / sum(b.values()):.2f}%",
                    len(top_z & top_b)))
w.tabela(wiersze, ["n-gram", "razem (z)", "unikalne (z)", "razem (bez)", "unikalne (bez)",
                   "top10 udział (z)", "top10 udział (bez)", "wspólne w top10"],
         [10, 12, 14, 13, 16, 18, 19, 17])


# ---- 4. nazwy własne wyrażeniem regularnym
# Wielka litera w ŚRODKU zdania: poprzedza ją mała litera lub przecinek/średnik i spacja w tej samej linii.
#   - początek wersu / zdania (po . ! ? albo po znaku nowej linii) odpada, bo tam nie stoi [mała litera/,;] + spacja,
#   - nagłówki typu „KSIĘGA PIERWSZA” odpadają, bo po wielkiej literze musi być mała.
WZORZEC = re.compile(rf"(?<=[{w.LITERY_PL_MALE},;] )[{w.LITERY_PL_DUZE}][{w.LITERY_PL_MALE}]+")

tekst_linie = "\n".join(re.sub(r"[ \t]+", " ", linia) for linia in surowy.splitlines())
kandydaci = WZORZEC.findall(tekst_linie)
# odsiewamy zaimki i partykuły napisane wielką literą po przecinku (np. „Ty”, „Co”) — są na liście stop words
nazwy = [k for k in kandydaci if k.lower() not in stop and len(k) >= 3]

w.naglowek("4–5. Nazwy własne (wyrażenie regularne)")
print("wzorzec:", WZORZEC.pattern)
print(f"dopasowań: {len(kandydaci)}, po odsianiu stop words i słów krótszych niż 3 litery: {len(nazwy)}")
print(f"unikalnych nazw: {len(set(nazwy))}")
print("\n10 najczęściej występujących nazw własnych:")
licznik = Counter(nazwy)
for nazwa, v in licznik.most_common(10):
    print(f"  {v:5}  {nazwa}")
print("\nNastępne 15 (do oceny jakości wyniku):")
for nazwa, v in licznik.most_common(25)[10:]:
    print(f"  {v:5}  {nazwa}")
w.wykres_top(licznik, "10 najczęstszych nazw własnych — Pan Tadeusz", "G_nazwy_wlasne.png")

