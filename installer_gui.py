#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""GUI (PySide6) instalatora moda Matcha Cocomelon — nakładka na installer.py.

Nie duplikuje logiki: woła detect_paks_dir / resolve_paks_from_user_path /
find_mod_dir / list_mod_files z installer.py. Kopiowanie kilku małych plików
jest natychmiastowe, więc działa wprost w wątku GUI (bez QThread).

Uruchomienie: python installer_gui.py
Build .exe:   build.bat (PyInstaller, patrz README)
"""
import os
import shutil
import sys

from installer import (
    GAME_NAME, detect_paks_dir, find_mod_dir, list_mod_files,
    resolve_paks_from_user_path,
)
from gui_theme import build_qss, GREEN, RED, YELLOW

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QApplication, QFileDialog, QFrame, QHBoxLayout, QLabel, QLineEdit,
    QMainWindow, QMessageBox, QPlainTextEdit, QPushButton, QVBoxLayout, QWidget,
)


def resource_path(name):
    """Ścieżka do pliku dołączonego do buildu (PyInstaller onefile) lub obok źródła."""
    base = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, name)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Matcha Cocomelon Mod — Instalator")
        self.resize(720, 500)
        logo = resource_path("logo.png")
        if os.path.exists(logo):
            self.setWindowIcon(QIcon(logo))

        self.mod_dir = find_mod_dir()
        self.mod_files = list_mod_files(self.mod_dir) if self.mod_dir else []

        self._build_ui()
        self._log(
            f"Znaleziono {len(self.mod_files)} plików moda."
            if self.mod_files
            else "Nie znalazłem plików moda — rozpakuj cały ZIP do jednego folderu.",
            GREEN if self.mod_files else RED,
        )
        self._auto_detect()

    # ------------------------------------------------------------- układ ---
    def _build_ui(self):
        root = QWidget()
        self.setCentralWidget(root)
        v = QVBoxLayout(root)
        v.setContentsMargins(14, 14, 14, 14)
        v.setSpacing(10)

        header = QFrame(); header.setObjectName("Header")
        h = QHBoxLayout(header); h.setContentsMargins(16, 12, 16, 12)
        tbox = QVBoxLayout(); tbox.setSpacing(0)
        t1 = QLabel("Matcha Cocomelon Mod"); t1.setObjectName("AppTitle")
        t2 = QLabel('Zmienia dźwięk gwizdu na „widzisz mnie?"')
        t2.setObjectName("AppSubtitle")
        tbox.addWidget(t1); tbox.addWidget(t2)
        h.addLayout(tbox)
        h.addStretch(1)
        self.status_dot = QLabel("●"); self.status_dot.setObjectName("StatusDot")
        self.status_label = QLabel("Szukam gry…"); self.status_label.setObjectName("StatusLabel")
        h.addWidget(self.status_dot); h.addWidget(self.status_label)
        v.addWidget(header)

        card = QFrame(); card.setObjectName("Card")
        p = QHBoxLayout(card); p.setContentsMargins(16, 12, 16, 12); p.setSpacing(10)
        p.addWidget(QLabel("Folder gry:"))
        self.path_edit = QLineEdit()
        self.path_edit.setPlaceholderText(f"...\\{GAME_NAME}\\Chameleon\\Content\\Paks")
        p.addWidget(self.path_edit, 1)
        btn_browse = QPushButton("Przeglądaj…")
        btn_browse.clicked.connect(self._browse)
        p.addWidget(btn_browse)
        btn_detect = QPushButton("Wykryj automatycznie")
        btn_detect.clicked.connect(self._auto_detect)
        p.addWidget(btn_detect)
        v.addWidget(card)

        self.log = QPlainTextEdit(); self.log.setReadOnly(True)
        v.addWidget(self.log, 1)

        actions = QHBoxLayout()
        actions.addStretch(1)
        self.btn_install = QPushButton("Zainstaluj")
        self.btn_install.setProperty("class", "accent")
        self.btn_install.setEnabled(bool(self.mod_files))
        self.btn_install.clicked.connect(self._install)
        self.btn_uninstall = QPushButton("Odinstaluj")
        self.btn_uninstall.setProperty("class", "danger")
        self.btn_uninstall.clicked.connect(self._uninstall)
        actions.addWidget(self.btn_install); actions.addWidget(self.btn_uninstall)
        v.addLayout(actions)

    # ---------------------------------------------------------- pomocnicze ---
    def _log(self, text, color=None):
        if color:
            self.log.appendHtml(f'<span style="color:{color}">{text}</span>')
        else:
            self.log.appendPlainText(text)
        sb = self.log.verticalScrollBar()
        sb.setValue(sb.maximum())

    def _set_status(self, ok, text):
        self.status_dot.setStyleSheet(f"color: {GREEN if ok else RED};")
        self.status_label.setText(text)

    def _auto_detect(self):
        paks = detect_paks_dir()
        if paks:
            self.path_edit.setText(paks)
            self._set_status(True, "Gra wykryta")
            self._log(f"Wykryto grę: {paks}", GREEN)
        else:
            self._set_status(False, "Nie znaleziono gry")
            self._log("Nie wykryłem gry automatycznie — wskaż folder ręcznie.", YELLOW)

    def _browse(self):
        start = self.path_edit.text().strip() or os.path.expanduser("~")
        chosen = QFileDialog.getExistingDirectory(
            self, "Wskaż folder gry MECCHA CHAMELEON", start)
        if chosen:
            self.path_edit.setText(chosen)

    def _resolve_target(self):
        raw = self.path_edit.text().strip()
        target = resolve_paks_from_user_path(raw) if raw else None
        if not target:
            QMessageBox.warning(
                self, "Nie znaleziono gry",
                "Wskaż folder gry MECCHA CHAMELEON (albo jego podfolder "
                "Content\\Paks) i spróbuj ponownie.")
            return None
        self.path_edit.setText(target)
        self._set_status(True, "Gra wykryta")
        return target

    # ------------------------------------------------------------- akcje ---
    def _install(self):
        if not self.mod_files:
            QMessageBox.critical(
                self, "Brak plików moda",
                "Nie znalazłem plików moda obok programu. Rozpakuj cały ZIP "
                "do jednego folderu.")
            return
        target = self._resolve_target()
        if not target:
            return
        try:
            os.makedirs(target, exist_ok=True)
            for src in self.mod_files:
                dst = os.path.join(target, os.path.basename(src))
                shutil.copy2(src, dst)
                self._log(f"Wgrano {os.path.basename(src)}", GREEN)
        except OSError as exc:
            self._log(f"Błąd zapisu: {exc}", RED)
            QMessageBox.critical(self, "Błąd zapisu",
                                  f"{exc}\n\nGra może być uruchomiona albo brak "
                                  "uprawnień do zapisu.")
            return
        self._log('Dźwięk gwizdu zmieniony na „widzisz mnie?".', GREEN)
        QMessageBox.information(self, "Gotowe",
                                 "Mod zainstalowany. Uruchom (lub zrestartuj) grę.")

    def _uninstall(self):
        target = self._resolve_target()
        if not target:
            return
        mod_names = {os.path.basename(f) for f in self.mod_files} if self.mod_files else None
        targets = ([os.path.join(target, n) for n in mod_names] if mod_names
                   else list_mod_files(target))
        removed = 0
        try:
            for path in targets:
                if os.path.isfile(path):
                    os.remove(path)
                    removed += 1
                    self._log(f"Usunięto {os.path.basename(path)}", GREEN)
        except OSError as exc:
            self._log(f"Błąd usuwania: {exc}", RED)
            QMessageBox.critical(self, "Błąd usuwania",
                                  f"{exc}\n\nGra może być uruchomiona albo brak "
                                  "uprawnień do zapisu.")
            return
        self._log(f"Usunięto plików: {removed}. Gwizd wrócił do oryginału.", GREEN)
        QMessageBox.information(self, "Gotowe", f"Odinstalowano ({removed} plików).")


def main():
    app = QApplication(sys.argv)
    app.setStyleSheet(build_qss())
    win = MainWindow()
    win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
