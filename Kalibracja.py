#!/usr/bin/env python3
"""
Kalibracja kamery z ChArUco - ŚCIŚLE według dokumentacji OpenCV 4.x
Dokumentacja: https://docs.opencv.org/4.x/df/d4a/tutorial_charuco_detection.html

Główne kroki (z dokumentacji):
1. Wykryj markery ARUCO (cv2.aruco.detectMarkers)
2. Interpoluj rogi ChArUco (CharucoDetector.detectBoard)
3. Kalibruj kamerę (cv2.aruco.calibrateCameraCharuco)
"""

import cv2
import numpy as np
import json
from pathlib import Path
import sys
import datetime
import shutil
import os

# ====== KONFIGURACJA (zgodna z generate_aruco_pattern.py) ======
SOURCE_VIDEO = "/Users/bartlomiejostasz/PYCH/nagrania/seria1/kalibracja6.MOV"

# Parametry planszy ChArUco
SQUARES_X = 4  # Liczba pól w poziomie
SQUARES_Y = 6  # Liczba pól w pionie
SQUARE_LENGTH = 0.040  # 40mm w metrach (dokumentacja zaleca metry!)
MARKER_LENGTH = 0.032  # 32mm w metrach (80% kwadratu)
DICT_NAME = cv2.aruco.DICT_6X6_1000
LEGACY_PATTERN = False  # OpenCV 4.12+ używa NOWEGO układu! (nie legacy)

# Wymagania kalibracji
MIN_CHARUCO_CORNERS = 4  # Minimum 4 rogi ChArUco (z dokumentacji)
MIN_FRAMES = 5  # Minimum 10 dobrych klatek

# Próbkowanie
FRAME_SKIP = 15  # Co 1 klatkę dla maksymalnej precyzji

# Output
OUTPUT_DIR = Path("calibration_opencv4x")
DEBUG_DIR = Path("debug_charuco")

# System serii
SERIES_BASE_DIR = Path("serie_kalibracji")


def get_next_series_number():
    """Znajdź następny numer serii"""
    if not SERIES_BASE_DIR.exists():
        return 1

    existing_series = []
    for item in SERIES_BASE_DIR.iterdir():
        if item.is_dir() and item.name.startswith("seria_"):
            try:
                num = int(item.name.split("_")[1])
                existing_series.append(num)
            except (ValueError, IndexError):
                continue

    return max(existing_series, default=0) + 1


def create_series_folder(series_num):
    """Utwórz folder dla nowej serii"""
    series_dir = SERIES_BASE_DIR / f"seria_{series_num:03d}"
    series_dir.mkdir(parents=True, exist_ok=True)
    return series_dir


