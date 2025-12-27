# Meraki CLI

Prosty, ale kompletny **CLI w Pythonie** do pracy z Cisco Meraki Dashboard API.  
Aplikacja pozwala na:

- weryfikację połączenia z API,
- wylistowanie sieci w organizacji,
- podgląd klientów w konkretnej sieci,
- inwentaryzację urządzeń (AP / MX / MS),
- zainicjowanie restartu Access Pointa po numerze seryjnym,
- pracę w różnych środowiskach: lokalnie (venv), w testach (pytest + mocki) oraz w kontenerze Docker.

Projekt przygotowany pod **Windows 11 + Visual Studio 2022** (lub nowsze), ale działa na dowolnym systemie z Pythonem 3.11+.

---

## 🛠 Technologie

- **Python 3.11+**
- [Typer](https://typer.tiangolo.com/) – budowa interfejsu CLI
- [Cisco Meraki Dashboard API Python Library](https://pypi.org/project/meraki/)
- [Rich](https://rich.readthedocs.io/) – kolorowe tabele i komunikaty w terminalu
- [pytest](https://docs.pytest.org/) – testy jednostkowe
- `unittest.mock` – mockowanie `meraki.DashboardAPI`
- [Docker](https://www.docker.com/) + `docker-compose` – konteneryzacja aplikacji

---

## 📂 Struktura projektu

Główne pliki w katalogu projektu:

```text
MerakiCli/
├── meraki_cli.py       # Główny plik aplikacji (Typer)
├── requirements.txt    # Zależności Pythona
├── Dockerfile          # Definicja obrazu Dockera
├── docker-compose.yml  # Konfiguracja uruchamiania w kontenerze
└── tests/
    └── test_cli.py     # Testy jednostkowe (pytest)
```

> **Uwaga:** Wszystkie komendy w instrukcji zakładają, że znajdujesz się w katalogu, w którym jest plik `meraki_cli.py`.

---

## ⚙️ Wymagania wstępne

- System operacyjny: Windows 10/11, Linux lub macOS.
- Zainstalowany **Python 3.11+** (z opcją *"Add Python to PATH"*).
- (Opcjonalnie) **Docker Desktop** – do uruchamiania w kontenerach.

---

## 🚀 Instalacja (lokalnie – venv)

### 1. Przygotowanie środowiska

W terminalu (PowerShell/Bash) przejdź do katalogu projektu i utwórz wirtualne środowisko:

```powershell
# Tworzenie venv
python -m venv venv

# Aktywacja venv (Windows)
.\venv\Scripts\activate

# Aktywacja venv (Linux/macOS)
# source venv/bin/activate
```

Po aktywacji powinieneś widzieć `(venv)` przed znakiem zachęty.

### 2. Instalacja zależności

```powershell
pip install --upgrade pip
pip install -r requirements.txt
```

---

## 🔑 Konfiguracja – Klucz API

CLI wymaga zmiennej środowiskowej `MERAKI_DASHBOARD_API_KEY`.

### Metoda A: Plik `.env` (Zalecane)
Utwórz plik `.env` w katalogu z `meraki_cli.py`:

```text
MERAKI_DASHBOARD_API_KEY=TWOJ_PRAWDZIWY_KLUCZ_API
```
Aplikacja automatycznie załaduje klucz dzięki bibliotece `python-dotenv`.

### Metoda B: Zmienna w terminalu (Tylko bieżąca sesja)

```powershell
$env:MERAKI_DASHBOARD_API_KEY="TWOJ_PRAWDZIWY_KLUCZ_API"
```

---

## 💻 Komendy CLI

Aplikacja oparta jest o **Typer**. Główna składnia:
`python meraki_cli.py [KOMENDA] [ARGUMENTY]`

Aby zobaczyć pomoc: `python meraki_cli.py --help`

### 1. `hello` – Test połączenia
Sprawdza poprawność klucza i połączenia z chmurą Meraki.

```powershell
python meraki_cli.py hello
```

### 2. `list-networks` – Lista sieci
Pobiera organizację i wyświetla dostępne w niej sieci. Zanotuj **ID sieci** (np. `L_6468...`), będzie potrzebne w kolejnych krokach.

```powershell
python meraki_cli.py list-networks
```

### 3. `list-clients` – Klienci w sieci
Wyświetla listę klientów podłączonych do danej sieci.

```powershell
# Składnia: python meraki_cli.py list-clients <NETWORK_ID>
python meraki_cli.py list-clients L_646829496481105433
```

### 4. `list-devices` – Urządzenia w sieci
Wyświetla urządzenia (AP, Switch, Gateway) w sieci. Użyj tej komendy, aby znaleźć **numer seryjny** (Serial) urządzenia do restartu.

```powershell
python meraki_cli.py list-devices L_646829496481105433
```

### 5. `restart-ap` – Restart Access Pointa
Wymusza restart urządzenia o podanym numerze seryjnym.

```powershell
# Składnia: python meraki_cli.py restart-ap <SERIAL>
python meraki_cli.py restart-ap Q2MD-BHHS-5FDL
```

> **Ważne (Meraki Sandbox):** > Jeśli korzystasz z publicznego *Meraki Always-On Sandbox*, operacja ta zwróci błąd `403 Forbidden`. Jest to zachowanie oczekiwane – sandbox ma uprawnienia "Read Only". Kod CLI obsłuży ten błąd i wyświetli stosowny komunikat.

---

## 🧪 Testy (pytest)

Projekt posiada testy jednostkowe, które **nie wykonują** prawdziwych połączeń do API (wszystkie wywołania są mockowane).

Aby uruchomić testy:
```powershell
python -m pytest -q
```
Oczekiwany wynik: `Passed`.

---

## 🐳 Docker

Możesz uruchomić aplikację w izolowanym środowisku bez instalowania Pythona na hoście.

### Dockerfile (Budowanie obrazu)

```powershell
docker build -t meraki-cli .
```

Przykładowe uruchomienie (z przekazaniem klucza API):

```powershell
docker run --rm -e MERAKI_DASHBOARD_API_KEY=$env:MERAKI_DASHBOARD_API_KEY meraki-cli list-networks
```

### Docker Compose (Wygodniejsze użycie)

Plik `docker-compose.yml` automatyzuje przekazywanie zmiennych.

1. Ustaw zmienną na hoście: `$env:MERAKI_DASHBOARD_API_KEY="..."`
2. Uruchom wybraną komendę:

```powershell
# Lista sieci
docker-compose run --rm meraki-cli list-networks

# Restart AP
docker-compose run --rm meraki-cli restart-ap Q2MD-BHHS-5FDL
```

---

## 📝 Podsumowanie

Projekt demonstruje:
1. **Integrację API**: Obsługa Meraki SDK w Pythonie.
2. **Bezpieczeństwo**: Obsługa kluczy przez zmienne środowiskowe/pliki `.env`.
3. **UX**: Nowoczesny interfejs CLI z kolorowymi tabelami.
4. **Jakość**: Testy jednostkowe z mockowaniem.
5. **Wdrożenie**: Gotowość do pracy w kontenerach Docker.
