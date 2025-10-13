#!/bin/bash
# Skrypt uruchamiający GUI Wychyleniomierza

# Zmień katalog na folder projektu
cd "$(dirname "$0")"

# Aktywuj środowisko wirtualne
if [ -d "venv" ]; then
    echo "🔄 Aktywacja środowiska wirtualnego..."
    source venv/bin/activate
else
    echo "❌ Brak środowiska wirtualnego!"
    echo "Uruchom najpierw: python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt"
    exit 1
fi

# Uruchom aplikację
echo "🚀 Uruchamianie Wychyleniomierz GUI..."
echo "📱 Aplikacja będzie dostępna pod adresem: http://localhost:7862"
python3 GUI_Wychyleniomierz.py

