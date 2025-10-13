#!/bin/bash
# Skrypt uruchamiający Wychyleniomierz GUI z ikony pulpitu

# Przejdź do folderu aplikacji
cd "/Users/bartlomiejostasz/PYCH/Wychyleniomierz"

# Sprawdź czy folder istnieje
if [ ! -d "/Users/bartlomiejostasz/PYCH/Wychyleniomierz" ]; then
    osascript -e 'display alert "Błąd" message "Nie można znaleźć folderu aplikacji Wychyleniomierz!" buttons {"OK"} default button "OK"'
    exit 1
fi

# Sprawdź czy środowisko wirtualne istnieje
if [ ! -d "venv" ]; then
    osascript -e 'display alert "Błąd" message "Brak środowiska wirtualnego! Uruchom najpierw instalację." buttons {"OK"} default button "OK"'
    exit 1
fi

# Aktywuj środowisko wirtualne i uruchom aplikację
source venv/bin/activate

# Uruchom aplikację (aplikacja sama znajdzie wolny port)
echo "🚀 Uruchamianie Wychyleniomierz GUI..."

# Uruchom aplikację i przechwytuj output
python3 GUI_Wychyleniomierz.py 2>&1 | tee /tmp/wychyleniomierz_output.log &
APP_PID=$!

# Poczekaj chwilę na uruchomienie
sleep 5

# Znajdź port z logów
PORT=$(grep "Aplikacja będzie dostępna pod adresem:" /tmp/wychyleniomierz_output.log | grep -o 'localhost:[0-9]*' | cut -d: -f2)

if [ -z "$PORT" ]; then
    # Jeśli nie znaleziono portu, spróbuj domyślnych
    for port in 7860 7861 7862 7863 7864; do
        if curl -s "http://localhost:$port" > /dev/null 2>&1; then
            PORT=$port
            break
        fi
    done
fi

if [ -n "$PORT" ]; then
    # Otwórz przeglądarkę
    open "http://localhost:$PORT"
    
    # Pokaż powiadomienie
    osascript -e "display notification \"Wychyleniomierz GUI uruchomiony na http://localhost:$PORT\" with title \"Wychyleniomierz\" subtitle \"Aplikacja gotowa do użycia\""
else
    echo "❌ Nie można znaleźć portu aplikacji"
    osascript -e "display alert \"Błąd\" message \"Nie można znaleźć portu aplikacji!\" buttons {\"OK\"} default button \"OK\""
fi
