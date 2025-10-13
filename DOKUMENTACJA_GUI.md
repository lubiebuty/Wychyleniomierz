# Wychyleniomierz - Dokumentacja Systemu GUI

## Przegląd

System Wychyleniomierz to zaawansowana aplikacja z interfejsem graficznym Gradio do kalibracji kamer i pomiaru wychyleń obiektów za pomocą markerów ArUco/ChArUco.

## Utworzone pliki

### 1. `GUI_Wychyleniomierz.py`
Główny plik aplikacji GUI zawierający:
- Interfejs użytkownika Gradio
- Logikę przetwarzania kalibracji
- Integrację z modułami:
  - `Generowanie_wzorca.py` - generowanie wzorców ChArUco
  - `Kalibracja.py` - kalibracja kamery
  - `Wychyleniomierz.py` - pomiar wychyleń

### 2. `requirements.txt`
Lista zależności potrzebnych do uruchomienia aplikacji:
- gradio >= 4.0.0
- opencv-contrib-python >= 4.8.0
- numpy >= 1.24.0
- matplotlib >= 3.7.0
- pandas >= 2.0.0
- pillow >= 10.0.0

### 3. `README_GUI.md`
Szczegółowa instrukcja użytkowania aplikacji zawierająca:
- Kroki instalacji
- Przewodnik krok po kroku dla użytkownika
- Opis struktury folderów
- Rozwiązywanie problemów
- Parametry techniczne

### 4. `start_gui.sh`
Skrypt uruchamiający aplikację:
```bash
./start_gui.sh
```

## Architektura aplikacji

### Przepływ pracy

#### Okno 1: Kalibracja

```
┌─────────────────────────────────────┐
│ 1. Generuj/Pobierz wzorzec ChArUco │
└────────────┬────────────────────────┘
             │
             v
┌─────────────────────────────────────┐
│ 2. Opcja A: Wgraj plik .npz         │
│    Opcja B: Nagraj wideo kalibracji│
└────────────┬────────────────────────┘
             │
             v (Opcja B)
┌─────────────────────────────────────┐
│ 3. Ustaw parametry:                 │
│    - Nazwa serii                    │
│    - Frameskip (1-30)               │
└────────────┬────────────────────────┘
             │
             v
┌─────────────────────────────────────┐
│ 4. Wykonaj kalibrację               │
│    - Wykrywanie rogów ChArUco       │
│    - Obliczanie macierzy kamery     │
│    - Generowanie raportu            │
└────────────┬────────────────────────┘
             │
             v
┌─────────────────────────────────────┐
│ 5. Raport kalibracji                │
│    - RMS error                      │
│    - Macierz kamery                 │
│    - Współczynniki dystorsji        │
└────────────┬────────────────────────┘
             │
       ┌─────┴─────┐
       │           │
       v           v
  Powtórz?      Akceptuj
       │           │
       └───────────┘
                   │
                   v
┌─────────────────────────────────────┐
│ 6. Utwórz folder na wyniki          │
│    - Kopiuj plik kalibracji         │
└─────────────────────────────────────┘
```

#### Okno 2: Pomiary

```
┌─────────────────────────────────────┐
│ 1. Wgraj wideo pomiaru              │
└────────────┬────────────────────────┘
             │
             v
┌─────────────────────────────────────┐
│ 2. Podaj nazwę pomiaru              │
└────────────┬────────────────────────┘
             │
             v
┌─────────────────────────────────────┐
│ 3. Wykonaj pomiar                   │
│    - Wykrywanie markera ArUco       │
│    - Śledzenie ruchu                │
│    - Obliczanie wychyleń            │
└────────────┬────────────────────────┘
             │
             v
┌─────────────────────────────────────┐
│ 4. Zapisz wyniki:                   │
│    - Wideo z adnotacjami            │
│    - Wideo z wykresem               │
│    - CSV z danymi                   │
│    - Wykresy PNG                    │
└────────────┬────────────────────────┘
             │
             v
       Kolejny pomiar?
             │
             └─────> TAK: powrót do kroku 1
                     NIE: zakończenie
```

### Klasa WychyleniomierzGUI

```python
class WychyleniomierzGUI:
    def __init__(self):
        self.calibration_file_path = None
        self.calibration_folder = None
        self.results_base_folder = None
        self.current_calibration_report = None
    
    # Metody kalibracji
    def download_pattern()
    def validate_npz_file()
    def process_calibration_video()
    def run_calibration()
    
    # Metody pomiarów
    def create_results_folder()
    def process_measurement_video()
    def run_measurement()
    
    # Budowa interfejsu
    def build_interface()
```

## Kluczowe funkcjonalności

### 1. Generowanie wzorca kalibracyjnego
- Tworzy wzorzec ChArUco 4x6 pól
- Rozmiar pola: 40mm
- Rozmiar markera: 32mm
- Format: JPG, 300 DPI na A4
- Dodany pasek skali 100mm

