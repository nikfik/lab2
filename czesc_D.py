"""
Część D — porównanie stemmerów (Porter vs Lancaster) na tekście angielskim.
Punkt wyjścia: example_08.py

Uruchomienie:  python czesc_D.py
"""
from collections import Counter, defaultdict

from nltk.stem import LancasterStemmer, PorterStemmer, WordNetLemmatizer

import wspolne as w

w.tee("czesc_D")
w.nltk_dane("wordnet", "omw-1.4")

tekst = w.oczysc(w.wczytaj_en())
slowa = w.wyrazy(tekst)
czest = Counter(slowa)
# pomijamy słowa bardzo rzadkie, żeby przykłady były czytelne
slownik = [s for s, c in czest.most_common() if c >= 3 and len(s) > 2]
print(f"tokenów: {len(slowa)}, słów unikalnych: {len(czest)}, użytych do porównania (min. 3 wystąpienia): {len(slownik)}")

porter, lancaster = PorterStemmer(), LancasterStemmer()
lem = WordNetLemmatizer()

# ---- 2. słowa z różnymi rdzeniami
roznice = [(s, porter.stem(s), lancaster.stem(s)) for s in slownik
           if porter.stem(s) != lancaster.stem(s)]
w.naglowek("2. Słowa, dla których Porter i Lancaster dają różne rdzenie")
print(f"{len(roznice)} z {len(slownik)} słów ({100 * len(roznice) / len(slownik):.0f}%). 25 najczęstszych:")
w.tabela([(s, p, l, czest[s]) for s, p, l in roznice[:25]],
         ["słowo", "Porter", "Lancaster", "częstość"], [16, 14, 14, 10])
print("\nSkomentuj w sprawozdaniu: Lancaster jest agresywniejszy (krótsze rdzenie), Porter ostrożniejszy.")


# ---- 3. nadmierne i niedostateczne obcinanie
def lematy(s):
    return {lem.lemmatize(s, p) for p in "nvar"}


def lemat_kanon(s):
    v = lem.lemmatize(s, "v")
    return v if v != s else lem.lemmatize(s, "n")


for nazwa, stemmer in (("Porter", porter), ("Lancaster", lancaster)):
    # nadmierne: różne wyrazy (rozłączne zbiory lematów) mają ten sam rdzeń
    grupy = defaultdict(list)
    for s in slownik:
        grupy[stemmer.stem(s)].append(s)
    nad = []
    for rdzen, lista in grupy.items():
        wyr = []
        for s in lista:
            if all(lematy(s).isdisjoint(lematy(t)) for t in wyr):
                wyr.append(s)
        if len(wyr) >= 2:
            nad.append((rdzen, wyr, sum(czest[s] for s in wyr)))
    nad.sort(key=lambda x: -x[2])
    w.naglowek(f"3a. NADMIERNE obcinanie — {nazwa}: różne wyrazy, ten sam rdzeń")
    print(f"znaleziono {len(nad)} takich rdzeni; najczęstsze:")
    for rdzen, wyr, _ in nad[:10]:
        print(f"  rdzeń {rdzen!r:10} <- {', '.join(wyr[:6])}")

    # niedostateczne: ten sam lemat, ale różne rdzenie
    po_lemacie = defaultdict(set)
    for s in slownik:
        po_lemacie[lemat_kanon(s)].add(s)
    nied = []
    for lemat, ws in po_lemacie.items():
        rdzenie = {stemmer.stem(s) for s in ws}
        if len(rdzenie) >= 2:
            nied.append((lemat, sorted(ws), sorted(rdzenie), sum(czest[s] for s in ws)))
    nied.sort(key=lambda x: -x[3])
    w.naglowek(f"3b. NIEDOSTATECZNE obcinanie — {nazwa}: ten sam lemat, różne rdzenie")
    print(f"znaleziono {len(nied)} lematów; najczęstsze:")
    for lemat, ws, rdzenie, _ in nied[:10]:
        print(f"  lemat {lemat!r:10} formy: {', '.join(ws[:6]):40} rdzenie: {', '.join(rdzenie)}")
