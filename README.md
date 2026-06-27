<p align="center">
  <img src="logo.png" alt="Matcha Cocomelon Mod" width="420">
</p>

<h1 align="center">Mod do gry MECCHA CHAMELEON</h1>

<p align="center">Mod zmienia dźwięk gwizdu na „widzisz mnie?".</p>

---

Instalator jest **wieloplatformowy** — działa pod **Windows** i **Linux** (Steam / Steam Proton). Ma retro wygląd terminala w stylu testu pamięci (zielona ramka **OK**, czerwona **ERROR**).

## Instalacja

### 1. Pobranie i wypakowanie
Pobierz archiwum ZIP z sekcji **[Releases](../../releases/latest)**, a następnie wypakuj jego **całą zawartość** do jednego folderu (np. na pulpicie).

> **Ważne:** najpierw wypakuj całą zawartość archiwum. Obok instalatora musi znajdować się folder `mod`.

### 2. Uruchomienie instalatora

**Windows**
- Dwuklik na **`Zainstaluj.bat`** (wymaga zainstalowanego [Pythona 3](https://www.python.org/downloads/) — przy instalacji zaznacz *„Add Python to PATH"*), **albo**
- uruchom samodzielny **`Zainstaluj.exe`** (nie wymaga Pythona).

**Linux**
- W terminalu w folderze moda:
  ```bash
  ./zainstaluj.sh
  ```
  (lub `python3 installer.py`).

Następnie wybierz opcję **Zainstaluj** (`1`). Instalator sam wyszukuje grę w bibliotekach Steam; jeśli jej nie znajdzie, poprosi o wskazanie folderu.

### 3. Zakończenie
Po wyświetleniu zielonej ramki **„MOD ZAINSTALOWANY POMYSLNIE"** uruchom grę.

> **Wskazówka:** możesz pominąć menu, podając argument: `installer.py /install` lub `installer.py /uninstall`.

---

## Komunikat „System Windows ochronił komputer"
Komunikat może się pojawić, ponieważ plik nie jest podpisany cyfrowo. Aby kontynuować, wybierz **„Więcej informacji"**, a następnie **„Uruchom mimo to"**.

---

## Odinstalowanie
Uruchom instalator tak samo jak przy instalacji i wybierz opcję **Odinstaluj** (`2`). Mod zostanie usunięty, a gwizd wróci do oryginału.

---

## Najczęstsze problemy
| Problem | Rozwiązanie |
|---|---|
| Brak zmian w grze | Zamknij grę całkowicie i uruchom ponownie — mod ładuje się przy starcie. |
| Komunikat „Nie znalazłem plików moda" | Wypakuj całą zawartość archiwum do jednego folderu (folder `mod` musi znajdować się obok instalatora). |
| Komunikat „Nie znalazłem gry" | Gdy instalator o to poprosi, wpisz lub wklej ścieżkę do folderu gry. Lokalizację znajdziesz w aplikacji Steam: prawy przycisk myszy na grze → **Zarządzaj** → **Przeglądaj pliki lokalne**. |
| Mod przestał działać | Weryfikacja integralności plików gry w Steam usuwa mody. Zainstaluj mod ponownie. |

---

## Wymagania
- Gra **MECCHA CHAMELEON** na platformie Steam
- System **Windows 10/11** lub **Linux**
- **Python 3** (dla `Zainstaluj.bat` / `zainstaluj.sh`; w Windows alternatywnie samodzielny `Zainstaluj.exe`)

<sub>Nieoficjalny mod fanowski. Mod można odinstalować w dowolnym momencie.</sub>
