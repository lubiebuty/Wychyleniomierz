# 🖥️ Instrukcja tworzenia skrótu na pulpicie - Wychyleniomierz GUI

## 📋 Kroki do utworzenia skrótu na pulpicie:

### 1. **Utwórz plik aplikacji**

1. Otwórz **Automator** (znajdź w Launchpad lub Applications)
2. Wybierz **"Application"** (Aplikacja)
3. W lewym panelu znajdź **"Run Shell Script"** (Uruchom skrypt powłoki)
4. Przeciągnij go do głównego obszaru

### 2. **Skonfiguruj skrypt**

W polu tekstowym wklej następujący kod:

```bash
#!/bin/bash
cd "/Users/bartlomiejostasz/PYCH/Wychyleniomierz"
./uruchom_gui.sh
```

### 3. **Zapisz aplikację**

1. Naciśnij **Cmd + S** (Zapisz)
2. Nazwij aplikację: **"Wychyleniomierz GUI"**
3. Wybierz lokalizację: **Desktop** (Pulpit)
4. Kliknij **"Save"** (Zapisz)

### 4. **Opcjonalnie: Zmień ikonę**

1. Kliknij prawym przyciskiem na ikonę aplikacji na pulpicie
2. Wybierz **"Get Info"** (Pobierz informacje)
3. Kliknij na ikonę w lewym górnym rogu okna informacji
4. Wklej nową ikonę (Cmd + V) lub przeciągnij plik ikony

## 🎯 Alternatywna metoda - Automator z AppleScript:

### 1. **Otwórz Automator**
2. Wybierz **"Application"**
3. Znajdź **"Run AppleScript"**
4. Wklej kod:

```applescript
tell application "Terminal"
    activate
    do script "cd '/Users/bartlomiejostasz/PYCH/Wychyleniomierz' && ./uruchom_gui.sh"
end tell
```

5. Zapisz jako **"Wychyleniomierz GUI"** na pulpicie

## 🚀 Jak używać:

1. **Kliknij dwukrotnie** na ikonę **"Wychyleniomierz GUI"** na pulpicie
2. Terminal się otworzy i uruchomi aplikację
3. Przeglądarka automatycznie otworzy się z aplikacją
4. Pojawi się powiadomienie o uruchomieniu

## 🔧 Rozwiązywanie problemów:

### Jeśli aplikacja się nie uruchamia:
1. Sprawdź czy masz uprawnienia do wykonywania skryptów
2. Otwórz Terminal i wpisz: `chmod +x /Users/bartlomiejostasz/PYCH/Wychyleniomierz/uruchom_gui.sh`

### Jeśli port jest zajęty:
- Skrypt automatycznie znajdzie wolny port
- Powiadomienie pokaże aktualny port

### Jeśli nie ma środowiska wirtualnego:
- Uruchom najpierw: `cd /Users/bartlomiejostasz/PYCH/Wychyleniomierz && python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt`

## 📱 Funkcje skrótu:

- ✅ **Automatyczne uruchamianie** aplikacji
- ✅ **Automatyczne otwieranie** przeglądarki
- ✅ **Powiadomienia** o statusie
- ✅ **Automatyczne znajdowanie** wolnego portu
- ✅ **Sprawdzanie** środowiska wirtualnego
- ✅ **Obsługa błędów** z komunikatami

## 🎨 Opcjonalne: Ikona aplikacji

Możesz użyć dowolnej ikony PNG/ICO:
1. Pobierz ikonę (np. z internetu)
2. Otwórz ją w Preview
3. Skopiuj (Cmd + C)
4. Kliknij prawym na ikonę aplikacji → Get Info
5. Kliknij na ikonę w oknie informacji
6. Wklej (Cmd + V)

---

**Gotowe!** 🎉 Teraz masz skrót na pulpicie do uruchamiania Wychyleniomierz GUI jednym kliknięciem!
