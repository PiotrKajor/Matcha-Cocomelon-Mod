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

# Znaki blokowe (█) wymagaja UTF-8 na stdout - inaczej stara konsola Windows
# (cp1250) rzucilaby UnicodeEncodeError. errors="replace" = degradacja zamiast crasha.
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass


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

    REVERSE = "\033[7m"

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

# Pikselowa czcionka blokowa - wielkie napisy jak na ekranie testu pamieci.
# Glify 5x7; '#' = piksel wlaczony. Renderowane pelnymi blokami (██).
_FONT = {
    "O": [" ### ", "#   #", "#   #", "#   #", "#   #", "#   #", " ### "],
    "K": ["#   #", "#  # ", "# #  ", "##   ", "# #  ", "#  # ", "#   #"],
    "E": ["#####", "#    ", "#    ", "#### ", "#    ", "#    ", "#####"],
    "R": ["#### ", "#   #", "#   #", "#### ", "# #  ", "#  # ", "#   #"],
}
_FONT_ROWS = 7


def _render_word(word, on="██", off="  ", gap="  "):
    """Sklada wyraz z pikselowych glifow w liste 7 wierszy (poziomo x2)."""
    rows = []
    for r in range(_FONT_ROWS):
        parts = ["".join(on if c == "#" else off for c in _FONT[ch][r]) for ch in word]
        rows.append(gap.join(parts))
    return rows


_BIG_OK = _render_word("OK")
_BIG_ERROR = _render_word("ERROR")


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
    """Pikselowa ramka (z blokow) z napisem OK/ERROR, wysrodkowana na ekranie."""
    term_w = shutil.get_terminal_size((WIDTH + 6, 24)).columns
    content_w = max(max(len(l) for l in lines), len(subtitle))
    inner_w = content_w + 6
    side = "██"  # pionowa krawedz ramki, grubosc dopasowana do pikseli liter
    box_w = inner_w + 2 * len(side)
    margin = " " * max(0, (term_w - box_w) // 2)

    top = color + "█" * box_w + C.RESET
    blank = color + side + " " * inner_w + side + C.RESET

    def framed(inner):
        # tresc miedzy pionowymi krawedziami ramki
        print(margin + color + side + C.RESET + inner + color + side + C.RESET)

    print()
    print(margin + top)
    print(margin + blank)
    for l in lines:
        framed(color + C.BOLD + l.center(inner_w) + C.RESET)
    print(margin + blank)
    framed(subtitle.center(inner_w))
    print(margin + top)
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
    if interactive and UI_TUI:
        return tui_pick_directory()
    if interactive:
        return ask_manual_path()
    return None


def do_install(interactive=True):
    mod_dir = find_mod_dir()
    if not mod_dir:
        banner("Instalacja moda - zmiana dzwieku gwizdu")
        info_row("System", f"{platform.system()} {platform.release()}")
        info_row("Pliki moda", "NIE ZNALEZIONO", ok=False)
        hr()
        print(f"{C.RED}Nie znalazlem plikow moda.{C.RESET}")
        print("Upewnij sie, ze obok programu jest folder 'mod' z plikami")
        print("*_P.utoc / *_P.ucas / *_P.pak (rozpakuj caly ZIP do jednego folderu).")
        error_box("Brak plikow moda")
        return 1

    mod_files = list_mod_files(mod_dir)

    # Najpierw ustalamy folder gry (moze otworzyc przegladarke czyszczaca ekran),
    # a dopiero potem rysujemy czysty ekran podsumowania.
    target = get_target_paks(interactive)

    banner("Instalacja moda - zmiana dzwieku gwizdu")
    info_row("System", f"{platform.system()} {platform.release()}")
    info_row("Pliki moda", f"{len(mod_files)} plikow", ok=True)
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
    mod_dir = find_mod_dir()
    mod_names = (
        {os.path.basename(f) for f in list_mod_files(mod_dir)} if mod_dir else None
    )

    target = get_target_paks(interactive)

    banner("Odinstalowanie moda - powrot do oryginalu")
    info_row("System", f"{platform.system()} {platform.release()}")
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
#  Interaktywny interfejs (TUI): nawigacja strzalkami, przyciski, przegladarka
# --------------------------------------------------------------------------- #

UI_TUI = False  # ustawiane w main(), gdy terminal jest interaktywny


def read_key():
    """Czyta pojedynczy klawisz i normalizuje go.

    Zwraca: 'UP','DOWN','LEFT','RIGHT','ENTER','ESC','SPACE','BACK' lub znak.
    """
    if IS_WINDOWS:
        import msvcrt

        ch = msvcrt.getwch()
        if ch in ("\x00", "\xe0"):
            code = msvcrt.getwch()
            return {"H": "UP", "P": "DOWN", "K": "LEFT", "M": "RIGHT"}.get(code, "")
        if ch in ("\r", "\n"):
            return "ENTER"
        if ch == "\x1b":
            return "ESC"
        if ch == "\x03":
            raise KeyboardInterrupt
        if ch in ("\x08", "\x7f"):
            return "BACK"
        if ch == " ":
            return "SPACE"
        return ch

    import termios
    import tty
    import select

    fd = sys.stdin.fileno()
    old = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        ch = sys.stdin.read(1)
        if ch == "\x1b":
            # rozroznienie: samo ESC vs sekwencja strzalki. 50 ms jest niewidoczne
            # przy wcisnieciu Esc, a pewnie laczy bajty sekwencji (tez przez SSH).
            if select.select([sys.stdin], [], [], 0.05)[0]:
                seq = sys.stdin.read(1)
                if seq in ("[", "O"):
                    code = sys.stdin.read(1)
                    return {"A": "UP", "B": "DOWN", "C": "RIGHT", "D": "LEFT"}.get(code, "")
            return "ESC"
        if ch in ("\r", "\n"):
            return "ENTER"
        if ch == "\x03":
            raise KeyboardInterrupt
        if ch in ("\x08", "\x7f"):
            return "BACK"
        if ch == " ":
            return "SPACE"
        return ch
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old)


