@echo off
pyinstaller --onefile --clean --console --icon=icon.ico --add-data "data;data" --name AegisConnect App.py
pause
