#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Instalator moda "widzisz mnie?" do gry MECCHA CHAMELEON.

Dziala pod Windowsem i Linuxem (Steam / Steam Proton).
Zmienia dzwiek gwizdu w grze na "widzisz mnie?".

Uzycie:
    python installer.py            -> menu (Zainstaluj / Odinstaluj)
    python installer.py /install   -> instalacja bez pytania
    python installer.py /uninstall -> odinstalowanie bez pytania

Uwaga: skrypt korzysta wylacznie z biblioteki standardowej Pythona 3.
"""

import os
import re
import sys
import glob
import shutil
import string
import platform

# --------------------------------------------------------------------------- #
#  Kolory / styl terminala (a la PassMark MemTest86)
# --------------------------------------------------------------------------- #

IS_WINDOWS = os.name == "nt"


def _enable_ansi_on_windows():
    """Wlacza obsluge sekwencji ANSI w konsoli Windows 10/11."""
    if not IS_WINDOWS:
        return True
    try:
        import ctypes

        kernel32 = ctypes.windll.kernel32
        # ENABLE_VIRTUAL_TERMINAL_PROCESSING = 0x0004
        for handle_id in (-11,):  # STD_OUTPUT_HANDLE
            handle = kernel32.GetStdHandle(handle_id)
            mode = ctypes.c_uint32()
            if kernel32.GetConsoleMode(handle, ctypes.byref(mode)):
                kernel32.SetConsoleMode(handle, mode.value | 0x0004)
        return True
    except Exception:
        return False


_ANSI_OK = _enable_ansi_on_windows()


class C:
    """Kody ANSI. Gdy terminal ich nie wspiera -> puste napisy."""

    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"

    GREEN = "\033[92m"
    RED = "\033[91m"
    CYAN = "\033[96m"
    WHITE = "\033[97m"
    GREY = "\033[90m"
    YELLOW = "\033[93m"

    # tla
    BG_GREEN = "\033[42m"
    BLACK = "\033[30m"


if not _ANSI_OK or os.environ.get("NO_COLOR"):
    for _name in dir(C):
        if not _name.startswith("_") and _name.isupper():
            setattr(C, _name, "")


WIDTH = 64  # szerokosc ramki interfejsu


# --------------------------------------------------------------------------- #
#  Rysowanie interfejsu
# --------------------------------------------------------------------------- #

# Wielkie napisy w stylu blokowym (OK / ERROR), 5-liniowe, monospaced.
_BIG_OK = [
    "  ___  _  __",
    " / _ \\| |/ /",
    "| | | | ' / ",
    "| |_| | . \\ ",
    " \\___/|_|\\_\\",
]

_BIG_ERROR = [
    " _____ ____  ____   ___  ____  ",
    "| ____|  _ \\|  _ \\ / _ \\|  _ \\ ",
    "|  _| | |_) | |_) | | | | |_) |",
    "| |___|  _ <|  _ <| |_| |  _ < ",
    "|_____|_| \\_\\_| \\_\\\\___/|_| \\_\\",
]


def clear_screen():
    os.system("cls" if IS_WINDOWS else "clear")


def hr(char="-"):
    print(f"{C.GREY}{char * WIDTH}{C.RESET}")


def banner(title):
    clear_screen()
    head = " Matcha Cocomelon Mod  -  Instalator v2.0 "
    print(f"{C.BG_GREEN}{C.BLACK}{C.BOLD}{head:<{WIDTH}}{C.RESET}")
    print(f"{C.CYAN}{title:<{WIDTH}}{C.RESET}")
    hr("=")


def info_row(label, value, ok=None):
    """Wiersz 'etykieta : wartosc' jak w panelu MemTest86."""
    if ok is True:
        col = C.GREEN
    elif ok is False:
        col = C.RED
    else:
        col = C.WHITE
    label = f"{label}:"
    print(f"{C.CYAN}{label:<16}{C.RESET}{col}{value}{C.RESET}")


def big_box(lines, color, subtitle):
    """Wielka ramka z napisem OK/ERROR na srodku ekranu."""
    inner_w = max(max(len(l) for l in lines), len(subtitle)) + 8
    pad = " " * inner_w
    border = color + "+" + "-" * inner_w + "+" + C.RESET
    print()
    print("   " + border)
    print("   " + color + "|" + pad + "|" + C.RESET)
    for l in lines:
        centered = l.center(inner_w)
        print("   " + color + "|" + C.BOLD + centered + C.RESET + color + "|" + C.RESET)
    print("   " + color + "|" + pad + "|" + C.RESET)
    print("   " + color + "|" + C.RESET + subtitle.center(inner_w) + color + "|" + C.RESET)
    print("   " + border)
    print()


def ok_box(subtitle="Operacja zakonczona pomyslnie"):
    big_box(_BIG_OK, C.GREEN, subtitle)


def error_box(subtitle="Operacja przerwana"):
    big_box(_BIG_ERROR, C.RED, subtitle)


# --------------------------------------------------------------------------- #
#  Logika: pliki moda
# --------------------------------------------------------------------------- #

MOD_GLOBS = ("*_P.utoc", "*_P.ucas", "*_P.pak")


def script_dir():
    return os.path.dirname(os.path.abspath(sys.argv[0]))


def find_mod_dir():
    """Szuka folderu 'mod' z plikami *_P.* obok skryptu."""
    base = script_dir()
    candidates = [
        os.path.join(base, "mod"),
        base,
    ]
    for cand in candidates:
        if os.path.isdir(cand) and list_mod_files(cand):
            return cand
    return None


def list_mod_files(folder):
    files = []
    for pat in MOD_GLOBS:
        files.extend(glob.glob(os.path.join(folder, pat)))
    return sorted(set(files))


# --------------------------------------------------------------------------- #
#  Logika: wykrywanie gry MECCHA CHAMELEON
# --------------------------------------------------------------------------- #

GAME_SUBPATH = os.path.join(
    "steamapps", "common", "MECCHA CHAMELEON", "Chameleon", "Content", "Paks"
)
GAME_NAME = "MECCHA CHAMELEON"


def _paks_from_library(library_root):
    """Z korzenia biblioteki Steam tworzy sciezke do folderu Paks gry."""
    return os.path.join(library_root, GAME_SUBPATH)


def _steam_roots_windows():
    roots = []
    # 1. Rejestr
    try:
        import winreg

        for hive, key, value in (
            (winreg.HKEY_CURRENT_USER, r"Software\Valve\Steam", "SteamPath"),
            (
                winreg.HKEY_LOCAL_MACHINE,
                r"SOFTWARE\WOW6432Node\Valve\Steam",
                "InstallPath",
            ),
        ):
            try:
                with winreg.OpenKey(hive, key) as k:
                    path, _ = winreg.QueryValueEx(k, value)
                    if path:
                        roots.append(path)
            except OSError:
                pass
    except Exception:
        pass

    # 2. Typowe lokalizacje
    pf = os.environ.get("ProgramFiles", r"C:\Program Files")
    pfx86 = os.environ.get("ProgramFiles(x86)", r"C:\Program Files (x86)")
    for base in (pfx86, pf):
        roots.append(os.path.join(base, "Steam"))
    for drive in _windows_drives():
        roots.append(drive)  # biblioteka moze byc wprost w korzeniu dysku (D:\steamapps\...)
        roots.append(os.path.join(drive, "Steam"))
        roots.append(os.path.join(drive, "SteamLibrary"))
        roots.append(os.path.join(drive, "Games", "Steam"))
        roots.append(os.path.join(drive, "SteamGames"))
    return roots


def _windows_drives():
    drives = []
    for letter in string.ascii_uppercase:
        root = f"{letter}:\\"
        if os.path.isdir(root):
            drives.append(root)
    return drives


def _steam_roots_linux():
    home = os.path.expanduser("~")
    return [
        os.path.join(home, ".steam", "steam"),
        os.path.join(home, ".steam", "root"),
        os.path.join(home, ".local", "share", "Steam"),
        os.path.join(home, ".var", "app", "com.valvesoftware.Steam", "data", "Steam"),
        "/usr/local/games/Steam",
    ]


def _libraries_from_vdf(steam_root):
    """Parsuje libraryfolders.vdf, zwraca dodatkowe korzenie bibliotek."""
    libs = []
    vdf = os.path.join(steam_root, "steamapps", "libraryfolders.vdf")
    if not os.path.isfile(vdf):
        return libs
    try:
        with open(vdf, "r", encoding="utf-8", errors="ignore") as fh:
            text = fh.read()
        for match in re.finditer(r'"path"\s+"(.+?)"', text):
            path = match.group(1).replace("\\\\", os.sep).replace("\\", os.sep)
            libs.append(path)
    except OSError:
        pass
    return libs


def detect_paks_dir():
    """Zwraca sciezke folderu Paks gry albo None."""
    if IS_WINDOWS:
        steam_roots = _steam_roots_windows()
    else:
        steam_roots = _steam_roots_linux()

    seen = set()
    search_roots = []
    for root in steam_roots:
        if root and root not in seen and os.path.isdir(root):
            seen.add(root)
            search_roots.append(root)
            for lib in _libraries_from_vdf(root):
                if lib not in seen:
                    seen.add(lib)
                    search_roots.append(lib)

    for root in search_roots:
        paks = _paks_from_library(root)
        if os.path.isdir(paks):
            return paks
    return None


def resolve_paks_from_user_path(user_path):
    """Z dowolnej sciezki podanej przez uzytkownika wyciaga folder Paks.

    Akceptuje: folder gry, ...\\Content\\Paks, korzen biblioteki Steam.
    """
    user_path = user_path.strip().strip('"').strip("'")
    if not user_path:
        return None
    user_path = os.path.expanduser(user_path)
    if not os.path.isdir(user_path):
        return None

    # Kandydaci wzgledem podanej sciezki.
    candidates = [
        user_path,  # juz Paks?
        os.path.join(user_path, "Paks"),
        os.path.join(user_path, "Content", "Paks"),
        os.path.join(user_path, "Chameleon", "Content", "Paks"),
        os.path.join(user_path, GAME_NAME, "Chameleon", "Content", "Paks"),
        _paks_from_library(user_path),  # korzen biblioteki Steam
    ]
    for cand in candidates:
        if os.path.isdir(cand) and os.path.basename(cand) == "Paks":
            return cand
    # Jako ostatnia deska ratunku: jesli folder zawiera pliki .pak gry.
    if os.path.isdir(user_path) and glob.glob(os.path.join(user_path, "*.utoc")):
        return user_path
    return None


# --------------------------------------------------------------------------- #
#  Akcje: instalacja / odinstalowanie
# --------------------------------------------------------------------------- #


def ask_manual_path():
    print()
    print(f"{C.YELLOW}Nie znalazlem gry {GAME_NAME} automatycznie.{C.RESET}")
    print(f"{C.WHITE}Wskaz folder gry (ten z napisem \"{GAME_NAME}\")")
    print(f"lub jego podfolder ...{os.sep}Content{os.sep}Paks.{C.RESET}")
    print(f"{C.DIM}W Steam: prawy przycisk na grze -> Zarzadzaj -> Przegladaj pliki lokalne.{C.RESET}")
    print(f"{C.DIM}(Enter bez wpisywania = przerwij){C.RESET}")
    try:
        raw = input(f"{C.CYAN}Sciezka> {C.RESET}")
    except (EOFError, KeyboardInterrupt):
        return None
    return resolve_paks_from_user_path(raw)


def get_target_paks(interactive=True):
    paks = detect_paks_dir()
    if paks:
        return paks
    if interactive:
        return ask_manual_path()
    return None


def do_install(interactive=True):
    banner("Instalacja moda - zmiana dzwieku gwizdu")

    mod_dir = find_mod_dir()
    info_row("System", f"{platform.system()} {platform.release()}")
    if not mod_dir:
        info_row("Pliki moda", "NIE ZNALEZIONO", ok=False)
        hr()
        print(f"{C.RED}Nie znalazlem plikow moda.{C.RESET}")
        print("Upewnij sie, ze obok programu jest folder 'mod' z plikami")
        print("*_P.utoc / *_P.ucas / *_P.pak (rozpakuj caly ZIP do jednego folderu).")
        error_box("Brak plikow moda")
        return 1

    mod_files = list_mod_files(mod_dir)
    info_row("Pliki moda", f"{len(mod_files)} plikow", ok=True)

    target = get_target_paks(interactive)
    if not target:
        info_row("Folder gry", "NIE ZNALEZIONO", ok=False)
        hr()
        print(f"{C.RED}PRZERWANO - nie znaleziono folderu gry.{C.RESET}")
        print("Recznie skopiuj pliki *_P.* do:")
        print(f"{C.DIM}   ...{os.sep}{GAME_NAME}{os.sep}Chameleon{os.sep}Content{os.sep}Paks{C.RESET}")
        error_box("Brak folderu gry")
        return 1

    info_row("Folder gry", target, ok=True)
    hr()

    copied = 0
    try:
        os.makedirs(target, exist_ok=True)
        for src in mod_files:
            dst = os.path.join(target, os.path.basename(src))
            print(f"{C.GREEN}  Wgrywanie {C.WHITE}{os.path.basename(src):<32}{C.RESET}", end="")
            shutil.copy2(src, dst)
            copied += 1
            print(f"{C.GREEN}[ OK ]{C.RESET}")
    except Exception as exc:
        hr()
        print(f"{C.RED}BLAD: {exc}{C.RESET}")
        print("Byc moze gra jest uruchomiona albo brak uprawnien do zapisu.")
        error_box("Blad zapisu")
        return 1

    hr()
    print(f"{C.GREEN}Wgrano {copied} plikow do:{C.RESET}")
    print(f"{C.DIM}   {target}{C.RESET}")
    print(f'{C.WHITE}Dzwiek gwizdu zmieniony na "widzisz mnie?".{C.RESET}')
    print(f"{C.WHITE}Uruchom gre i sprawdz (jak byla wlaczona - zrestartuj).{C.RESET}")
    ok_box("MOD ZAINSTALOWANY POMYSLNIE!")
    return 0


def do_uninstall(interactive=True):
    banner("Odinstalowanie moda - powrot do oryginalu")

    mod_dir = find_mod_dir()
    mod_names = (
        {os.path.basename(f) for f in list_mod_files(mod_dir)} if mod_dir else None
    )

    info_row("System", f"{platform.system()} {platform.release()}")

    target = get_target_paks(interactive)
    if not target:
        info_row("Folder gry", "NIE ZNALEZIONO", ok=False)
        hr()
        print(f"{C.RED}PRZERWANO - nie znaleziono folderu gry.{C.RESET}")
        error_box("Brak folderu gry")
        return 1

    info_row("Folder gry", target, ok=True)
    hr()

    removed = 0
    try:
        # Usun pliki dokladnie pasujace do dostarczonego moda,
        # a jesli nie znamy nazw - wszystkie pliki *_P.* w folderze Paks.
        if mod_names:
            targets = [os.path.join(target, n) for n in mod_names]
        else:
            targets = list_mod_files(target)
        for path in targets:
            if os.path.isfile(path):
                print(f"{C.RED}  Usuwanie  {C.WHITE}{os.path.basename(path):<32}{C.RESET}", end="")
                os.remove(path)
                removed += 1
                print(f"{C.GREEN}[ OK ]{C.RESET}")
    except Exception as exc:
        hr()
        print(f"{C.RED}BLAD: {exc}{C.RESET}")
        print("Byc moze gra jest uruchomiona albo brak uprawnien do zapisu.")
        error_box("Blad usuwania")
        return 1

    hr()
    print(f"{C.GREEN}Usunieto plikow: {removed}{C.RESET}")
    print(f"{C.WHITE}Gwizd wrocil do oryginalu.{C.RESET}")
    print(f"{C.DIM}Folder: {target}{C.RESET}")
    ok_box("MOD ODINSTALOWANY")
    return 0


# --------------------------------------------------------------------------- #
#  Menu
# --------------------------------------------------------------------------- #


def menu():
    banner("Mod do MECCHA CHAMELEON")
    info_row("System", f"{platform.system()} {platform.release()}")
    info_row("Mod", 'zmienia dzwiek gwizdu na "widzisz mnie?"')
    paks = detect_paks_dir()
    info_row("Gra", paks if paks else "wykryje przy instalacji", ok=bool(paks))
    hr()
    print(f"{C.WHITE}Co chcesz zrobic?{C.RESET}")
    print(f"  {C.GREEN}[1]{C.RESET} Zainstaluj")
    print(f"  {C.RED}[2]{C.RESET} Odinstaluj")
    print(f"  {C.GREY}[0]{C.RESET} Wyjscie")
    hr()
    try:
        choice = input(f"{C.CYAN}Wybor> {C.RESET}").strip()
    except (EOFError, KeyboardInterrupt):
        return 0

    if choice == "1":
        return do_install(interactive=True)
    if choice == "2":
        return do_uninstall(interactive=True)
    return 0


def main(argv):
    args = [a.lower() for a in argv[1:]]
    if "/install" in args or "--install" in args:
        code = do_install(interactive=True)
    elif "/uninstall" in args or "--uninstall" in args:
        code = do_uninstall(interactive=True)
    else:
        code = menu()

    # Pod Windowsem konsola (uruchomiona dwuklikiem) zamyka sie od razu.
    if IS_WINDOWS and sys.stdin and sys.stdin.isatty():
        try:
            input(f"\n{C.DIM}Nacisnij Enter, aby zamknac...{C.RESET}")
        except (EOFError, KeyboardInterrupt):
            pass
    return code


if __name__ == "__main__":
    sys.exit(main(sys.argv))