def term_width():
    return shutil.get_terminal_size((WIDTH + 6, 24)).columns


def _clear():
    sys.stdout.write("\033[H\033[2J")


def _print_centered(text, vis_len, tw=None):
    tw = tw or term_width()
    print(" " * max(0, (tw - vis_len) // 2) + text)


def _trunc(s, n):
    if len(s) <= n:
        return s
    return "..." + s[-(n - 3):] if n > 3 else s[:n]


def _button(label, focused):
    """Zwraca 3 linie ramki przycisku oraz jego widoczna szerokosc."""
    bw = len(label) + 6
    text = label.center(bw)
    if focused:
        top = C.GREEN + "┏" + "━" * bw + "┓" + C.RESET
        mid = (C.GREEN + "┃" + C.BG_GREEN + C.BLACK + C.BOLD + text
               + C.RESET + C.GREEN + "┃" + C.RESET)
        bot = C.GREEN + "┗" + "━" * bw + "┛" + C.RESET
    else:
        top = C.GREY + "┌" + "─" * bw + "┐" + C.RESET
        mid = C.GREY + "│" + C.RESET + C.WHITE + text + C.GREY + "│" + C.RESET
        bot = C.GREY + "└" + "─" * bw + "┘" + C.RESET
    return (top, mid, bot), bw + 2


def _draw_header(tw):
    title = " MATCHA COCOMELON MOD  —  INSTALATOR v2.0 "
    bar = C.BG_GREEN + C.BLACK + C.BOLD + title.center(44) + C.RESET
    print()
    _print_centered(bar, 44, tw)
    print()


def _draw_info_panel(tw, paks):
    rows = [
        ("System", f"{platform.system()} {platform.release()}", C.WHITE),
        ("Mod", 'dzwiek gwizdu -> "widzisz mnie?"', C.WHITE),
        ("Gra", paks if paks else "wykryje przy instalacji",
         C.GREEN if paks else C.YELLOW),
    ]
    inner = 44
    plain = [f"{lab+':':<12}{_trunc(val, inner-12)}" for lab, val, _ in rows]
    block_w = max(len(p) for p in plain)
    margin = " " * max(0, (tw - block_w) // 2)
    for lab, val, col in rows:
        print(margin + f"{C.CYAN}{lab+':':<12}{C.RESET}{col}{_trunc(val, inner-12)}{C.RESET}")
    print(margin + C.GREY + "─" * block_w + C.RESET)


def tui_menu():
    """Glowne menu z przyciskami. Petla az do wyjscia."""
    labels = ["ZAINSTALUJ", "ODINSTALUJ", "WYJSCIE"]
    sel = 0
    while True:
        tw = term_width()
        _clear()
        _draw_header(tw)
        _draw_info_panel(tw, detect_paks_dir())
        print()

        btns = [_button(lab, i == sel) for i, lab in enumerate(labels)]
        gap = "   "
        vis = sum(w for _, w in btns) + len(gap) * (len(btns) - 1)
        for line_idx in range(3):
            row = gap.join(b[0][line_idx] for b in btns)
            _print_centered(row, vis, tw)
        print()
        hint = (f"{C.DIM}←/→ wybor    Enter zatwierdz    Esc wyjscie{C.RESET}")
        _print_centered(hint, len("←/→ wybor    Enter zatwierdz    Esc wyjscie"), tw)
        sys.stdout.flush()

        try:
            k = read_key()
        except KeyboardInterrupt:
            return 0

        if k in ("LEFT", "UP"):
            sel = (sel - 1) % len(labels)
        elif k in ("RIGHT", "DOWN"):
            sel = (sel + 1) % len(labels)
        elif k in ("1",):
            sel = 0
        elif k in ("2",):
            sel = 1
        elif k in ("0", "q", "Q"):
            return 0
        elif k == "ESC":
            return 0
        elif k == "ENTER":
            if sel == 0:
                do_install(interactive=True)
                wait_for_button()
            elif sel == 1:
                do_uninstall(interactive=True)
                wait_for_button()
            else:
                return 0


def wait_for_button(label="Powrot do menu"):
    """Rysuje wysrodkowany, podswietlony przycisk i czeka na Enter/Esc."""
    if not UI_TUI:
        return
    tw = term_width()
    (top, mid, bot), vis = _button(label, True)
    print()
    _print_centered(top, vis, tw)
    _print_centered(mid, vis, tw)
    _print_centered(bot, vis, tw)
    _print_centered(f"{C.DIM}Enter / Esc{C.RESET}", len("Enter / Esc"), tw)
    sys.stdout.flush()
    while True:
        try:
            k = read_key()
        except KeyboardInterrupt:
            return
        if k in ("ENTER", "ESC", "SPACE"):
            return


# ----  Przegladarka folderow (zamiast wpisywania sciezki)  ---------------- #

DRIVES = "::DRIVES::"


def _is_drive_root(p):
    return IS_WINDOWS and bool(re.match(r"^[A-Za-z]:[\\/]?$", p or ""))


def _parent(p):
    if _is_drive_root(p):
        return None
    par = os.path.dirname(p.rstrip("\\/"))
    if not par or par == p:
        return None
    return par


def _initial_browse_dir():
    roots = _steam_roots_windows() if IS_WINDOWS else _steam_roots_linux()
    for r in roots:
        if r and os.path.isdir(r):
            return r
    return os.path.expanduser("~")


def _subdirs(cur):
    try:
        names = [e.name for e in os.scandir(cur) if e.is_dir()]
    except OSError:
        return []
    return sorted(names, key=str.lower)


def _dir_entries(cur):
    """Buduje liste pozycji przegladarki dla danego folderu."""
    entries = []
    if cur == DRIVES:
        entries.append({"label": "Wybierz dysk / lokalizacje:",
                        "color": C.GREY, "action": "sep", "sel": False})
        for d in _windows_drives():
            entries.append({"label": "  [Dysk]  " + d, "color": C.WHITE,
                            "action": "dir", "payload": d, "sel": True})
        home = os.path.expanduser("~")
        entries.append({"label": "  [Folder domowy]  " + home, "color": C.WHITE,
                        "action": "dir", "payload": home, "sel": True})
        return entries

    entries.append({"label": "> Zainstaluj w TYM folderze", "color": C.GREEN,
                    "action": "choose", "sel": True})
    if _is_drive_root(cur) and IS_WINDOWS:
        entries.append({"label": ".. (inne dyski)", "color": C.CYAN,
                        "action": "drives", "sel": True})
    elif _parent(cur) is not None:
        entries.append({"label": ".. (folder wyzej)", "color": C.CYAN,
                        "action": "up", "sel": True})

    subs = _subdirs(cur)
    entries.append({"label": f"podfoldery ({len(subs)}):", "color": C.GREY,
                    "action": "sep", "sel": False})
    for name in subs:
        entries.append({"label": "  " + name, "color": C.WHITE, "action": "dir",
                        "payload": os.path.join(cur, name), "sel": True})
    if not subs:
        entries.append({"label": "  (brak podfolderow)", "color": C.DIM,
                        "action": "sep", "sel": False})
    return entries


def _first_sel(entries):
    for i, e in enumerate(entries):
        if e.get("sel"):
            return i
    return 0


def _move_sel(entries, idx, step):
    n = len(entries)
    for _ in range(n):
        idx = (idx + step) % n
        if entries[idx].get("sel"):
            return idx
    return idx


def _list_select(title, subtitle, entries, warn=None):
    """Pionowa lista z przewijaniem. Zwraca wybrana pozycje albo None (Esc).

    Skroty: strzalka w lewo / Backspace => zwraca pozycje akcji 'up'/'drives'.
    """
    idx = _first_sel(entries)
    view = 14
    while True:
        tw = term_width()
        inner = min(60, max(30, tw - 8))
        _clear()
        print()
        _print_centered(C.BG_GREEN + C.BLACK + C.BOLD + (" " + title + " ").center(inner)
                        + C.RESET, inner, tw)
        _print_centered(C.CYAN + _trunc(subtitle, inner) + C.RESET,
                        len(_trunc(subtitle, inner)), tw)
        if warn:
            _print_centered(C.YELLOW + _trunc(warn, inner) + C.RESET,
                            len(_trunc(warn, inner)), tw)
        _print_centered(C.GREY + "─" * inner + C.RESET, inner, tw)

        start = 0
        if len(entries) > view:
            start = min(max(0, idx - view // 2), len(entries) - view)
        for i in range(start, min(start + view, len(entries))):
            e = entries[i]
            label = _trunc(e["label"], inner - 2)
            field = (" " + label).ljust(inner)
            if i == idx and e.get("sel"):
                line = C.BG_GREEN + C.BLACK + C.BOLD + field + C.RESET
            else:
                line = e["color"] + field + C.RESET
            _print_centered(line, inner, tw)

        _print_centered(C.GREY + "─" * inner + C.RESET, inner, tw)
        hint = "↑/↓ wybor   Enter otworz/wybierz   ←/Backspace wyzej   Esc anuluj"
        _print_centered(C.DIM + _trunc(hint, inner) + C.RESET,
                        len(_trunc(hint, inner)), tw)
        sys.stdout.flush()

        try:
            k = read_key()
        except KeyboardInterrupt:
            return None

        if k == "UP":
            idx = _move_sel(entries, idx, -1)
        elif k == "DOWN":
            idx = _move_sel(entries, idx, +1)
        elif k == "ENTER":
            if entries[idx].get("sel"):
                return entries[idx]
        elif k in ("LEFT", "BACK"):
            for e in entries:
                if e["action"] in ("up", "drives"):
                    return e
        elif k == "ESC":
            return None


def tui_pick_directory():
    """Interaktywny wybor folderu gry. Zwraca sciezke Paks albo None."""
    cur = _initial_browse_dir()
    warn = None
    while True:
        entries = _dir_entries(cur)
        chosen = _list_select("Wskaz folder gry MECCHA CHAMELEON", cur, entries, warn)
        warn = None
        if chosen is None:
            return None
        act = chosen["action"]
        if act == "choose":
            paks = resolve_paks_from_user_path(cur)
            if paks:
                return paks
            warn = "Brak plikow gry tutaj - wejdz do folderu MECCHA CHAMELEON."
        elif act == "up":
            par = _parent(cur)
            cur = par if par is not None else cur
        elif act == "drives":
            cur = DRIVES
        elif act == "dir":
            cur = chosen["payload"]


# --------------------------------------------------------------------------- #
#  Menu (tryb nieinteraktywny / fallback bez TTY)
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


def _interactive_tty():
    try:
        return bool(_ANSI_OK and sys.stdin.isatty() and sys.stdout.isatty())
    except Exception:
        return False


def main(argv):
    global UI_TUI
    args = [a.lower() for a in argv[1:]]
    if "/install" in args or "--install" in args:
        return do_install(interactive=True)
    if "/uninstall" in args or "--uninstall" in args:
        return do_uninstall(interactive=True)

    if _interactive_tty():
        UI_TUI = True
        try:
            code = tui_menu()
        except KeyboardInterrupt:
            code = 0
        finally:
            _clear()
            sys.stdout.write("\033[0m")
            sys.stdout.flush()
        return code

    # Fallback: brak interaktywnego terminala (potok, przekierowanie).
    code = menu()
    if IS_WINDOWS and sys.stdin and sys.stdin.isatty():
        try:
            input(f"\n{C.DIM}Nacisnij Enter, aby zamknac...{C.RESET}")
        except (EOFError, KeyboardInterrupt):
            pass
    return code


if __name__ == "__main__":
    sys.exit(main(sys.argv))
