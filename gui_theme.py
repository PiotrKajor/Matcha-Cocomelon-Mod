"""Ciemny motyw (QSS) dla installer_gui.py — bez zewnętrznych pakietów motywów.
Ten sam motyw co w DupeDealer (github.com/PiotrKajor/DupeDealer/gui_theme.py) —
wspólny wygląd GUI między projektami.

Paleta: granatowa czerń + steamowy błękit jako akcent. Wszystko zaokrąglone,
hover/pressed na przyciskach, tabela z naprzemiennymi wierszami i płaskim
nagłówkiem, slim scrollbary.

Strzałki (spinbox/combobox) i „ptaszek" checkboxa to małe PNG-i osadzone jako
base64 — Qt nie renderuje trójkątów z borderów tak jak CSS (wychodzi kwadrat),
więc `build_qss()` zapisuje je do temp i wstrzykuje ścieżki do arkusza.
"""
import base64
import os
import tempfile

BG = "#11141b"          # tło okna
SURFACE = "#181c26"     # panele/karty
SURFACE2 = "#212736"    # inputy, wiersze parzyste
BORDER = "#2a3245"
TEXT = "#e8ecf4"
TEXT_DIM = "#8b94a7"
ACCENT = "#4fb4ff"      # steamowy błękit
ACCENT_HOVER = "#6cc3ff"
ACCENT_PRESSED = "#3798e2"
GREEN = "#3ddc84"
RED = "#ff5d6c"
YELLOW = "#ffb454"

# --- ikonki (PNG base64) generowane raz, offline; kolor DIM/akcent wtopiony ---
_ARROW_DOWN = "iVBORw0KGgoAAAANSUhEUgAAAAoAAAAGCAYAAAD68A/GAAAA2klEQVR4nFXOMWoCQRgF4Df7j4q7prDxCF4gJ/ACAQPaWKRyCxvLIFtYGgUDihi0stAII3iCQJoUuUdKCxvdmXWd/S0Wg77q8fiKJwaT9cLNey86PJwhhMRNOEms6xUoDMO1cyyRr/Xxy/UeJDOf/xGnSBv9I0zcFADQm66KOZH5JSnLkTEWgMhmc06S2D99wmPQru+cmlLUaTX2sYmerLV7KSUREZjZRKe4GrTrO6UUAQCupT9aVt4/NvFovuW38fIZALrd77vf8GezTIpXr/3x5xAAfD/dAOACgyBcM24VpbIAAAAASUVORK5CYII="
_ARROW_DOWN_SM = "iVBORw0KGgoAAAANSUhEUgAAAAkAAAAGCAYAAAARx7TFAAAAyklEQVR4nE3IoU7DUBSH8f89p1l3OxIegVfhIQCxJQgEYoJiIBDEra4jw2LXJbNYMo9GYHgCQpgg7b1dzzkYSPjUL5+rF83a++Koa7/FETF+M1XxxYRjbJ9IWM9j6t5yX7CZKQCYmY7GnlNK7yPJzuh2Pvvqd/2xikRmBmBKRGZmMsgwLcuTDwphk91dnr6m2M7zsSfA7YrJHvepu7q5mL2EsMkAAH+oF8394+rZ6odl8/9nAFBVhwIEynX/erv9PHA0lDBzqCoFgB8uN19QQJZICgAAAABJRU5ErkJggg=="
_ARROW_UP_SM = "iVBORw0KGgoAAAANSUhEUgAAAAkAAAAGCAYAAAARx7TFAAAA3ElEQVR4nC3OMU4CQRQG4P+9GXZWQLPGxAvYUHABrOQEHkAbL0Bho90whdFIjGxDjAXFJjRUVrZYWegZvINiZHdgZ56Ftl/1AQBEhKy1nOfP5u5h/jSaFPv4NwBgABgOX5RzLnr+us2yvWOJOgeRAEcMAGTtQjvXr2/GxVl7J5uWqx/fam+b7+Xn+cXg9N7ahSYAuBoX3WbafI8xJDEGELEo3YD31eHl4OSNriezXS3qNUlMx1dlJCIWkZiYlOvN5qNRU49V4MfUbHV8uQpE9Hcg4nVVBmPMwVrV019ocVdrejj7pwAAAABJRU5ErkJggg=="
_CHECK = "iVBORw0KGgoAAAANSUhEUgAAAA4AAAAOCAYAAAAfSC3RAAABbUlEQVR4nI2SsWsUQRTGf+/tqLmd271cdjeIhbWVhRjTamtpGxEsbQUrC3vBWhFLK1sbwX9AsBALa0kdFe/kTnK5nc8ie7gcUe4VM4/h+33fMG9gs7JuzzbUnwltBGcAg7LaG5a7n+KourXu9q8kb5pmMDvWRze/IqUW8XA2PPdqHfQOaIEALPOifu1uB5IWQDBzTyndDmtQ6vrzwCIvmvvuHEhaAm5mLtLL+a9v71aJAVgOymrP0fZs+uN9jNtXycIH4AKQMAuSvszH8TqHh8e2Soqxuklmb4GtJN1x47GZ73dpBrRyuzH/efQZyAywvKjumtlzIP59F9EtrZmFVunB7+n3F6vbOSCcS2YegcWpWOpDKaU3fWhlnQFtXlSP3P2ppJNOkMAypK/BT65NJpNpZ6b+GAJAXlbPhqNdxbJWLBvFUaNBsbPf/wxnDTs7hesnsawnsayP8mLn3v+gfjnA1nh8Oc+bi/2z9foD0wt6svcfem0AAAAASUVORK5CYII="


