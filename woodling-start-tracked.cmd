@echo off
set "ROOT=%~dp0"
Start "" pyw "%ROOT%app.py"
Start "" /B py "%ROOT%woodling_tracker.py"
