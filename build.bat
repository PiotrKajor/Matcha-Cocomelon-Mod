@echo off
REM Build MatchaCocomelonMod-Instalator.exe (PyInstaller onefile, bez konsoli).
REM Wymagania: Python 3.10+ w PATH (launcher `py`). Uruchom z katalogu repo.

setlocal

if not exist venv (
    echo [1/3] Tworze venv...
    py -3 -m venv venv || goto :error
)

echo [2/3] Instaluje zaleznosci...
call venv\Scripts\activate.bat || goto :error
python -m pip install --upgrade pip >nul
pip install -r requirements.txt || goto :error

echo [3/3] PyInstaller...
REM --add-data "mod;mod": pliki moda wbudowane w .exe (onefile) - jeden
REM samowystarczalny plik, bez rozpakowywania ZIP-a. find_mod_dir() w
REM installer.py sprawdza tez sys._MEIPASS, gdy program jest zamrozony.
pyinstaller --noconfirm --clean --onefile --windowed ^
    --name MatchaCocomelonMod-Instalator ^
    --add-data "logo.png;." ^
    --add-data "mod;mod" ^
    installer_gui.py || goto :error

echo.
echo Gotowe: dist\MatchaCocomelonMod-Instalator.exe
exit /b 0

:error
echo.
echo BUILD NIEUDANY — sprawdz komunikaty wyzej.
exit /b 1