### 2. Kalibracja kamery
- Wykrywanie markerów ArUco
- Interpolacja rogów ChArUco
- Obliczanie macierzy kamery i współczynników dystorsji
- Generowanie szczegółowego raportu
- Zapisywanie w formatach: .npz, .json, .xml
- Tworzenie obrazów debug z wykrytymi markerami

### 3. Pomiar wychyleń
- Wykrywanie markera ArUco (domyślnie ID=2)
- Śledzenie 3-poziomowe: ArUco → Lucas-Kanade → CSRT
- Undistortion obrazu
- Obliczanie pozycji w pikselach i centymetrach
- Generowanie:
  - Wideo z adnotacjami
  - Wideo z wykresem wychyleń w czasie rzeczywistym
  - CSV z danymi pozycji
  - Wykresy wychyleń (px i cm)

## Struktura danych wyjściowych

```
Wychyleniomierz/
├── venv/                           # Środowisko wirtualne
├── patterns/                       # Wzorce kalibracyjne
│   └── charuco_4x6_40mm.jpg
├── serie_kalibracji/               # Wyniki kalibracji
│   └── [nazwa]_[data_czas]/
│       ├── pliki_kalibracji/
│       │   ├── charuco_calibration.npz
│       │   ├── charuco_calibration.json
│       │   └── charuco_calibration.xml
│       ├── pliki_debug/
│       │   └── charuco_*.jpg
│       └── raport_kalibracji.txt
└── [nazwa_folderu]_[data_czas]/   # Wyniki pomiarów
    ├── kalibracja/
    │   └── charuco_calibration.npz
    ├── [pomiar_1]/
    │   ├── out_annotated.mp4
    │   ├── out_annotated_with_plot.mp4
    │   ├── positions_px.csv
    │   ├── deflection_y_px.png
    │   └── deflection_y_cm.png
    └── [pomiar_2]/
        └── ...
```

## Parametry konfigurowalne

### Kalibracja (GUI)
- `series_name`: Nazwa serii kalibracyjnej
- `frameskip`: Co ile klatek analizować (1-30)

### Kalibracja (kod - Kalibracja.py)
- `SQUARES_X = 4`: Pola w poziomie
- `SQUARES_Y = 6`: Pola w pionie
- `SQUARE_LENGTH = 0.040`: Rozmiar pola (m)
- `MARKER_LENGTH = 0.032`: Rozmiar markera (m)
- `MIN_CHARUCO_CORNERS = 4`: Min. rogów do akceptacji
- `MIN_FRAMES = 5`: Min. klatek do kalibracji

### Pomiary (kod - Wychyleniomierz.py)
- `MARKER_ID = 2`: ID markera ArUco
- `MARKER_LEN_M = 0.034`: Rozmiar markera (m)
- `ARUCO_DICT = "DICT_6X6_1000"`: Słownik ArUco
- `LOCK_PLANE_DISTANCE_M = 3.0`: Stała odległość płaszczyzny (m)
- `EMBED_PLOT_IN_VIDEO = True`: Generuj wideo z wykresem
- `PLOT_UNIT_CM = True`: Wykres w cm (False = px)

## Algorytmy śledzenia

### 1. Detekcja ArUco (priorytet najwyższy)
- Pełnokadrowa w wielu skalach
- Re-detekcja w ROI wokół ostatniej pozycji
- Refinement narożników (subpikselowy)

### 2. Lucas-Kanade Optical Flow (fallback)
- Śledzenie 4 narożników markera
- Forward-backward check
- Gating na krok ruchu
- Rekonstrukcja affiniczna brakującego narożnika

### 3. CSRT Tracker (ostateczny fallback)
- Śledzenie całego bboxa
- Aktywowany po utracie ArUco i LK

### 4. ROI "Blue Box"
- Okno poszukiwań wokół ostatniej pozycji
- Rozszerzanie po nieudanej detekcji
- Kotwica pełnokadrowa co N klatek

## Wskaźniki jakości

### Kalibracja
- **DOSKONAŁA**: RMS < 0.5 px
- **BARDZO DOBRA**: RMS < 1.0 px
- **DOBRA**: RMS < 2.0 px
- **SŁABA**: RMS > 2.0 px (powtórz)

### Pomiary
- Ciągłość śledzenia: % klatek z wykrytym markerem
- Płynność ruchu: brak dużych skoków pozycji
- Zgodność źródeł: ArUco > LK > CSRT

## Instrukcja uruchomienia

### Pierwsze uruchomienie

```bash
# 1. Przejdź do folderu projektu
cd /Users/bartlomiejostasz/PYCH/Wychyleniomierz

# 2. Utwórz środowisko wirtualne
python3 -m venv venv

# 3. Aktywuj środowisko
source venv/bin/activate

# 4. Zainstaluj zależności
pip install -r requirements.txt

# 5. Uruchom GUI
python3 GUI_Wychyleniomierz.py
```

