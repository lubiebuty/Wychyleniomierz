#!/usr/bin/env osascript
-- Skrypt AppleScript do uruchamiania Wychyleniomierz GUI

tell application "Terminal"
    activate
    do script "cd '/Users/bartlomiejostasz/PYCH/Wychyleniomierz' && ./uruchom_gui.sh"
end tell
