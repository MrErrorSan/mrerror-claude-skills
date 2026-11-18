@echo off
REM anvil.cmd: run the Anvil CLI from cmd.exe or PowerShell.
REM Finds Python the same way as bin/anvil: python, then py -3, then python3,
REM skipping any interpreter whose path contains WindowsApps (the Microsoft
REM Store stubs). where.exe is called with $PATH: so nothing is picked up from
REM the current directory.
setlocal
REM The trailing "." keeps a backslash from escaping the closing quote below.
set "BIN_DIR=%~dp0."
set "PY="
set "PY_ARGS="
for %%C in (python.exe py.exe python3.exe) do if not defined PY for /f "delims=" %%P in ('"%SystemRoot%\System32\where.exe" $PATH:%%C 2^>nul') do if not defined PY (echo %%P| "%SystemRoot%\System32\findstr.exe" /i WindowsApps >nul || set "PY=%%P")
if not defined PY (
    echo anvil: no working Python found ^(tried python, py -3, python3^) 1>&2
    exit /b 1
)
for %%P in ("%PY%") do if /i "%%~nP"=="py" set "PY_ARGS=-3"

REM Run outside any parenthesized block so %ERRORLEVEL% is read after the run.
"%PY%" %PY_ARGS% -I -c "import sys;sys.path.insert(0,sys.argv.pop(1));from anvil_cli.cli import main;sys.exit(main())" "%BIN_DIR%" %*
exit /b %ERRORLEVEL%
