@echo off
chcp 65001 >nul
title Matcha Cocomelon Mod - Instalator
cd /d "%~dp0"

rem Szukamy Pythona 3 (launcher "py" lub "python").
set "PYEXE="
where py >nul 2>nul && set "PYEXE=py -3"
if not defined PYEXE (
    where python >nul 2>nul && set "PYEXE=python"
)

if not defined PYEXE (
    echo.
    echo   Nie znalazlem Pythona 3 na tym komputerze.
    echo   Zainstaluj go z https://www.python.org/downloads/
    echo   (przy instalacji zaznacz "Add Python to PATH"^), a potem
    echo   uruchom ten plik ponownie.
    echo.
    pause
    exit /b 1
)

%PYEXE% "%~dp0installer.py" %*