def _write_assets(asset_dir):
    """Zapisuje PNG-i do katalogu i zwraca ścieżki (forward slash — Qt QSS lubi je
    na każdej platformie, też Windows)."""
    os.makedirs(asset_dir, exist_ok=True)
    out = {}
    for name, data in (("arrow_down", _ARROW_DOWN), ("arrow_down_sm", _ARROW_DOWN_SM),
                       ("arrow_up_sm", _ARROW_UP_SM), ("check", _CHECK)):
        path = os.path.join(asset_dir, name + ".png")
        if not os.path.exists(path):
            with open(path, "wb") as f:
                f.write(base64.b64decode(data))
        out[name] = path.replace("\\", "/")
    return out


def build_qss(asset_dir=None):
    """Zwraca gotowy arkusz QSS. Ikonki lądują w `asset_dir` (domyślnie podkatalog
    w temp systemu)."""
    if asset_dir is None:
        asset_dir = os.path.join(tempfile.gettempdir(), "dupedealer_assets")
    a = _write_assets(asset_dir)
    return f"""
* {{
    font-family: 'Segoe UI', 'Inter', 'Cantarell', 'Noto Sans', sans-serif;
    font-size: 13px;
    color: {TEXT};
    selection-background-color: {ACCENT};
    selection-color: #0b0e14;
    outline: none;
}}
QMainWindow, QDialog, QMessageBox {{ background: {BG}; }}

#Header {{
    background: {SURFACE};
    border: 1px solid {BORDER};
    border-radius: 12px;
}}
#AppTitle {{ font-size: 16px; font-weight: 700; }}
#AppSubtitle {{ color: {TEXT_DIM}; font-size: 12px; }}
#StatusDot {{ font-size: 15px; }}
#StatusLabel {{ font-weight: 600; }}
#HintLabel {{ color: {TEXT_DIM}; }}

#Card {{
    background: {SURFACE};
    border: 1px solid {BORDER};
    border-radius: 12px;
}}
QLabel {{ background: transparent; border: none; }}

QPushButton {{
    background: {SURFACE2};
    border: 1px solid {BORDER};
    border-radius: 9px;
    padding: 7px 16px;
    font-weight: 600;
}}
QPushButton:hover {{ background: #2a3143; border-color: #38445c; }}
QPushButton:pressed {{ background: #1b202c; }}
QPushButton:disabled {{ color: #5b6373; background: #1a1e29; border-color: #232a38; }}

QPushButton[class="accent"] {{
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 {ACCENT}, stop:1 #2f8fdd);
    border: none;
    color: #06121f;
}}
QPushButton[class="accent"]:hover {{
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 {ACCENT_HOVER}, stop:1 {ACCENT});
}}
QPushButton[class="accent"]:pressed {{ background: {ACCENT_PRESSED}; }}
QPushButton[class="accent"]:disabled {{ background: #27374a; color: #5b6373; }}

QPushButton[class="danger"] {{
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #ff6b78, stop:1 #d94550);
    border: none;
    color: #1c0608;
}}
QPushButton[class="danger"]:hover {{ background: #ff7d89; }}
QPushButton[class="danger"]:disabled {{ background: #3a2830; color: #6d5a5e; }}

QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox {{
    background: {SURFACE2};
    border: 1px solid {BORDER};
    border-radius: 8px;
    padding: 6px 10px;
}}
QLineEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus, QComboBox:focus {{
    border-color: {ACCENT};
}}
QSpinBox, QDoubleSpinBox {{ padding-right: 20px; }}
QSpinBox::up-button, QDoubleSpinBox::up-button {{
    subcontrol-origin: border; subcontrol-position: top right;
    width: 18px; height: 50%;
    border: none; border-top-right-radius: 8px; background: transparent;
}}
QSpinBox::down-button, QDoubleSpinBox::down-button {{
    subcontrol-origin: border; subcontrol-position: bottom right;
    width: 18px; height: 50%;
    border: none; border-bottom-right-radius: 8px; background: transparent;
}}
QSpinBox::up-button:hover, QDoubleSpinBox::up-button:hover,
QSpinBox::down-button:hover, QDoubleSpinBox::down-button:hover {{ background: #2a3143; }}
QSpinBox::up-arrow, QDoubleSpinBox::up-arrow {{
    image: url({a['arrow_up_sm']}); width: 9px; height: 6px;
}}
QSpinBox::down-arrow, QDoubleSpinBox::down-arrow {{
    image: url({a['arrow_down_sm']}); width: 9px; height: 6px;
}}
QComboBox::drop-down {{
    subcontrol-origin: padding; subcontrol-position: center right;
    border: none; width: 26px;
}}
QComboBox::down-arrow {{ image: url({a['arrow_down']}); width: 10px; height: 6px; }}
QComboBox QAbstractItemView {{
    background: {SURFACE2};
    border: 1px solid {BORDER};
    border-radius: 8px;
    padding: 4px;
    selection-background-color: {ACCENT};
    selection-color: #0b0e14;
}}

QTableWidget {{
    background: {SURFACE};
    alternate-background-color: #1c212d;
    border: 1px solid {BORDER};
    border-radius: 12px;
    gridline-color: transparent;
}}
QTableWidget::item {{ padding: 4px 8px; border: none; }}
QTableWidget::item:selected {{ background: #29405e; color: {TEXT}; }}
QHeaderView::section {{
    background: #1d2330;
    color: {TEXT_DIM};
    font-weight: 700;
    border: none;
    border-bottom: 2px solid {BORDER};
    padding: 8px 8px;
}}
QHeaderView::section:first {{ border-top-left-radius: 12px; }}
QHeaderView::section:last {{ border-top-right-radius: 12px; }}
QTableCornerButton::section {{ background: #1d2330; border: none; }}

QProgressBar {{
    background: {SURFACE2};
    border: none;
    border-radius: 5px;
    height: 10px;
    text-align: center;
    color: transparent;
}}
QProgressBar::chunk {{
    border-radius: 5px;
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 {ACCENT}, stop:1 #7cd0ff);
}}

QPlainTextEdit {{
    background: #0c0f15;
    border: 1px solid {BORDER};
    border-radius: 12px;
    font-family: 'Cascadia Mono', 'Consolas', 'DejaVu Sans Mono', monospace;
    font-size: 12px;
    padding: 6px;
}}

QCheckBox {{ spacing: 8px; }}
QCheckBox::indicator, QTableWidget::indicator {{
    width: 17px; height: 17px;
    border: 1px solid {BORDER};
    border-radius: 5px;
    background: {SURFACE2};
}}
QCheckBox::indicator:hover, QTableWidget::indicator:hover {{ border-color: {ACCENT}; }}
QCheckBox::indicator:checked, QTableWidget::indicator:checked {{
    background: {ACCENT};
    border-color: {ACCENT};
    image: url({a['check']});
}}

QScrollBar:vertical {{
    background: transparent; width: 10px; margin: 2px;
}}
QScrollBar::handle:vertical {{
    background: #333d52; border-radius: 4px; min-height: 28px;
}}
QScrollBar::handle:vertical:hover {{ background: #43506c; }}
QScrollBar:horizontal {{
    background: transparent; height: 10px; margin: 2px;
}}
QScrollBar::handle:horizontal {{
    background: #333d52; border-radius: 4px; min-width: 28px;
}}
QScrollBar::handle:horizontal:hover {{ background: #43506c; }}
QScrollBar::add-line, QScrollBar::sub-line {{ width: 0; height: 0; }}
QScrollBar::add-page, QScrollBar::sub-page {{ background: transparent; }}

QToolTip {{
    background: {SURFACE2};
    color: {TEXT};
    border: 1px solid {BORDER};
    border-radius: 6px;
    padding: 5px 8px;
}}
QMessageBox QLabel {{ font-size: 13px; }}
"""
