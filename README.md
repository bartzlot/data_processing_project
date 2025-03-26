# data_processing_project

# Analiza komentarzy z YouTube – Pobieranie i analiza sentymentu

## Opis projektu

Ten projekt umożliwia:
- Pobranie komentarzy z filmów YouTube na podstawie linków.
- Przeprowadzenie analizy sentymentu komentarzy przy użyciu modelu BERT (`nlptown/bert-base-multilingual-uncased-sentiment`).
- Zapisanie wyników do plików `.csv` lub `.json` z dodatkowymi metadanymi (ilość słów, znaki, lajki itp.).

---

## Wymagania systemowe

- Python 3.8+
- Połączenie z internetem
- YouTube Data API v3 (klucz API)

---

## Instalacja

1. Sklonuj repozytorium

2. Utwórz środowisko wirtualne i zainstaluj zależności:

```
python -m venv venv
source venv/bin/activate      # lub venv\Scripts\activate na Windows
pip install -r requirements.txt
```
---

## Moduł: yt_comments.py

### Klasa: `YouTubeCommentsFetcher`

- `fetch_comments(video_id: str, max_results: int = 10) -> list`  
  Pobiera komentarze dla danego ID filmu.

- `save_comments_to_json(comments: list, id: int)`  
  Zapisuje komentarze do pliku JSON.

- `strip_emojis(text: str) -> str`  
  Usuwa emoji z komentarza.

- `extract_video_id(video_url: str) -> str`  
  Wyciąga identyfikator wideo z URL.

### Funkcja pomocnicza:

- `read_links_from_file(file_path: str) -> list`  
  Wczytuje linki z pliku tekstowego.

---

## Moduł: yt_comments_analyzer.py

### Klasa: `CommentsAnalyzer`

- `analyze_comments(file_name: str)`  
  Otwiera plik JSON z komentarzami i analizuje je.

- `get_batch_sentiments(comments: list) -> list`  
  Analiza sentymentu przy użyciu modelu `nlptown/bert-base-multilingual-uncased-sentiment`.

- `save_to_csv(analyzed_data, csv_path)`  
  Zapisuje dane do pliku CSV.

### Oceniane sentymenty:

- 1: Very Negative  
- 2: Negative  
- 3: Neutral  
- 4: Positive  
- 5: Very Positive

## Czym jest analiza sentymentu?

**Sentyment** to inaczej emocjonalny ton wypowiedzi. Gdy ktoś pisze komentarz, to z samej treści często można wyczytać, czy jego intencje były:

- pozytywne (pochwała, entuzjazm, radość),
- negatywne (krytyka, frustracja, niezadowolenie),
- neutralne (fakty, bez emocji).

**Analiza sentymentu (sentiment analysis)** to proces automatycznego oceniania tych emocji w tekście, bez potrzeby czytania komentarzy przez człowieka.

---

## Jak działa analiza sentymentu w tym programie?

Program korzysta z gotowego modelu językowego:  
**`nlptown/bert-base-multilingual-uncased-sentiment`**, który został wytrenowany na dużej liczbie opinii użytkowników (np. recenzji produktów, usług, itd.) w różnych językach – w tym także po polsku.

### Model BERT

Model, z którego korzysta program, to wariant BERT-a (Bidirectional Encoder Representations from Transformers). BERT to nowoczesna architektura w dziedzinie **uczenia maszynowego (NLP)**, która potrafi zrozumieć znaczenie słów w kontekście całego zdania.

W uproszczeniu:

- Model „czyta” tekst komentarza,
- Analizuje, jakie słowa i frazy się tam pojawiają,
- Na tej podstawie ocenia ogólny **ton wypowiedzi**,
- Zwraca ocenę w skali **od 1 do 5** gwiazdek (gdzie 1 = bardzo negatywny, 5 = bardzo pozytywny).

---

## Jakie są możliwe wyniki?

W programie każda liczba (od 1 do 5) zamieniana jest na etykietę tekstową:

| Ocena | Etykieta           | Znaczenie                           |
|-------|--------------------|--------------------------------------|
|   1   | Very Negative      | Bardzo negatywny komentarz           |
|   2   | Negative           | Negatywny komentarz                  |
|   3   | Neutral            | Bez emocji, neutralna wypowiedź      |
|   4   | Positive           | Pozytywny komentarz                  |
|   5   | Very Positive      | Bardzo pozytywny, entuzjastyczny     |

Przykłady:

