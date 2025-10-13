# Wychyleniomierz - GUI

System do kalibracji kamery i pomiaru wychyleń z użyciem markerów ArUco/ChArUco.

## Instalacja

### Wymagania
- Python 3.8 lub nowszy
- OpenCV z modułem contrib
- Gradio

### Instalacja zależności

```bash
pip install -r requirements.txt
```

Lub ręcznie:

```bash
pip install gradio opencv-contrib-python numpy matplotlib pandas pillow
```

## Uruchomienie

```bash
python GUI_Wychyleniomierz.py
```

Aplikacja otworzy się automatycznie w przeglądarce pod adresem `http://localhost:7860`

## Instrukcja użycia

### Okno 1: Kalibracja

#### Krok 1: Wzorzec kalibracyjny
1. Kliknij przycisk **"📥 Pobierz wzorzec kalibracyjny"**
2. Wzorzec zostanie wygenerowany i zapisany w folderze `patterns/`
3. Wydrukuj wzorzec w skali 100% (bez dopasowania)
4. Po wydruku zmierz pasek skali - powinien mieć dokładnie 100 mm

#### Krok 2: Wybierz metodę kalibracji

**Opcja A: Wgraj gotowy plik kalibracji**
- Jeśli masz już plik kalibracyjny `.npz`, przeciągnij go do pola lub kliknij aby wybrać
- System automatycznie sprawdzi czy plik ma rozszerzenie `.npz`

**Opcja B: Wykonaj nową kalibrację**

1. **Nagraj wideo kalibracyjne:**
   - Ustaw wydrukowany wzorzec w stabilnym miejscu
   - Nagraj wideo pokazujące wzorzec z różnych kątów i odległości
   - Minimum 5-10 sekund wideo
   - Upewnij się, że wzorzec jest dobrze oświetlony i wyraźny

2. **Wgraj wideo:**
   - Przeciągnij plik wideo lub kliknij aby wybrać
   - Obsługiwane formaty: `.mp4`, `.mov`, `.avi`

3. **Ustaw parametry kalibracji:**
   - **Nazwa serii:** Podaj opisową nazwę (np. `kalibracja_laboratorium_1`)
   - **Frameskip:** Wybierz co ile klatek przeprowadzać analizę
     - Niższy frameskip (5-10) = wyższa dokładność, dłuższy czas
     - Wyższy frameskip (15-30) = szybsza kalibracja, niższa dokładność
     - Zalecane: 10-15

4. **Rozpocznij kalibrację:**
   - Kliknij **"🚀 Rozpocznij kalibrację"**
   - Poczekaj na zakończenie procesu
   - System wyświetli szczegółowy raport kalibracji

#### Krok 3: Raport kalibracji

Po zakończeniu kalibracji zobaczysz raport zawierający:
- RMS error (błąd reprojekcji)
- Macierz kamery
- Współczynniki dystorsji
- Statystyki wykrywania
- Ocenę jakości kalibracji

**Ocena jakości:**
- RMS < 0.5 px: DOSKONAŁA jakość
- RMS < 1.0 px: BARDZO DOBRA jakość
- RMS < 2.0 px: DOBRA jakość
- RMS > 2.0 px: SŁABA jakość (rozważ powtórzenie)

**Opcje:**
- **🔄 Powtórz kalibrację:** Jeśli jakość jest niezadowalająca
- **✅ Akceptuj i przejdź dalej:** Zapisz kalibrację i przejdź do pomiarów

#### Krok 4: Folder na wyniki

Po zaakceptowaniu kalibracji:
1. Podaj nazwę folderu na wyniki pomiarów
2. Kliknij **"📁 Utwórz folder"**
3. System utworzy folder z datą i godziną
4. Plik kalibracyjny zostanie skopiowany do podfolderu

### Okno 2: Pomiary

#### Wykonywanie pomiarów

1. **Przygotowanie:**
   - Upewnij się, że kalibracja została zakończona
   - Przygotuj marker ArUco (domyślnie ID=2 ze słownika DICT_6X6_1000)
   - Ustaw marker na obiekcie, którego wychylenia chcesz mierzyć

2. **Nagraj wideo pomiaru:**
   - Marker musi być widoczny przez większość czasu
   - Marker powinien być dobrze oświetlony
   - Unikaj silnych odbić i cieni

