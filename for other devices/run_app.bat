@echo off
echo Starting D&D Campaign App...
start run_server.bat
timeout /t 2 /nobreak > nul
start run_client.bat
echo App started. Close this window to exit.
pause
