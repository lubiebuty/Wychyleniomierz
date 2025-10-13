#!/bin/bash
# Prosty skrypt uruchamiający Wychyleniomierz GUI - ZAWSZE DZIAŁA!

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

# Zatrzymaj wszystkie poprzednie instancje
pkill -f "python3 GUI_Wychyleniomierz.py" 2>/dev/null || true
sleep 2

# Uruchom aplikację
python3 GUI_Wychyleniomierz.py &

# Poczekaj na uruchomienie
sleep 5

# Znajdź port na którym działa aplikacja
PORT=""
for port in 7860 7861 7862 7863 7864 7865 7866 7867 7868 7869; do
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
    
    echo ""
    echo "🎉 GOTOWE! Aplikacja działa!"
    echo "📱 Adres: http://localhost:$PORT"
    echo ""
    echo "Aby zatrzymać aplikację, zamknij to okno terminala."
    
    # Poczekaj na zamknięcie terminala
    wait
else
    echo "❌ Nie można znaleźć portu aplikacji"
    echo "Sprawdź czy aplikacja się uruchomiła poprawnie"
    echo "Możliwe przyczyny:"
    echo "- Brak uprawnień do portów"
    echo "- Problem z środowiskiem wirtualnym"
    echo "- Błąd w kodzie aplikacji"
    read -p "Naciśnij Enter aby zamknąć..."
fi
