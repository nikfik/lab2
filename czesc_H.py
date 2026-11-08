"""
Część H — własny tokenizator podsłowowy (BPE, biblioteka tokenizers).
Punkt wyjścia: example_14.py, example_15.py

Uruchomienie:  python czesc_H.py
Wymaga:        pip install tokenizers transformers sentencepiece
Pobierane są tylko pliki tokenizatorów (gpt2, HerBERT, Bielik) — nie wagi modeli.
Powstają: tokenizer_pl.json (wariant 5000) oraz tokenizer_pl_1000.json i tokenizer_pl_30000.json.
"""
import csv
import statistics

import matplotlib.pyplot as plt
from tokenizers import Tokenizer, decoders, models, pre_tokenizers, trainers

import wspolne as w

w.tee("czesc_H")

KORPUS = w.pobierz("pl")
ROZMIARY = [1000, 5000, 30000]


def bytes_to_unicode():
    """Odwzorowanie bajt -> znak używane przez tokenizację ByteLevel (jak w GPT-2)."""
    bs = list(range(ord("!"), ord("~") + 1)) + list(range(ord("¡"), ord("¬") + 1)) + list(range(ord("®"), ord("ÿ") + 1))
    cs, n = bs[:], 0
    for b in range(256):
        if b not in bs:
            bs.append(b)
            cs.append(256 + n)
            n += 1
    return dict(zip(bs, map(chr, cs)))


ODWROTNE = {c: b for b, c in bytes_to_unicode().items()}


def czytelny(token):
    """Token ByteLevel (np. 'Ä\x99') zamieniamy z powrotem na tekst (np. 'ę') — tylko do wyświetlania."""
    try:
        return bytes(ODWROTNE[c] for c in token).decode("utf-8", errors="replace")
    except KeyError:
        return token


def trenuj(rozmiar):
    tok = Tokenizer(models.BPE(unk_token="[UNK]"))
    tok.pre_tokenizer = pre_tokenizers.ByteLevel(add_prefix_space=True)
    tok.decoder = decoders.ByteLevel()
    trainer = trainers.BpeTrainer(
        vocab_size=rozmiar, min_frequency=2,
        special_tokens=["[UNK]", "[CLS]", "[SEP]", "[PAD]", "[MASK]"],
        initial_alphabet=pre_tokenizers.ByteLevel.alphabet(),
        show_progress=False,
    )
    tok.train([str(KORPUS)], trainer)
    return tok


# ---- 1–2. uczenie trzech tokenizatorów
w.naglowek("1–2. Uczenie BPE dla trzech rozmiarów słownika")
tokenizery = {}
for r in ROZMIARY:
    tokenizery[r] = trenuj(r)
    plik = "tokenizer_pl.json" if r == 5000 else f"tokenizer_pl_{r}.json"
    tokenizery[r].save(str(w.KATALOG / plik))
    print(f"zamówiony rozmiar {r:6} -> faktyczny rozmiar słownika {tokenizery[r].get_vocab_size():6}  (zapisano {plik})")
print("""Uwaga: faktyczny rozmiar może być mniejszy od zamówionego — korpus jednej książki
(~450 kB) ma za mało powtarzających się par, by BPE wykonało tyle scaleń (min_frequency=2).""")

# ---- 3. podział czterech słów
SLOWA = ["nieprzetłumaczalny", "hiperparametryzacja", "kotkowi", "Mickiewicz"]
w.naglowek("3. Podział słów przez trzy tokenizatory")
wiersze = []
for s in SLOWA:
    wiersz = [s]
    for r in ROZMIARY:
        enc = tokenizery[r].encode(s)
        wiersz.append(f"{len(enc.tokens)}: " + " | ".join(czytelny(t) for t in enc.tokens))
    wiersze.append(wiersz)
w.tabela(wiersze, ["słowo", *[f"V={r}" for r in ROZMIARY]], [22, 48, 48, 48])
with open(w.WYNIKI / "H_podzial_slow.csv", "w", encoding="utf-8", newline="") as f:
    cw = csv.writer(f)
    cw.writerow(["slowo", *[f"V={r}" for r in ROZMIARY]])
    cw.writerows(wiersze)

# ---- 4–5. liczba tokenów dla zdań
PL = [
    "Przetwarzanie języka naturalnego to dziedzina sztucznej inteligencji.",
    "Litwo! Ojczyzno moja! ty jesteś jak zdrowie.",
    "Wczoraj wieczorem długo rozmawialiśmy o nieprzetłumaczalnych słowach.",
    "Studenci Politechniki Krakowskiej piszą sprawozdanie z laboratorium.",
    "Kotkowi spodobał się nowy, ciepły koc leżący pod oknem.",
]
EN = [
    "Natural language processing is a field of artificial intelligence.",
    "To be, or not to be, that is the question.",
    "Students at the university are writing a report about tokenization.",
    "Yesterday evening we talked for a long time about untranslatable words.",
    "The kitten liked the new warm blanket lying under the window.",
]

from transformers import AutoTokenizer  # noqa: E402

