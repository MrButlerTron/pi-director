@echo off  
REM put me in %appdata%\Microsoft\Windows\Start Menu\Programs\Startup
REM Assuming chrome is installed globally and system auto logs in
REM put your URL where you host the pi-director app in the URL variable
set URL=
start "" "C:\Program Files\Google\Chrome\Application\chrome.exe"  --start-fullscreen  --disable-session-crashed-bubble --noerrordialogs --hide-crash-restore-bubble --noerrors http://%URL%?host=%COMPUTERNAME% &