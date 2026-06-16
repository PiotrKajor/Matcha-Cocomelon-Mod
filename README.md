<p align="center">
  <img src="logo.png" alt="Match Cocomelon Mod" width="420">
</p>

# 🎺 widzisz mnie? — mod do MECCHA CHAMELEON

Mały mod do gry **MECCHA CHAMELEON** (Steam), który **zmienia dźwięk gwizdu** na *„widzisz mnie?"*.

Działa jako mod IoStore `_P` — nadpisuje tylko ten jeden dźwięk, reszta gry zostaje bez zmian. Plug-and-play, bez ruszania plików bazowych gry.

---

## ⬇️ Instalacja (łatwa)

1. Pobierz najnowszy **[Release](../../releases/latest)** i rozpakuj **cały** ZIP do jednego folderu (obok `Zainstaluj.exe` musi zostać folder `mod`).
2. Uruchom **`Zainstaluj.exe`** → **Zainstaluj**.
3. Program sam znajdzie grę przez Steam i wgra mod. Po komunikacie *„ZAINSTALOWANY POMYSLNIE"* uruchom grę.

> 💡 Jeśli gra była włączona — **zamknij ją i odpal od nowa** (mod montuje się przy starcie).

> ⚠️ **Windows SmartScreen:** plik `.exe` nie jest podpisany cyfrowo, więc przy pierwszym uruchomieniu Windows może pokazać „System Windows ochronił komputer" → *Więcej informacji* → *Uruchom mimo to*. To normalne dla małych, własnych narzędzi.

### Instalacja ręczna (gdyby exe był blokowany)
Skopiuj pliki z folderu **`mod/`** (`*_P.utoc`, `*_P.ucas`, `*_P.pak`) do folderu gry:
```
...\steamapps\common\MECCHA CHAMELEON\Chameleon\Content\Paks\
```
(Folder gry najszybciej: Steam → prawy klik na grę → *Zarządzaj* → *Przeglądaj pliki lokalne* → `Chameleon\Content\Paks`.)

## 🗑️ Odinstalowanie
Uruchom `Zainstaluj.exe` → **Odinstaluj** (albo usuń pliki `*_P.*` z folderu `Paks`).

---

## ✅ Wymagania
- Gra **MECCHA CHAMELEON** na Steam (ta sama wersja gry).
- Windows 10/11.

## ⚙️ Jak to zrobione (dla ciekawych)
Nowy dźwięk zaimportowany w **Unreal Engine 5.6**, cookowany pod Windows i spakowany do kontenera IoStore narzędziem [retoc](https://github.com/trumank/retoc) z tym samym `PackageId` co oryginał — dzięki temu pak `_P` nadpisuje dokładnie ten asset.

## ⚠️ Uwagi
- Mod kosmetyczny, działa po Twojej stronie. „Sprawdź integralność plików gry" w Steam usuwa mod → wystarczy zainstalować ponownie.
- Nieoficjalny mod fanowski; nie jest powiązany z twórcami gry.
