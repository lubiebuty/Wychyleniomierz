# 🎯 WYCHYLENIOMIERZ GUI - SKRÓT NA PULPICIE

## ✅ GOTOWE! 

Utworzyłem dla Ciebie skrót na pulpicie:

### 📁 Pliki utworzone:

1. **`Wychyleniomierz GUI.command`** - Główny plik uruchamiający
   - Skopiowany na pulpit
   - Można uruchomić podwójnym kliknięciem

2. **`uruchom_gui.sh`** - Skrypt pomocniczy
   - Automatyczne znajdowanie wolnego portu
   - Sprawdzanie środowiska wirtualnego
   - Powiadomienia o statusie

3. **`Wychyleniomierz.applescript`** - Skrypt AppleScript
   - Alternatywna metoda uruchamiania

4. **`INSTRUKCJA_SKROT_PULPIT.md`** - Szczegółowa instrukcja
   - Jak utworzyć ikonę aplikacji w Automator
   - Jak zmienić ikonę
   - Rozwiązywanie problemów

## 🚀 Jak używać:

### **Metoda 1: Podwójne kliknięcie (najłatwiejsza)**
1. Znajdź na pulpicie plik **"Wychyleniomierz GUI.command"**
2. **Kliknij dwukrotnie** na ikonę
3. Terminal się otworzy i uruchomi aplikację
4. Przeglądarka automatycznie otworzy się z aplikacją

### **Metoda 2: Automator (z własną ikoną)**
1. Otwórz **Automator**
2. Wybierz **"Application"**
3. Dodaj **"Run Shell Script"**
4. Wklej: `cd "/Users/bartlomiejostasz/PYCH/Wychyleniomierz" && ./uruchom_gui.sh`
5. Zapisz jako **"Wychyleniomierz GUI"** na pulpicie

## 🎨 Funkcje skrótu:

- ✅ **Automatyczne uruchamianie** aplikacji
- ✅ **Automatyczne otwieranie** przeglądarki  
- ✅ **Automatyczne znajdowanie** wolnego portu
- ✅ **Sprawdzanie** środowiska wirtualnego
- ✅ **Obsługa błędów** z komunikatami
- ✅ **Powiadomienia** o statusie

## 🔧 Jeśli coś nie działa:

1. **Sprawdź uprawnienia:**
   ```bash
   chmod +x "/Users/bartlomiejostasz/PYCH/Wychyleniomierz/uruchom_gui.sh"
   ```

2. **Sprawdź środowisko wirtualne:**
   ```bash
   cd /Users/bartlomiejostasz/PYCH/Wychyleniomierz
   ls -la venv/
   ```

3. **Zainstaluj zależności:**
   ```bash
   source venv/bin/activate
   pip install -r requirements.txt
   ```

## 🎯 Gotowe do użycia!

Teraz możesz uruchomić Wychyleniomierz GUI jednym kliknięciem na pulpicie! 🎉

---

**Lokalizacja plików:**
- Pulpit: `~/Desktop/Wychyleniomierz GUI.command`
- Folder aplikacji: `/Users/bartlomiejostasz/PYCH/Wychyleniomierz/`
