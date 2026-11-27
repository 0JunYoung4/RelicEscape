@echo off
cd /d "%~dp0"
"%~dp0.venv\Scripts\python.exe" -m tools.preview_b1_encounter %*
