@echo off
rem Drag a document onto this file: summary is saved and opened in Notepad.
if "%~1"=="" (
  echo Drag a file onto this .bat
  pause
  exit /b 1
)
python "%~dp0summarize.py" "%~1" --out "%~dp0output\%~n1_summary.md"
if not errorlevel 1 notepad "%~dp0output\%~n1_summary.md"
pause
