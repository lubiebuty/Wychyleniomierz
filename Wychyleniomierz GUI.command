#!/bin/bash
# Wychyleniomierz GUI Launcher
# Podwójne kliknięcie uruchamia aplikację

# Przejdź do folderu aplikacji
cd "/Users/bartlomiejostasz/PYCH/Wychyleniomierz"

# Sprawdź czy folder istnieje
if [ ! -d "/Users/bartlomiejostasz/PYCH/Wychyleniomierz" ]; then
    echo "❌ Błąd: Nie można znaleźć folderu aplikacji!"
    read -p "Naciśnij Enter aby zamknąć..."
    exit 1
fi

# Sprawdź czy środowisko wirtualne istnieje
if [ ! -d "venv" ]; then
    echo "❌ Błąd: Brak środowiska wirtualnego!"
    echo "Uruchom najpierw instalację:"
    echo "python3 -m venv venv"
    echo "source venv/bin/activate"
    echo "pip install -r requirements.txt"
    read -p "Naciśnij Enter aby zamknąć..."
    exit 1
fi

echo "🚀 Uruchamianie Wychyleniomierz GUI..."

# Aktywuj środowisko wirtualne
source venv/bin/activate

echo "🚀 Uruchamianie Wychyleniomierz GUI..."

# Uruchom aplikację w tle
python3 GUI_Wychyleniomierz.py &

# Poczekaj chwilę na uruchomienie
sleep 5

# Sprawdź na jakim porcie działa aplikacja
PORT=""
for port in 7860 7861 7862 7863 7864 7865; do
    if curl -s "http://localhost:$port" > /dev/null 2>&1; then
        PORT=$port
        break
    fi
done

if [ -n "$PORT" ]; then
    echo "✅ Aplikacja uruchomiona na porcie $PORT!"
    echo "🌐 Otwórz przeglądarkę pod adresem: http://localhost:$PORT"
    
    # Otwórz przeglądarkę
    open "http://localhost:$PORT"
else
    echo "❌ Nie można znaleźć portu aplikacji"
    echo "Sprawdź czy aplikacja się uruchomiła poprawnie"
fi
echo ""
echo "Aby zatrzymać aplikację, zamknij to okno terminala."

# Poczekaj na zamknięcie terminala
wait
