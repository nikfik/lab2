"""
wspolne.py — funkcje wspólne dla wszystkich części laboratorium nr 2.

Zawiera: pobieranie i wczytywanie tekstów, czyszczenie, tokenizację zdań i wyrazów,
n-gramy, wykresy oraz zapisywanie wyników (to, co skrypt drukuje, trafia też do
pliku wyniki/<nazwa>.txt — z tego korzystamy potem w sprawozdaniu).
"""

import re
import sys
import unicodedata
import urllib.request
from collections import Counter
from pathlib import Path

# Windows (cp1250) nie umie wypisać np. strzałek — wymuszamy UTF-8
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

import matplotlib

matplotlib.use("Agg")  # rysujemy do plików, bez okienek
import matplotlib.pyplot as plt

KATALOG = Path(__file__).resolve().parent
DANE = KATALOG / "dane"
WYNIKI = KATALOG / "wyniki"
DANE.mkdir(exist_ok=True)
WYNIKI.mkdir(exist_ok=True)

TEKSTY = {
    "pl": ("pan-tadeusz.txt", "https://wolnelektury.pl/media/book/txt/pan-tadeusz.txt"),
    "en": ("hamlet.txt", "https://www.gutenberg.org/cache/epub/27761/pg27761.txt"),
}

LITERY_PL_DUZE = "A-ZĄĆĘŁŃÓŚŹŻ"
LITERY_PL_MALE = "a-ząćęłńóśźż"


# ---------------------------------------------------------------- wyniki
class _Tee:
    def __init__(self, nazwa):
        self.plik = open(WYNIKI / f"{nazwa}.txt", "w", encoding="utf-8")
        self.konsola = sys.stdout

    def write(self, s):
        self.konsola.write(s)
        self.plik.write(s)

    def flush(self):
        self.konsola.flush()
        self.plik.flush()


def tee(nazwa):
    """Od teraz print() pisze i na ekran, i do wyniki/<nazwa>.txt."""
    sys.stdout = _Tee(nazwa)


def naglowek(tekst):
    print()
    print("=" * 70)
    print(tekst)
    print("=" * 70)


# ---------------------------------------------------------------- teksty
def pobierz(klucz):
    """Zwraca ścieżkę do pliku z tekstem; pobiera go, jeśli jeszcze go nie ma."""
    nazwa, url = TEKSTY[klucz]
    sciezka = DANE / nazwa
    if not sciezka.exists():
        print(f"pobieram {url} ...")
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (lab PJN)"})
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                sciezka.write_bytes(r.read())
        except Exception as e:
            sys.exit(f"Nie udało się pobrać ({e}).\n"
                     f"Pobierz ręcznie {url}\ni zapisz jako {sciezka}")
    return sciezka


def wczytaj_pl():
    """Pan Tadeusz z Wolnych Lektur, bez stopki z informacją o licencji."""
    t = pobierz("pl").read_text(encoding="utf-8-sig")
    t = t.replace("\r\n", "\n")
    return t.split("\n-----")[0].strip()


def wczytaj_en():
    """Tekst z Project Gutenberg bez nagłówka i stopki licencyjnej."""
    t = pobierz("en").read_text(encoding="utf-8-sig").replace("\r\n", "\n")
    m = re.search(r"\*\*\* ?START OF[^\n]*\n", t)
    if m:
        t = t[m.end():]
    m = re.search(r"\*\*\* ?END OF", t)
    if m:
        t = t[:m.start()]
    return t.strip()


# ---------------------------------------------------------------- NLTK
_ZASOBY = {
    "punkt_tab": "tokenizers/punkt_tab",
    "punkt": "tokenizers/punkt",
    "wordnet": "corpora/wordnet",
    "omw-1.4": "corpora/omw-1.4",
    "averaged_perceptron_tagger_eng": "taggers/averaged_perceptron_tagger_eng",
    "averaged_perceptron_tagger": "taggers/averaged_perceptron_tagger",
}


def nltk_dane(*nazwy):
    """Pobiera dane nltk tylko wtedy, gdy ich jeszcze nie ma (część może nie istnieć w danej wersji)."""
    import nltk
    for n in nazwy:
        try:
            nltk.data.find(_ZASOBY[n])
        except LookupError:
            try:
                nltk.download(n, quiet=True)
            except Exception:
                pass


# ---------------------------------------------------------------- czyszczenie / tokenizacja
def oczysc(tekst):
    """
    Czyszczenie: NFC, małe litery, usunięcie cyfr i znaków specjalnych, zwinięcie białych znaków.
    Zostawiamy tylko litery oraz . ! ? — dzięki temu da się jeszcze podzielić tekst na zdania.
    """
    t = unicodedata.normalize("NFC", tekst).lower()
    t = t.replace("…", ".")
    t = re.sub(r"[\d_]+", " ", t)                  # cyfry i podkreślenia
    t = re.sub(r"[^\w\s.!?]", " ", t)              # znaki specjalne i interpunkcja (poza .!?)
    t = re.sub(r"\s+", " ", t).strip()             # wielokrotne białe znaki
    return t


def zdania(tekst, jezyk="polish"):
    import nltk
    nltk_dane("punkt_tab", "punkt")
    return nltk.sent_tokenize(tekst, language=jezyk)


def wyrazy(tekst):
    """Wyrazy = ciągi liter (cyfry, podkreślenia i interpunkcja odpadają)."""
    return re.findall(r"[^\W\d_]+", tekst)


def ngramy(slowa, n):
    return list(zip(*[slowa[i:] for i in range(n)]))


# ---------------------------------------------------------------- wykresy
def wykres_top(licznik, tytul, plik, n=10):
    top = licznik.most_common(n)
    etykiety = [" ".join(g) if isinstance(g, tuple) else g for g, _ in top][::-1]
    wartosci = [c for _, c in top][::-1]
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.barh(etykiety, wartosci, color="#3b6ea8")
    for i, v in enumerate(wartosci):
        ax.text(v, i, f" {v}", va="center", fontsize=9)
    ax.set_title(tytul)
    ax.set_xlabel("liczba wystąpień")
    ax.margins(x=0.12)
    fig.tight_layout()
    fig.savefig(WYNIKI / plik, dpi=150)
    plt.close(fig)
    print(f"  [wykres zapisany: wyniki/{plik}]")


def tabela(wiersze, naglowki, szerokosci=None):
    """Prosta tabela tekstowa do wydruku."""
    if szerokosci is None:
        szerokosci = [max(len(str(x)) for x in [h] + [r[i] for r in wiersze]) + 2
                      for i, h in enumerate(naglowki)]
    fmt = "".join(f"{{:<{w}}}" for w in szerokosci)
    print(fmt.format(*naglowki))
    print("-" * sum(szerokosci))
    for r in wiersze:
        print(fmt.format(*[str(x) for x in r]))


__all__ = ["Counter"]