def create_detailed_report(series_dir, video_path, calibration_results, detection_stats,
                           board_params, processing_params, output_files):
    """Utwórz szczegółowy raport tekstowy"""

    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    report_content = f"""
================================================================================
RAPORT KALIBRACJI KAMERY - ChArUco OpenCV 4.x
================================================================================

📅 DATA I CZAS: {timestamp}
🔢 NUMER SERII: {series_dir.name}

================================================================================
📹 INFORMACJE O NAGRANIU
================================================================================

Nazwa pliku: {Path(video_path).name}
Pełna ścieżka: {video_path}
Rozmiar pliku: {Path(video_path).stat().st_size / (1024 * 1024):.2f} MB
Data modyfikacji: {datetime.datetime.fromtimestamp(Path(video_path).stat().st_mtime).strftime('%Y-%m-%d %H:%M:%S')}

================================================================================
⚙️ PARAMETRY PLANSZY ChArUco
================================================================================

Wymiary planszy: {board_params['squares_x']} x {board_params['squares_y']} pól
Rozmiar pola: {board_params['square_length']} mm
Rozmiar markera: {board_params['marker_length']} mm
Słownik ARUCO: {board_params['dictionary']}
Tryb legacy: {board_params['legacy_pattern']}

================================================================================
🎬 PARAMETRY PRZETWARZANIA
================================================================================

Sampling klatek: co {processing_params['frame_skip']} klatek
Minimum rogów ChArUco: {processing_params['min_charuco_corners']}
Minimum klatek do kalibracji: {processing_params['min_frames']}
Preprocessing obrazu: {processing_params['preprocessing']}
Debug frames: {processing_params['save_debug_frames']}

================================================================================
📊 STATYSTYKI WYKRYWANIA
================================================================================

Całkowita liczba klatek w wideo: {detection_stats['total_frames']}
Przetworzonych klatek: {detection_stats['processed_frames']}
Klatek użytych do kalibracji: {detection_stats['used_frames']}
Łącznie wykrytych markerów ARUCO: {detection_stats['total_markers']}
Łącznie wykrytych rogów ChArUco: {detection_stats['total_corners']}
Średnio markerów na klatkę: {detection_stats['avg_markers_per_frame']:.1f}
Średnio rogów na klatkę: {detection_stats['avg_corners_per_frame']:.1f}

================================================================================
🎯 WYNIKI KALIBRACJI
================================================================================

RMS reprojection error: {calibration_results['rms_error']:.6f} pikseli

📷 MACIERZ KAMERY (K):
   fx (ogniskowa X): {calibration_results['camera_matrix'][0, 0]:.6f}
   fy (ogniskowa Y): {calibration_results['camera_matrix'][1, 1]:.6f}
   cx (centrum X): {calibration_results['camera_matrix'][0, 2]:.6f}
   cy (centrum Y): {calibration_results['camera_matrix'][1, 2]:.6f}

🔧 WSPÓŁCZYNNIKI DYSTORSJI (D):
   k1: {calibration_results['dist_coeffs'].flatten()[0]:.8f}
   k2: {calibration_results['dist_coeffs'].flatten()[1]:.8f}
   p1: {calibration_results['dist_coeffs'].flatten()[2]:.8f}
   p2: {calibration_results['dist_coeffs'].flatten()[3]:.8f}
   k3: {calibration_results['dist_coeffs'].flatten()[4]:.8f}
   k4: {calibration_results['dist_coeffs'].flatten()[5]:.8f}
   k5: {calibration_results['dist_coeffs'].flatten()[6]:.8f}
   k6: {calibration_results['dist_coeffs'].flatten()[7]:.8f}
   s1: {calibration_results['dist_coeffs'].flatten()[8]:.8f}
   s2: {calibration_results['dist_coeffs'].flatten()[9]:.8f}
   s3: {calibration_results['dist_coeffs'].flatten()[10]:.8f}
   s4: {calibration_results['dist_coeffs'].flatten()[11]:.8f}

📐 ROZMIAR OBRAZU:
   Szerokość: {calibration_results['image_size'][0]} pikseli
   Wysokość: {calibration_results['image_size'][1]} pikseli

================================================================================
💾 PLIKI WYGENEROWANE
================================================================================

Pliki kalibracji:
{chr(10).join([f"  📄 {file}" for file in output_files['calibration_files']])}

Pliki debug:
{chr(10).join([f"  🖼️  {file}" for file in output_files['debug_files']])}

Pliki serii:
{chr(10).join([f"  📁 {file}" for file in output_files['series_files']])}

================================================================================
📈 OCENA JAKOŚCI KALIBRACJI
================================================================================

RMS Error: {calibration_results['rms_error']:.6f} pikseli
"""

    # Ocena jakości
    if calibration_results['rms_error'] < 0.5:
        report_content += "✅ DOSKONAŁA jakość kalibracji (< 0.5 pix)\n"
    elif calibration_results['rms_error'] < 1.0:
        report_content += "✅ BARDZO DOBRA jakość kalibracji (< 1.0 pix)\n"
    elif calibration_results['rms_error'] < 2.0:
        report_content += "⚠️  DOBRA jakość kalibracji (< 2.0 pix)\n"
    else:
        report_content += "❌ SŁABA jakość kalibracji (> 2.0 pix)\n"

    report_content += f"""
Liczba klatek: {detection_stats['used_frames']} (minimum: {processing_params['min_frames']})
✅ {'Wystarczająca' if detection_stats['used_frames'] >= processing_params['min_frames'] else 'Niewystarczająca'} liczba klatek

================================================================================
🔧 INFORMACJE TECHNICZNE
================================================================================

Wersja OpenCV: {cv2.__version__}
API użyte: CharucoDetector + cv2.calibrateCamera()
Metoda kalibracji: ChArUco Boards (OpenCV 4.12+)
Flagi kalibracji: CALIB_RATIONAL_MODEL | CALIB_FIX_K3 | CALIB_FIX_K4 | CALIB_FIX_K5

================================================================================
📝 UWAGI I REKOMENDACJE
================================================================================

1. RMS error {calibration_results['rms_error']:.6f} pikseli {'jest doskonały' if calibration_results['rms_error'] < 0.5 else 'jest dobry' if calibration_results['rms_error'] < 1.0 else 'może być lepszy'}
2. Użyto {detection_stats['used_frames']} klatek z {detection_stats['total_frames']} dostępnych
3. Średnio {detection_stats['avg_corners_per_frame']:.1f} rogów ChArUco na klatkę
4. {'✅' if detection_stats['used_frames'] >= processing_params['min_frames'] else '❌'} Liczba klatek {'wystarczająca' if detection_stats['used_frames'] >= processing_params['min_frames'] else 'niewystarczająca'} do kalibracji

================================================================================
KONIEC RAPORTU
================================================================================
"""

    # Zapisz raport
    report_path = series_dir / "raport_kalibracji.txt"
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report_content)

    return report_path


