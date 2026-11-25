@echo off
rem Usage:
rem   run.bat assemble <source.asm> <output.bin> [--test]
rem   run.bat interpret <program.bin> <dump.json> <start> <end>
rem   run.bat test

if "%~1"=="" goto usage
if /I "%~1"=="assemble" goto assemble
if /I "%~1"=="interpret" goto interpret
if /I "%~1"=="test" goto test
goto usage

:assemble
python -m src.assembler %2 %3 %4 %5 %6 %7 %8 %9
exit /b %errorlevel%

:interpret
python -m src.interpreter %2 %3 %4 %5 %6 %7 %8 %9
exit /b %errorlevel%

:test
python -m pytest tests/ -q
exit /b %errorlevel%

:usage
echo Usage: run.bat {assemble^|interpret^|test} [args...]
exit /b 1