@echo off
setlocal

python -m pip install -e .[dev]

pyinstaller ^
  --noconfirm ^
  --clean ^
  --onefile ^
  --name MouseMover ^
  --collect-submodules mousemover.plugins ^
  --paths src ^
  launcher.py

echo Gerado em dist\MouseMover.exe
echo Sem argumentos: GUI
echo Com argumentos: CLI