def copy_files_to_series(series_dir, calibration_dir, debug_dir):
    """Skopiuj wszystkie wygenerowane pliki do folderu serii"""
    copied_files = []

    # Skopiuj pliki kalibracji
    if calibration_dir.exists():
        calib_dest = series_dir / "pliki_kalibracji"
        calib_dest.mkdir(exist_ok=True)
        for file in calibration_dir.iterdir():
            if file.is_file():
                shutil.copy2(file, calib_dest)
                copied_files.append(f"pliki_kalibracji/{file.name}")

    # Skopiuj pliki debug
    if debug_dir.exists():
        debug_dest = series_dir / "pliki_debug"
        debug_dest.mkdir(exist_ok=True)
        for file in debug_dir.iterdir():
            if file.is_file():
                shutil.copy2(file, debug_dest)
                copied_files.append(f"pliki_debug/{file.name}")

    return copied_files


def create_charuco_board():
    """
    Tworzy obiekt CharucoBoard zgodnie z dokumentacją OpenCV 4.x
    Dokumentacja: https://docs.opencv.org/4.x/df/d4a/tutorial_charuco_detection.html#autotoc_md2561
    """
    dictionary = cv2.aruco.getPredefinedDictionary(DICT_NAME)

    # CharucoBoard(Size(squaresX, squaresY), squareLength, markerLength, dictionary)
    board = cv2.aruco.CharucoBoard(
        (SQUARES_X, SQUARES_Y),
        SQUARE_LENGTH,
        MARKER_LENGTH,
        dictionary
    )

    print(f"✓ Utworzono CharucoBoard: {SQUARES_X}x{SQUARES_Y}, square={SQUARE_LENGTH}m, marker={MARKER_LENGTH}m")
    return board


def create_charuco_detector(board):
    """
    Tworzy CharucoDetector zgodnie z dokumentacją OpenCV 4.x
    Dokumentacja: https://docs.opencv.org/4.x/df/d4a/tutorial_charuco_detection.html#autotoc_md2561

    CharucoParameters:
    - tryRefineMarkers: refineDetectedMarkers() będzie użyty w detectBoard()
    - cameraMatrix: może być użyta w detectBoard() (None dla kalibracji)
    - distCoeffs: mogą być użyte w detectBoard() (None dla kalibracji)
    """
    # DetectorParameters - domyślne wartości
    detector_params = cv2.aruco.DetectorParameters()

    # CharucoParameters
    charuco_params = cv2.aruco.CharucoParameters()
    charuco_params.tryRefineMarkers = True  # Włącz refinement markerów
    # cameraMatrix i distCoeffs pozostawiamy None (kalibracja)

    # Utwórz CharucoDetector
    detector = cv2.aruco.CharucoDetector(board, charuco_params, detector_params)

    print(f"✓ Utworzono CharucoDetector (tryRefineMarkers=True)")
    return detector


