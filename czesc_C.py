"""
Część C — odległość edycyjna: „Ala ma kota” vs „Ala posiada kota”.
Punkt wyjścia: example_18.py

Uruchomienie:  python czesc_C.py
"""
import textdistance

import wspolne as w

w.tee("czesc_C")

A, B = "Ala ma kota", "Ala posiada kota"


def macierz(a, b):
    D = [[0] * (len(b) + 1) for _ in range(len(a) + 1)]
    for i in range(len(a) + 1):
        D[i][0] = i
    for j in range(len(b) + 1):
        D[0][j] = j
    for i in range(1, len(a) + 1):
        for j in range(1, len(b) + 1):
            koszt = 0 if a[i - 1] == b[j - 1] else 1
            D[i][j] = min(D[i - 1][j] + 1, D[i][j - 1] + 1, D[i - 1][j - 1] + koszt)
    return D


def operacje(a, b, D):
    """Cofamy się po macierzy i zbieramy operacje prowadzące do minimalnego kosztu."""
    i, j, ops = len(a), len(b), []
    while i > 0 or j > 0:
        if i > 0 and j > 0 and D[i][j] == D[i - 1][j - 1] + (a[i - 1] != b[j - 1]):
            ops.append(("bez zmian" if a[i - 1] == b[j - 1] else "zamiana", a[i - 1], b[j - 1], i, j))
            i, j = i - 1, j - 1
        elif i > 0 and D[i][j] == D[i - 1][j] + 1:
            ops.append(("usunięcie", a[i - 1], "", i, j))
            i -= 1
        else:
            ops.append(("wstawienie", "", b[j - 1], i, j))
            j -= 1
    return ops[::-1]


w.naglowek(f"Odległość Levenshteina: {A!r} -> {B!r}")
print("textdistance.levenshtein:", textdistance.levenshtein(A, B))
print("textdistance (znormalizowana odległość):", round(textdistance.levenshtein.normalized_distance(A, B), 3))
print(f"długości: {len(A)} i {len(B)} znaków (spacje też są znakami)")

D = macierz(A, B)
print("\nwłasna implementacja (programowanie dynamiczne):", D[-1][-1],
      "<- zgodne z biblioteką" if D[-1][-1] == textdistance.levenshtein(A, B) else "<- NIEZGODNE!")

ops = operacje(A, B, D)
w.naglowek("Operacje edycyjne (bez „bez zmian”)")
liczniki = {}
for typ, x, y, i, j in ops:
    if typ != "bez zmian":
        print(f"  {typ:11} {x!r:>4} -> {y!r:<4}  (pozycja w A: {i}, w B: {j})")
        liczniki[typ] = liczniki.get(typ, 0) + 1
print("\nPodsumowanie:", liczniki, " razem =", sum(liczniki.values()))

w.naglowek("Dlaczego tak?")
print("""Wspólny początek „Ala ” i końcówka „ kota” zostają bez zmian. Różni się tylko środek:
„ma” (2 znaki) kontra „posiada” (7 znaków). Żeby z „ma” zrobić „posiada”, trzeba:
  - dodać 7 - 2 = 5 znaków (wstawienia), bo „posiada” jest o 5 znaków dłuższe,
  - dopasować „ma” do „posiada”: wspólna jest tylko litera „a” (litery „m” w „posiada” nie ma),
    więc „m” nie ma z czym się zgodzić i musi zostać zamienione na inny znak (1 zamiana).
Stąd 5 wstawień + 1 zamiana = 6. Mniej się nie da: długości różnią się o 5, a najdłuższy
wspólny podciąg środka ma tylko jeden znak („a”), więc co najmniej jedna litera musi się zmienić.
""")

w.naglowek("Macierz programowania dynamicznego (wiersze: A, kolumny: B)")
print("      ∅ " + " ".join(f"{c:>2}" for c in B))
for i, wiersz in enumerate(D):
    et = "∅" if i == 0 else A[i - 1]
    print(f"  {et:>2}  " + " ".join(f"{v:>2}" for v in wiersz))