- **"Ten film był tragiczny."** → *Very Negative*
- **"Mogło być lepiej."** → *Negative*
- **"To jest film."** → *Neutral*
- **"Super, polecam każdemu!"** → *Very Positive*

---

## Czy model zawsze ma rację?

Nie zawsze – to nadal tylko maszyna. Model analizuje tekst na podstawie tego, czego się nauczył. Czasem może:

- pomylić się, jeśli komentarz jest sarkastyczny (np. "No świetnie, kolejny zmarnowany wieczór.")
- nie zrozumieć kontekstu kulturowego lub lokalnych wyrażeń
- dawać mniej trafne wyniki dla bardzo krótkich lub jednoznacznych komentarzy (np. "XD", "meh")

Dlatego analiza sentymentu jest bardzo przydatna do ogólnego przeglądu nastroju, ale nie zastępuje dokładnej, ludzkiej interpretacji w 100%.

---

## Po co robić analizę sentymentu?

Dzięki niej możesz:

- zrozumieć, jak widzowie reagują na dany film
- śledzić zmiany nastroju społeczności
- porównywać różne filmy lub kanały
- wyłapywać negatywne komentarze automatycznie
- wspierać działania marketingowe lub badawcze

To sposób na uporządkowanie dużej ilości tekstu i wyciągnięcie z niego konkretnej informacji – bez konieczności ręcznego czytania setek komentarzy.

## Jak działa model BERT?

Model używany w tym programie to specjalna wersja BERT-a – jednego z najpotężniejszych modeli językowych ostatnich lat. Ale co właściwie się dzieje, kiedy podajemy mu tekst komentarza?

### 1. Tokenizacja

Na początku tekst komentarza (np. *"Bardzo fajny film!"*) musi zostać przekształcony na formę, którą model „rozumie”. To się nazywa **tokenizacja**.

Tokenizacja polega na rozbiciu tekstu na mniejsze fragmenty, tzw. **tokeny**. Są to słowa, części słów, znaki interpunkcyjne itd. Model nie operuje na słowach tak jak człowiek, tylko właśnie na tokenach zakodowanych jako liczby.

Przykład:


(Liczby to ID tokenów w słowniku modelu)

---

### 2. Embeddingi

Każdy token zostaje zamieniony na tzw. **wektor liczbowy** – czyli zestaw kilkudziesięciu lub kilkuset liczb, które opisują „znaczenie” tego słowa.

Dzięki temu model może „zrozumieć”, że np. słowa *dobry* i *świetny* mają podobne znaczenie, a *tragiczny* – odwrotne.

---

### 3. Mechanizm Attention (uwagi)

To najważniejsza część BERT-a. Model nie czyta tekstu od początku do końca, tylko **patrzy na cały kontekst naraz** i „zastanawia się”, które słowa są dla niego ważne w danym momencie.

Przykład:
W zdaniu „Nie podobał mi się ten film” – ważne jest słowo „nie”, które zmienia znaczenie „podobał się”. Model BERT jest w stanie to zauważyć, bo analizuje relacje między wszystkimi słowami równocześnie.

To działa dzięki tzw. **self-attention** – mechanizmowi, który przypisuje wagę każdemu słowu w zależności od jego kontekstu.

---

### 4. Warstwy transformera

BERT składa się z wielu warstw przetwarzania. Każda z nich analizuje tekst trochę głębiej. Na początku rozpoznawane są proste relacje między słowami, ale im dalej w sieć, tym bardziej model „rozumie” ogólny sens wypowiedzi.

Można to porównać do czytania:

- Najpierw zauważasz słowa
- potem rozumiesz zdania
- na końcu łapiesz cały sens wypowiedzi

---

### 5. Klasyfikacja sentymentu

Na końcu – po przejściu przez wszystkie warstwy – model wybiera jedną z pięciu klas.
To się odbywa przez tzw. **warstwę wyjściową (output layer)**, która działa podobnie jak „głosowanie” – model przypisuje każdej klasie pewne prawdopodobieństwo i wybiera tę, która ma najwyższy wynik.

---

BERT jest lepszy niż starsze podejścia (np. na podstawie słów kluczowych), ponieważ:

- rozumie kontekst (np. „nie lubię” ≠ „lubię”),
- działa w wielu językach,
- potrafi działać nawet na krótkich zdaniach czy fragmentach

To dlatego został użyty w tym programie – aby zapewnić jak najlepszą jakość analizy.