### Kolejne uruchomienia

```bash
./start_gui.sh
```

lub

```bash
source venv/bin/activate
python3 GUI_Wychyleniomierz.py
```

## API Gradio

### Komponenty UI

#### Okno Kalibracji
- `gr.Button`: Pobierz wzorzec, Rozpocznij kalibrację
- `gr.File`: Upload plików .npz i video
- `gr.Textbox`: Nazwa serii, Raport
- `gr.Slider`: Frameskip (1-30)
- `gr.Markdown`: Instrukcje i informacje

#### Okno Pomiarów
- `gr.File`: Upload video pomiaru
- `gr.Textbox`: Nazwa pomiaru, Wyniki
- `gr.Button`: Rozpocznij pomiar, Następny pomiar

### Callbacki

```python
# Pobierz wzorzec
btn_download_pattern.click(
    fn=self.download_pattern,
    inputs=[],
    outputs=[pattern_output, pattern_status]
)

# Walidacja .npz
upload_calib_file.change(
    fn=self.validate_npz_file,
    inputs=[upload_calib_file],
    outputs=[upload_calib_file, calib_file_status]
)

# Kalibracja
btn_start_calibration.click(
    fn=self.process_calibration_video,
    inputs=[upload_calib_video, series_name_input, frameskip_input],
    outputs=[calibration_report, calib_video_status]
)

# Pomiar
btn_start_measurement.click(
    fn=self.process_measurement_video,
    inputs=[upload_measurement_video, measurement_name_input],
    outputs=[measurement_results, measurement_name_input]
)
```

## Bezpieczeństwo i walidacja

### Walidacja plików
- Wymuszenie rozszerzenia `.npz` dla plików kalibracji
- Sprawdzanie formatu wideo (`.mp4`, `.mov`, `.avi`)
- Weryfikacja istnienia plików kalibracji przed pomiarem

### Obsługa błędów
- Try-catch w kluczowych operacjach
- Komunikaty błędów dla użytkownika
- Przywracanie oryginalnych parametrów modułów

### Struktura folderów
- Automatyczne tworzenie folderów z timestamp
- Unikanie kolizji nazw
- Organizacja wyników w hierarchii

## Optymalizacja wydajności

### Kalibracja
- Frameskip redukuje liczbę przetwarzanych klatek
- Preprocessing ROI (CLAHE, wyostrzenie)
- Pamięć tylko pierwszych 10 obrazów debug

### Pomiary
- Undistortion z precomputed maps
- ROI search zamiast pełnokadrowego
- Fallback na szybsze trackery
- Zapisywanie tylko istotnych klatek

## Rozszerzalność

### Dodawanie nowych funkcji
1. Dodaj metodę do klasy `WychyleniomierzGUI`
2. Utwórz komponenty UI w `build_interface()`
3. Połącz callback
4. Przetestuj workflow

### Modyfikacja parametrów
- GUI: Edytuj `build_interface()` dla nowych kontrolek
- Backend: Modyfikuj stałe w modułach źródłowych
- Dokumentacja: Zaktualizuj README_GUI.md

## Znane ograniczenia

1. **Gradio File Dialog**: Brak natywnego dialogu wyboru folderu
   - Obejście: Użytkownik podaje nazwę, system tworzy folder
   
2. **Długi czas kalibracji**: Zależny od długości wideo
   - Optymalizacja: Zwiększ frameskip (trade-off: dokładność)
   
3. **Brak podglądu na żywo**: Offline processing
   - Przyszłość: Dodać progress bar z Gradio
   
4. **Jeden marker**: Domyślnie ID=2
   - Rozwiązanie: Dodaj pole wyboru ID markera w GUI

## Wsparcie i rozwój

### Logowanie
- Terminal output dla diagnostyki
- Pliki debug w `pliki_debug/`
- Raport kalibracji w `raport_kalibracji.txt`

### Testowanie
- Test generowania wzorca
- Test kalibracji z próbnym wideo
- Test pomiaru z przykładowym wideo
- Weryfikacja jakości RMS < 1.0 px

### Przyszłe funkcje
- [ ] Progress bar dla długich operacji
- [ ] Wybór ID markera w GUI
- [ ] Batch processing wielu pomiarów
- [ ] Eksport do różnych formatów
- [ ] Porównanie wielu pomiarów na jednym wykresie
- [ ] Live preview z kamery
- [ ] Multi-marker tracking
- [ ] Analiza częstotliwościowa

## Kontakt i licencja

Copyright © 2024
System opracowany dla potrzeb pomiarów wychyleń konstrukcji.

---

**Wersja**: 1.0.0  
**Data**: 2024-10-13  
**Autor**: System Wychyleniomierz  
**Python**: >= 3.8  
**OpenCV**: >= 4.8.0  
**Gradio**: >= 4.0.0