def detect_charuco_corners(detector, image):
    """
    Wykrywa rogi ChArUco zgodnie z dokumentacją
    Dokumentacja: https://docs.opencv.org/4.x/df/d4a/tutorial_charuco_detection.html#autotoc_md2564

    UWAGA: CharucoDetector.detectBoard() może nie działać w niektórych wersjach!
    Używamy starszego API interpolateCornersCharuco() jako fallback.

    Returns:
        charuco_corners, charuco_ids, marker_corners, marker_ids
    """
    # Spróbuj nowego API (CharucoDetector)
    try:
        charuco_corners, charuco_ids, marker_corners, marker_ids = detector.detectBoard(image)

        # Jeśli znaleziono markery ale 0 rogów, spróbuj starego API
        if marker_ids is not None and len(marker_ids) > 0 and (charuco_corners is None or len(charuco_corners) == 0):
            # Fallback: użyj starego API
            raise RuntimeError("detectBoard() zwróciło 0 rogów - spróbuj interpolateCornersCharuco()")

        return charuco_corners, charuco_ids, marker_corners, marker_ids

    except Exception as e:
        # Fallback: stare API (OpenCV < 4.7)
        # (debug wyłączony - zbyt dużo outputu)

        # Najpierw wykryj markery ARUCO
        aruco_detector = cv2.aruco.ArucoDetector(
            detector.getBoard().getDictionary(),
            cv2.aruco.DetectorParameters()
        )
        marker_corners, marker_ids, rejected = aruco_detector.detectMarkers(image)

        if marker_ids is None or len(marker_ids) == 0:
            return None, None, None, None

        # Interpoluj rogi ChArUco używając starego API
        if hasattr(cv2.aruco, 'interpolateCornersCharuco'):
            result = cv2.aruco.interpolateCornersCharuco(
                marker_corners, marker_ids, image, detector.getBoard(),
                cameraMatrix=None,
                distCoeffs=None
            )

            # Rozpakuj wynik (może być 2 lub 3 elementy)
            if len(result) == 3:
                num_corners, charuco_corners, charuco_ids = result
            elif len(result) == 2:
                charuco_corners, charuco_ids = result
            else:
                charuco_corners, charuco_ids = None, None

            return charuco_corners, charuco_ids, marker_corners, marker_ids

        # Jeśli nic nie działa, zwróć None
        return None, None, marker_corners, marker_ids