GOTOWE = {
    "gpt2": ["gpt2"],
    "herbert": ["allegro/herbert-base-cased"],
    "bielik": ["speakleash/Bielik-1.5B-v3", "speakleash/Bielik-1.5B-v3.0-Instruct"],
}
liczniki = {"własny (5000)": lambda t: len(tokenizery[5000].encode(t).tokens)}
for klucz, kandydaci in GOTOWE.items():
    for nazwa in kandydaci:
        try:
            tok = AutoTokenizer.from_pretrained(nazwa)
            liczniki[klucz] = (lambda tk: (lambda t: len(tk.tokenize(t))))(tok)
            print(f"załadowano tokenizator: {nazwa} (|V|={tok.vocab_size})")
            break
        except Exception as e:
            print(f"nie udało się załadować {nazwa}: {type(e).__name__}: {str(e)[:500]}")
    else:
        print(f"UWAGA: pomijam {klucz} — brak tokenizatora (sprawdź internet / nazwę repozytorium)")

w.naglowek("4–5. Liczba tokenów na zdanie")
wiersze_csv, srednie = [], {}
for jezyk, zdania in (("PL", PL), ("EN", EN)):
    for i, z in enumerate(zdania, 1):
        wiersze_csv.append([jezyk, i, z, len(z.split()), *[f(z) for f in liczniki.values()]])
w.tabela([[r[0], r[1], r[3], *r[4:]] for r in wiersze_csv],
         ["język", "zd.", "wyrazów", *liczniki], [8, 6, 10, *[16] * len(liczniki)])
with open(w.WYNIKI / "H_tokeny_zdania.csv", "w", encoding="utf-8", newline="") as f:
    cw = csv.writer(f)
    cw.writerow(["jezyk", "nr", "zdanie", "wyrazow", *liczniki])
    cw.writerows(wiersze_csv)

for jezyk in ("PL", "EN"):
    srednie[jezyk] = {n: statistics.mean(r[4 + k] for r in wiersze_csv if r[0] == jezyk)
                      for k, n in enumerate(liczniki)}
print("\nŚrednia liczba tokenów na zdanie:")
w.tabela([[n, f"{srednie['PL'][n]:.1f}", f"{srednie['EN'][n]:.1f}", f"{srednie['PL'][n] / srednie['EN'][n]:.2f}"]
          for n in liczniki], ["tokenizator", "PL", "EN", "PL/EN"], [18, 8, 8, 8])

fig, ax = plt.subplots(figsize=(8, 5))
szer, nazwy = 0.38, list(liczniki)
xs = range(len(nazwy))
b1 = ax.bar([x - szer / 2 for x in xs], [srednie["PL"][n] for n in nazwy], szer, label="polski", color="#c0504d")
b2 = ax.bar([x + szer / 2 for x in xs], [srednie["EN"][n] for n in nazwy], szer, label="angielski", color="#3b6ea8")
ax.bar_label(b1, fmt="%.1f", fontsize=9)
ax.bar_label(b2, fmt="%.1f", fontsize=9)
ax.set_xticks(list(xs), nazwy)
ax.set_ylabel("średnia liczba tokenów na zdanie")
ax.set_title("Koszt zdania w tokenach: polski vs angielski")
ax.legend()
fig.tight_layout()
fig.savefig(w.WYNIKI / "H_srednia_tokenow.png", dpi=150)
plt.close(fig)
print("[wykres zapisany: wyniki/H_srednia_tokenow.png]")

# ---- 6. dodatkowe liczby do odpowiedzi na pytania
w.naglowek("6. Liczby do odpowiedzi na pytania")
tekst_pl = KORPUS.read_text(encoding="utf-8-sig")
tekst_en = w.wczytaj_en()[:len(tekst_pl)]
print(f"a) liczba tokenów całego Pana Tadeusza ({len(tekst_pl.split())} wyrazów) vs rozmiar słownika:")
tok_pl = []
for r in ROZMIARY:
    n = len(tokenizery[r].encode(tekst_pl).tokens)
    tok_pl.append(n)
    print(f"   V={r:6} (faktycznie {tokenizery[r].get_vocab_size():6}): {n:7} tokenów, {n / len(tekst_pl.split()):.2f} tokenu/wyraz")
print("   -> czy zależność jest liniowa? (przy 6-krotnym wzroście V liczba tokenów spada o ułamek, nie 6 razy)")

print("\nb) ten sam tokenizator (5000) na tekście, na którym się uczył, i na obcym:")
slow_en = len(tekst_en.split())
for nazwa, t, n_slow in (("Pan Tadeusz (korpus uczący)", tekst_pl, len(tekst_pl.split())),
                         ("Hamlet po angielsku (obcy)", tekst_en, slow_en)):
    n = len(tokenizery[5000].encode(t).tokens)
    print(f"   {nazwa:30} {n / n_slow:.2f} tokenu/wyraz")

fig, ax = plt.subplots(figsize=(6, 4))
ax.plot([tokenizery[r].get_vocab_size() for r in ROZMIARY], tok_pl, "o-", color="#3b6ea8")
ax.set_xscale("log")
ax.set_xlabel("faktyczny rozmiar słownika (skala log.)")
ax.set_ylabel("liczba tokenów Pana Tadeusza")
ax.set_title("Liczba tokenów a rozmiar słownika")
fig.tight_layout()
fig.savefig(w.WYNIKI / "H_tokeny_vs_slownik.png", dpi=150)
plt.close(fig)
print("[wykres zapisany: wyniki/H_tokeny_vs_slownik.png]")