3. **Wgraj wideo:**
   - Przeciągnij plik wideo lub kliknij aby wybrać
   - Obsługiwane formaty: `.mp4`, `.mov`, `.avi`

4. **Podaj nazwę pomiaru:**
   - Wpisz opisową nazwę (np. `test_obciazenie_50kg`)

5. **Rozpocznij pomiar:**
   - Kliknij **"🚀 Rozpocznij pomiar"**
   - Poczekaj na zakończenie analizy

#### Wyniki pomiarów

System wygeneruje następujące pliki w folderze pomiaru:

- `out_annotated.mp4` - Wideo z naniesionymi adnotacjami (wykryty marker)
- `out_annotated_with_plot.mp4` - Wideo z wykresem wychyleń w czasie rzeczywistym
- `positions_px.csv` - Dane pozycji w pikselach i cm
- `deflection_y_px.png` - Wykres wychylenia pionowego w pikselach
- `deflection_y_cm.png` - Wykres wychylenia pionowego w centymetrach

#### Kolejne pomiary

Po zakończeniu pomiaru:
- Kliknij **"➕ Dodaj kolejny pomiar"**
- Wgraj kolejne wideo
- Wszystkie pomiary zostaną zapisane w tym samym folderze wyników

## Struktura folderów

```
Wychyleniomierz/
├── serie_kalibracji/
│   └── nazwa_serii_YYYY-MM-DD_HH-MM-SS/
│       ├── pliki_kalibracji/
│       │   ├── charuco_calibration.npz
│       │   ├── charuco_calibration.json
│       │   └── charuco_calibration.xml
│       ├── pliki_debug/
│       │   └── charuco_001_m12_c15.jpg
│       └── raport_kalibracji.txt
│
├── nazwa_folderu_wynikow_YYYY-MM-DD_HH-MM-SS/
│   ├── kalibracja/
│   │   └── charuco_calibration.npz
│   ├── pomiar_1/
│   │   ├── out_annotated.mp4
│   │   ├── out_annotated_with_plot.mp4
│   │   ├── positions_px.csv
│   │   ├── deflection_y_px.png
│   │   └── deflection_y_cm.png
│   └── pomiar_2/
│       └── ...
│
└── patterns/
    └── charuco_4x6_40mm.jpg
```

## Rozwiązywanie problemów

### Kalibracja nie wykrywa wzorca
- Upewnij się, że wzorzec jest dobrze oświetlony
- Sprawdź czy wzorzec nie jest uszkodzony lub zamazany
- Spróbuj zmniejszyć frameskip
- Nagraj dłuższe wideo z większą liczbą kątów

### Za mało klatek do kalibracji
- Zmniejsz frameskip (np. z 15 na 5)
- Nagraj dłuższe wideo
- Upewnij się, że wzorzec jest widoczny przez większość czasu

### Pomiar nie wykrywa markera
- Sprawdź ID markera (domyślnie 2)
- Upewnij się, że marker jest z właściwego słownika (DICT_6X6_1000)
- Zwiększ kontrast i oświetlenie
- Zwiększ rozmiar markera

### Duży błąd RMS (> 2.0 px)
- Powtórz kalibrację z większą liczbą klatek
- Użyj dłuższego wideo z różnymi kątami
- Sprawdź jakość wydruku wzorca
- Upewnij się, że kamera była nieruchoma podczas nagrywania

## Parametry techniczne

### Wzorzec ChArUco
- Wymiary: 4×6 pól
- Rozmiar pola: 40 mm
- Rozmiar markera: 32 mm (80% pola)
- Słownik: DICT_6X6_1000
- Format wydruku: A4, 300 DPI

### Kalibracja
- Minimum rogów ChArUco: 4
- Minimum klatek: 5
- Zalecany frameskip: 10-15
- Metoda: cv2.calibrateCamera() z ChArUco

### Pomiary
- Marker ArUco: Domyślnie ID=2
- Słownik: DICT_6X6_1000
- Rozmiar markera: 34 mm (konfigurowalne w kodzie)
- Tryby śledzenia: ArUco → Lucas-Kanade → CSRT

## Wsparcie

W razie problemów:
1. Sprawdź logi w terminalu
2. Sprawdź pliki debug w folderze `pliki_debug/`
3. Sprawdź raport kalibracji w `raport_kalibracji.txt`

## Licencja

Copyright © 2024

