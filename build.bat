\\@echo off
call inv_env\Scripts\activate
inv_env\Scripts\pyinstaller --onefile --icon=inventory.ico inventory.py
pause