def calibrate_camera_charuco(all_charuco_corners, all_charuco_ids, board, image_size):
    """
    Kalibracja kamery używając rogów ChArUco - OpenCV 4.12+ (NOWE API)

    W OpenCV 4.12+ NIE MA calibrateCameraCharuco()!
    Musimy użyć cv2.calibrateCamera() z rogami ChArUco jako punktami.
    """
    print("\n" + "=" * 60)
    print("KALIBRACJA KAMERY - METODA ChArUco (OpenCV 4.12+ API)")
    print("=" * 60)

    # Przygotuj punkty 3D i 2D dla cv2.calibrateCamera()
    obj_points = []
    img_points = []

    # Pobierz pozycje 3D rogów szachownicy z board
    all_obj_pts_3d = board.getChessboardCorners()

    for charuco_corners, charuco_ids in zip(all_charuco_corners, all_charuco_ids):
        if charuco_corners is None or charuco_ids is None:
            continue

        # Dla każdego roga ChArUco, znajdź odpowiadający mu punkt 3D
        frame_obj_pts = []
        frame_img_pts = []

        for i, corner_id in enumerate(charuco_ids.flatten()):
            # Punkt 3D z board (używając corner_id jako indeksu)
            if corner_id < len(all_obj_pts_3d):
                frame_obj_pts.append(all_obj_pts_3d[corner_id])
                # Punkt 2D z obrazu
                frame_img_pts.append(charuco_corners[i])

        if len(frame_obj_pts) > 0:
            obj_points.append(np.array(frame_obj_pts, dtype=np.float32))
            img_points.append(np.array(frame_img_pts, dtype=np.float32).reshape(-1, 1, 2))

    # Kalibracja używając cv2.calibrateCamera()
    calib_flags = (
            cv2.CALIB_RATIONAL_MODEL |
            cv2.CALIB_FIX_K3 |
            cv2.CALIB_FIX_K4 |
            cv2.CALIB_FIX_K5
    )

    print(f"Używam: cv2.calibrateCamera() z {len(obj_points)} klatkami rogów ChArUco")

    ret, camera_matrix, dist_coeffs, rvecs, tvecs = cv2.calibrateCamera(
        obj_points,
        img_points,
        image_size,
        None,
        None,
        flags=calib_flags
    )

    print(f"\n🎯 SUKCES! RMS error: {ret:.6f} pikseli")
    return ret, camera_matrix, dist_coeffs, rvecs, tvecs


def save_calibration_results(camera_matrix, dist_coeffs, rms_error, image_size):
    """Zapisz wyniki kalibracji"""
    OUTPUT_DIR.mkdir(exist_ok=True)

    # NPZ (numpy)
    npz_path = OUTPUT_DIR / "charuco_calibration.npz"
    np.savez(
        npz_path,
        camera_matrix=camera_matrix,
        dist_coeffs=dist_coeffs,
        rms_error=rms_error,
        image_size=image_size,
        square_length=SQUARE_LENGTH,
        marker_length=MARKER_LENGTH
    )

    # JSON (czytelny)
    json_path = OUTPUT_DIR / "charuco_calibration.json"
    with open(json_path, 'w') as f:
        json.dump({
            "rms_error": float(rms_error),
            "camera_matrix": camera_matrix.tolist(),
            "dist_coeffs": dist_coeffs.flatten().tolist(),
            "image_size": image_size,
            "square_length_m": SQUARE_LENGTH,
            "marker_length_m": MARKER_LENGTH,
            "board_size": [SQUARES_X, SQUARES_Y]
        }, f, indent=2)

    # OpenCV XML
    xml_path = OUTPUT_DIR / "charuco_calibration.xml"
    fs = cv2.FileStorage(str(xml_path), cv2.FILE_STORAGE_WRITE)
    fs.write("camera_matrix", camera_matrix)
    fs.write("dist_coeffs", dist_coeffs)
    fs.write("rms_error", rms_error)
    fs.write("image_width", image_size[0])
    fs.write("image_height", image_size[1])
    fs.release()


