@echo off
pyinstaller --onefile --clean --console --icon=icon.ico ^
--add-data "data;data" ^
--add-data "templates;templates" ^
--name AegisConnect App.py
pause
