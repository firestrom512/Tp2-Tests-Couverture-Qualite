@echo off
cd /d "%~dp0"
if not exist .venv\Scripts\python.exe (py -m venv .venv)
.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.venv\Scripts\python.exe -m ruff check .
.venv\Scripts\python.exe -m pytest
pause