def main():
    """Główna funkcja kalibracji z systemem serii"""
    print("=" * 60)
    print("KALIBRACJA KAMERY - ChArUco OpenCV 4.x")
    print("Dokumentacja: https://docs.opencv.org/4.x/df/d4a/tutorial_charuco_detection.html")
    print("=" * 60)

    # Utwórz folder dla nowej serii
    series_num = get_next_series_number()
    series_dir = create_series_folder(series_num)
    print(f"📁 Utworzono folder serii: {series_dir}")

    # 1. Utwórz planszę ChArUco
    board = create_charuco_board()
    print(f"✓ Utworzono CharucoBoard: {SQUARES_X}x{SQUARES_Y}, square={SQUARE_LENGTH}m, marker={MARKER_LENGTH}m")

    # 2. Utwórz detektor ChArUco
    detector = create_charuco_detector(board)
    print("✓ Utworzono CharucoDetector (tryRefineMarkers=True)")

    # 3. Otwórz wideo
    video_path = Path(SOURCE_VIDEO)
    if not video_path.exists():
        sys.exit(f"❌ Plik wideo nie istnieje: {video_path}")

    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        sys.exit(f"❌ Nie można otworzyć wideo: {video_path}")

    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    print(f"\n📹 Wideo: {video_path.name}")
    print(f"   Klatek: {total_frames}")
    print(f"   Sampling: co {FRAME_SKIP} klatek")
    print(f"   Minimum rogów ChArUco: {MIN_CHARUCO_CORNERS}")

    # Przygotuj katalogi
    DEBUG_DIR.mkdir(exist_ok=True)

    # Kolekcja danych kalibracyjnych
    all_charuco_corners = []
    all_charuco_ids = []
    image_size = None

    frame_idx = 0
    used_frames = 0
    total_markers = 0
    total_corners = 0

    print(f"\n🔍 Wykrywanie rogów ChArUco...")
    print("-" * 60)

    # 4. Przetwarzaj klatki
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame_idx += 1

        # Próbkowanie
        if frame_idx % FRAME_SKIP != 0:
            continue

        # Konwersja do grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        if image_size is None:
            image_size = gray.shape[::-1]

        # 5. Wykryj rogi ChArUco (KLUCZOWE!)
        charuco_corners, charuco_ids, marker_corners, marker_ids = detect_charuco_corners(detector, gray)

        # Policz wykryte elementy
        num_markers = len(marker_ids) if marker_ids is not None else 0
        num_corners = len(charuco_corners) if charuco_corners is not None else 0

        # 6. Sprawdź czy znaleziono wystarczająco rogów
        if charuco_corners is not None and charuco_ids is not None and len(charuco_corners) >= MIN_CHARUCO_CORNERS:
            all_charuco_corners.append(charuco_corners)
            all_charuco_ids.append(charuco_ids)
            used_frames += 1

            num_markers = len(marker_ids) if marker_ids is not None else 0
            num_corners = len(charuco_corners)
            total_markers += num_markers
            total_corners += num_corners

            # Debug output
            if used_frames == 1 or used_frames % 5 == 0:
                print(f"✓ Klatka {frame_idx}: {num_markers} markerów → {num_corners} rogów ChArUco")

            # Zapisz debug frame (pierwsze 10)
            if used_frames <= 10:
                debug_frame = frame.copy()

                # Rysuj markery
                if marker_corners is not None and marker_ids is not None:
                    cv2.aruco.drawDetectedMarkers(debug_frame, marker_corners, marker_ids)

                # Rysuj rogi ChArUco (zielone)
                cv2.aruco.drawDetectedCornersCharuco(debug_frame, charuco_corners, charuco_ids, (0, 255, 0))

                cv2.imwrite(
                    str(DEBUG_DIR / f"charuco_{used_frames:03d}_m{num_markers}_c{num_corners}.jpg"),
                    debug_frame
                )

        # Progress
        if frame_idx % (FRAME_SKIP * 10) == 0:
            progress = (frame_idx / total_frames) * 100
            print(f"Progress: {frame_idx}/{total_frames} ({progress:.1f}%) | Użytych: {used_frames}")

    cap.release()

    # 7. Podsumowanie wykrywania
    print("-" * 60)
    print(f"\n📊 Wyniki wykrywania:")
    print(f"   Przetworzonych klatek: {frame_idx}")
    print(f"   Użytych klatek: {used_frames}")
    print(f"   Łącznie markerów: {total_markers}")
    print(f"   Łącznie rogów ChArUco: {total_corners}")
    print(f"   Średnio rogów/klatkę: {total_corners / used_frames if used_frames > 0 else 0:.1f}")

    # 8. Sprawdź czy mamy wystarczająco danych
    if used_frames < MIN_FRAMES:
        sys.exit(f"\n❌ Za mało dobrych klatek! Potrzeba min. {MIN_FRAMES}, znaleziono {used_frames}")

    # 9. KALIBRACJA
    rms, camera_matrix, dist_coeffs, rvecs, tvecs = calibrate_camera_charuco(
        all_charuco_corners,
        all_charuco_ids,
        board,
        image_size
    )

    # 10. Wyświetl wyniki
    print(f"\n📷 Macierz kamery (K):")
    print(f"   fx = {camera_matrix[0, 0]:.2f}")
    print(f"   fy = {camera_matrix[1, 1]:.2f}")
    print(f"   cx = {camera_matrix[0, 2]:.2f}")
    print(f"   cy = {camera_matrix[1, 2]:.2f}")

    print(f"\n🔧 Współczynniki dystorsji (D):")
    print(f"   {dist_coeffs.flatten()}")

    # 11. Zapisz wyniki
    save_calibration_results(camera_matrix, dist_coeffs, rms, image_size)

    print(f"\n💾 Zapisano wyniki:")
    print(f"  {OUTPUT_DIR}/charuco_calibration.npz")
    print(f"  {OUTPUT_DIR}/charuco_calibration.json")
    print(f"  {OUTPUT_DIR}/charuco_calibration.xml")

    # Przygotuj dane dla raportu
    calibration_results = {
        'rms_error': rms,
        'camera_matrix': camera_matrix,
        'dist_coeffs': dist_coeffs,
        'image_size': image_size
    }

    detection_stats = {
        'total_frames': total_frames,
        'processed_frames': frame_idx,
        'used_frames': used_frames,
        'total_markers': total_markers,
        'total_corners': total_corners,
        'avg_markers_per_frame': total_markers / used_frames if used_frames > 0 else 0,
        'avg_corners_per_frame': total_corners / used_frames if used_frames > 0 else 0
    }

    board_params = {
        'squares_x': SQUARES_X,
        'squares_y': SQUARES_Y,
        'square_length': SQUARE_LENGTH * 1000,  # konwersja na mm
        'marker_length': MARKER_LENGTH * 1000,  # konwersja na mm
        'dictionary': DICT_NAME,
        'legacy_pattern': LEGACY_PATTERN
    }

    processing_params = {
        'frame_skip': FRAME_SKIP,
        'min_charuco_corners': MIN_CHARUCO_CORNERS,
        'min_frames': MIN_FRAMES,
        'preprocessing': 'CLAHE + Bilateral + Sharpening',
        'save_debug_frames': True
    }

    # Skopiuj pliki do folderu serii
    series_files = copy_files_to_series(series_dir, OUTPUT_DIR, DEBUG_DIR)

    # Przygotuj listę plików
    output_files = {
        'calibration_files': [
            f"{OUTPUT_DIR}/charuco_calibration.npz",
            f"{OUTPUT_DIR}/charuco_calibration.json",
            f"{OUTPUT_DIR}/charuco_calibration.xml"
        ],
        'debug_files': [
            f"{DEBUG_DIR}/charuco_{i:03d}_m{total_markers // used_frames if used_frames > 0 else 0}_c{total_corners // used_frames if used_frames > 0 else 0}.jpg"
            for i in range(1, min(11, used_frames + 1))],
        'series_files': series_files
    }

    # Utwórz szczegółowy raport
    report_path = create_detailed_report(
        series_dir, SOURCE_VIDEO, calibration_results, detection_stats,
        board_params, processing_params, output_files
    )

    print(f"\n📋 Utworzono szczegółowy raport:")
    print(f"  {report_path}")

    print(f"\n📁 Folder serii: {series_dir}")
    print(f"   📄 raport_kalibracji.txt")
    print(f"   📁 pliki_kalibracji/")
    print(f"   📁 pliki_debug/")

    print("\n" + "=" * 60)
    print("✅ KALIBRACJA ZAKOŃCZONA SUKCESEM!")
    print("=" * 60)

    print(f"\nDebug frames: {DEBUG_DIR}/")
    print(f"Wyniki: {OUTPUT_DIR}/")
    print(f"Serie: {SERIES_BASE_DIR}/")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Przerwano przez użytkownika")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ BŁĄD: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)

