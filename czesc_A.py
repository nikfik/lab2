"""
Część A — n-gramy w tekście polskim (Pan Tadeusz, Wolne Lektury).
Punkt wyjścia: example_16.py, example_17.py

Uruchomienie:  python czesc_A.py
"""
from collections import Counter

import wspolne as w

w.tee("czesc_A")

# 1. wczytanie książki
surowy = w.wczytaj_pl()
print(f"Wczytano tekst: {len(surowy)} znaków")

# 2. czyszczenie
czysty = w.oczysc(surowy)
(w.DANE / "pan_tadeusz_czysty.txt").write_text(czysty, encoding="utf-8")
print(f"Po oczyszczeniu: {len(czysty)} znaków (zapisano dane/pan_tadeusz_czysty.txt)")
print("Początek:", czysty[:150], "...")

# 3. tokenizacja zdaniowa i wyrazowa
lista_zdan = w.zdania(czysty, "polish")
slowa = w.wyrazy(czysty)
w.naglowek("3. Liczba zdań i wyrazów")
print(f"zdań:   {len(lista_zdan)}")
print(f"wyrazów (tokenów): {len(slowa)}")
print(f"wyrazów unikalnych: {len(set(slowa))}")
print(f"średnia długość zdania: {len(slowa) / len(lista_zdan):.1f} wyrazu")

# 4–5. n-gramy i częstości
uni = Counter(w.ngramy(slowa, 1))
bi = Counter(w.ngramy(slowa, 2))
tri = Counter(w.ngramy(slowa, 3))

w.naglowek("4–5. n-gramy i ich częstości")
for nazwa, c in (("unigramy", uni), ("bigramy", bi), ("trigramy", tri)):
    suma = sum(c.values())
    top10 = sum(v for _, v in c.most_common(10))
    hapax = sum(1 for v in c.values() if v == 1)
    print(f"{nazwa:9}: wszystkich {suma:6}, unikalnych {len(c):6}, "
          f"10 najczęstszych = {100 * top10 / suma:4.1f}% całości, "
          f"występujących raz: {100 * hapax / len(c):4.1f}% unikalnych")

for nazwa, c in (("unigramów", uni), ("bigramów", bi), ("trigramów", tri)):
    print(f"\n20 najczęstszych {nazwa}:")
    for g, v in c.most_common(20):
        print(f"  {v:5}  {' '.join(g)}")

# 6. histogramy
w.naglowek("6. Histogramy")
w.wykres_top(uni, "10 najczęstszych unigramów — Pan Tadeusz", "A_unigramy.png")
w.wykres_top(bi, "10 najczęstszych bigramów — Pan Tadeusz", "A_bigramy.png")
w.wykres_top(tri, "10 najczęstszych trigramów — Pan Tadeusz", "A_trigramy.png")

# 7. pytania — odpowiedzi uzupełnij po obejrzeniu wyników (patrz sprawozdanie)
print("""
7. Pytania do omówienia (odpowiedzi w sprawozdaniu, na podstawie powyższych liczb):
 - Jakie bigramy dominują?  -> sprawdź listę 20 najczęstszych bigramów: czy to same słowa funkcyjne?
 - Czy trigramy pokazują zwroty charakterystyczne dla autora?  -> patrz lista trigramów (powtarzalne formuły).
 - Jak różni się rozkład unigramów od bigramów?  -> porównaj udział 10 najczęstszych i odsetek n-gramów występujących raz.
""")
