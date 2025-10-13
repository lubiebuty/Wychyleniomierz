#!/usr/bin/env python3
"""
Gradio GUI dla Wychyleniomierza (Inclinometer)
Interfejs graficzny do śledzenia markerów ArUco
"""

import gradio as gr
import cv2
import numpy as np
import pandas as pd
from pathlib import Path
import tempfile
import shutil
import os
from datetime import datetime
import matplotlib.pyplot as plt
from typing import Optional, Tuple, Dict, Any
import json

# Import głównej klasy trackera
from Wychyleniomierz import ArucoTracker, ARUCO_DICTS, _make_output_dir

# Stałe dla GUI
DEFAULT_MARKER_SIZE = 0.034  # 3.4 cm
DEFAULT_LOCK_DISTANCE = 3.0  # 3 metry

def load_calibration_file(calib_file):
    """Ładuje plik kalibracyjny kamery"""
    if calib_file is None:
        return None, None, "❌ Brak pliku kalibracyjnego"
    
    try:
        with np.load(calib_file.name) as calib:
            K = calib["camera_matrix"]
            D = calib["dist_coeffs"]
        return K, D, f"✅ Załadowano kalibrację: K shape={K.shape}, D shape={D.shape}"
    except Exception as e:
        return None, None, f"❌ Błąd ładowania kalibracji: {str(e)}"

def get_video_info(video_path):
    """Pobiera informacje o wideo"""
    if video_path is None:
        return "Brak wideo"
    
    try:
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            return "❌ Nie można otworzyć wideo"
        
        fps = cap.get(cv2.CAP_PROP_FPS)
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        duration = frame_count / fps if fps > 0 else 0
        
        cap.release()
        
        return f"""
📹 **Informacje o wideo:**
- Rozdzielczość: {width}x{height}
- FPS: {fps:.2f}
- Liczba klatek: {frame_count}
- Czas trwania: {duration:.2f}s
"""
    except Exception as e:
        return f"❌ Błąd odczytu wideo: {str(e)}"

def get_first_frame_with_aruco(video_path, dict_name, marker_id):
    """Pobiera pierwszą klatkę z zaznaczonym markerem ArUco"""
    if video_path is None:
        return None
    
    try:
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            return None
        
        # Przygotuj detektor ArUco
        aruco_dict = cv2.aruco.getPredefinedDictionary(ARUCO_DICTS[dict_name])
        
        if hasattr(cv2.aruco, "ArucoDetector"):
            params = cv2.aruco.DetectorParameters()
            detector = cv2.aruco.ArucoDetector(aruco_dict, params)
            detect = lambda img: detector.detectMarkers(img)
        else:
            params = cv2.aruco.DetectorParameters_create()
            detect = lambda img: cv2.aruco.detectMarkers(img, aruco_dict, parameters=params)
        
        frame_found = None
        max_frames_to_check = 100
        
        for i in range(max_frames_to_check):
            ret, frame = cap.read()
            if not ret:
                break
            
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            corners, ids, _ = detect(gray)
            
            if ids is not None:
                ids = ids.flatten()
                # Rysuj wszystkie wykryte markery
                for idx, mid in enumerate(ids):
                    color = (0, 255, 0) if (marker_id is None or mid == marker_id) else (0, 0, 255)
                    c = corners[idx][0].astype(int)
                    cv2.polylines(frame, [c], True, color, 3)
                    # Dodaj ID markera
                    cx, cy = c.mean(axis=0).astype(int)
                    cv2.putText(frame, f"ID: {mid}", (cx-20, cy), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)
                
                # Jeśli znaleziono szukany marker (lub dowolny)
                if marker_id is None or marker_id in ids:
                    frame_found = frame
                    break
        
        cap.release()
        
        if frame_found is not None:
            # Dodaj informację na obrazie
            cv2.putText(frame_found, f"ArUco Dictionary: {dict_name}", (10, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 0), 2)
            return cv2.cvtColor(frame_found, cv2.COLOR_BGR2RGB)
        else:
            # Zwróć pierwszą klatkę z informacją
            cap = cv2.VideoCapture(video_path)
            ret, frame = cap.read()
            cap.release()
            if ret:
                cv2.putText(frame, "Nie znaleziono markera ArUco", (10, 30),
                           cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                return cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            return None
            
    except Exception as e:
        print(f"Błąd podglądu: {str(e)}")
        return None

def process_video(
    video_file,
    calib_file,
    dict_name,
    marker_id,
    marker_size_cm,
    lock_distance_m,
    const_scale_frames,
    embed_plot,
    plot_unit_cm,
    side_by_side,
    series_number,
    progress=gr.Progress()
):
    """Główna funkcja przetwarzania wideo"""
    
    if video_file is None:
        return None, None, None, None, "❌ Brak pliku wideo!"
    
    progress(0, desc="Przygotowywanie...")
    
    # Ładowanie kalibracji
    K, D = None, None
    if calib_file is not None:
        K, D, msg = load_calibration_file(calib_file)
        print(msg)
    
    # Przygotowanie parametrów
    marker_id_int = None if marker_id == -1 else marker_id
    marker_size_m = marker_size_cm / 100.0
    lock_distance = lock_distance_m if lock_distance_m > 0 else None
    const_scale = const_scale_frames if const_scale_frames > 0 else 0
    
    # Utworzenie katalogu wyjściowego
    progress(0.1, desc="Tworzenie katalogu wyjściowego...")
    series_no = series_number if series_number > 0 else None
    out_dir, series_num = _make_output_dir(series_no)
    out_video_path = out_dir / "out_annotated.mp4"
    
    try:
        progress(0.2, desc="Inicjalizacja trackera...")
        
        # Tymczasowo zmieniamy globalne zmienne w module
        import Wychyleniomierz
        original_marker_len = Wychyleniomierz.MARKER_LEN_M
        original_lock_plane = Wychyleniomierz.LOCK_PLANE_DISTANCE_M
        original_const_scale = Wychyleniomierz.CONST_SCALE_FROM_FIRST_N
        original_embed = Wychyleniomierz.EMBED_PLOT_IN_VIDEO
        original_plot_cm = Wychyleniomierz.PLOT_UNIT_CM
        original_side_by_side = Wychyleniomierz.SIDE_BY_SIDE_LAYOUT
        
        Wychyleniomierz.MARKER_LEN_M = marker_size_m
        Wychyleniomierz.LOCK_PLANE_DISTANCE_M = lock_distance
        Wychyleniomierz.CONST_SCALE_FROM_FIRST_N = const_scale
        Wychyleniomierz.EMBED_PLOT_IN_VIDEO = embed_plot
        Wychyleniomierz.PLOT_UNIT_CM = plot_unit_cm
        Wychyleniomierz.SIDE_BY_SIDE_LAYOUT = side_by_side
        
        # Utworzenie i uruchomienie trackera
        tracker = ArucoTracker(
            video_path=video_file.name,
            dict_name=dict_name,
            marker_id=marker_id_int,
            out_path=str(out_video_path),
            camera_matrix=K,
            dist_coeffs=D,
            out_dir=out_dir
        )
        
        progress(0.3, desc="Przetwarzanie wideo...")
        tracker.run()
        
        # Przywróć oryginalne wartości
        Wychyleniomierz.MARKER_LEN_M = original_marker_len
        Wychyleniomierz.LOCK_PLANE_DISTANCE_M = original_lock_plane
        Wychyleniomierz.CONST_SCALE_FROM_FIRST_N = original_const_scale
        Wychyleniomierz.EMBED_PLOT_IN_VIDEO = original_embed
        Wychyleniomierz.PLOT_UNIT_CM = original_plot_cm
        Wychyleniomierz.SIDE_BY_SIDE_LAYOUT = original_side_by_side
        
        progress(0.9, desc="Przygotowywanie wyników...")
        
        # Zbierz pliki wynikowe
        csv_path = out_dir / "positions_px.csv"
        plot_px_path = out_dir / "deflection_y_px.png"
        plot_cm_path = out_dir / "deflection_y_cm.png"
        video_with_plot_path = out_dir / "out_annotated_with_plot.mp4"
        
        # Przygotuj wyniki
        video_result = str(out_video_path) if out_video_path.exists() else None
        video_plot_result = str(video_with_plot_path) if video_with_plot_path.exists() else None
        csv_result = str(csv_path) if csv_path.exists() else None
        
        # Wykresy
        plot_px = plt.imread(str(plot_px_path)) if plot_px_path.exists() else None
        plot_cm = plt.imread(str(plot_cm_path)) if plot_cm_path.exists() else None
        
        # Informacja o wynikach
        info = f"""
✅ **Przetwarzanie zakończone!**

📁 Folder wyników: `{out_dir}` (seria {series_num})

📊 **Wygenerowane pliki:**
- Wideo z adnotacjami: {'✓' if video_result else '✗'}
- Wideo z wykresem: {'✓' if video_plot_result else '✗'}
- Dane CSV: {'✓' if csv_result else '✗'}
- Wykres [px]: {'✓' if plot_px is not None else '✗'}
- Wykres [cm]: {'✓' if plot_cm is not None else '✗'}
"""
        
        progress(1.0, desc="Gotowe!")
        
        return video_result, video_plot_result, csv_result, plot_px, plot_cm, info
        
    except Exception as e:
        error_msg = f"❌ Błąd podczas przetwarzania: {str(e)}"
        print(error_msg)
        import traceback
        traceback.print_exc()
        return None, None, None, None, None, error_msg

def create_interface():
    """Tworzy interfejs Gradio"""
    
    with gr.Blocks(title="Wychyleniomierz - GUI", theme=gr.themes.Soft()) as demo:
        gr.Markdown("""
        # 🎯 Wychyleniomierz - Śledzenie markerów ArUco
        
        Aplikacja do analizy wychyleń na podstawie śledzenia markerów ArUco w nagraniach wideo.
        """)
        
        with gr.Tab("📹 Wejście"):
            with gr.Row():
                with gr.Column(scale=1):
                    video_input = gr.File(
                        label="Plik wideo",
                        file_types=["video"],
                        type="filepath"
                    )
                    
                    calib_input = gr.File(
                        label="Plik kalibracji kamery (.npz)",
                        file_types=[".npz"],
                        type="filepath"
                    )
                    
                    gr.Markdown("### 🎯 Ustawienia markera ArUco")
                    
                    dict_dropdown = gr.Dropdown(
                        choices=list(ARUCO_DICTS.keys()),
                        value="DICT_6X6_1000",
                        label="Słownik ArUco"
                    )
                    
                    marker_id_input = gr.Number(
                        value=-1,
                        label="ID markera (-1 = dowolny)",
                        precision=0
                    )
                    
                    marker_size_input = gr.Number(
                        value=DEFAULT_MARKER_SIZE * 100,
                        label="Rozmiar markera [cm]",
                        minimum=0.1,
                        maximum=100.0,
                        step=0.1
                    )
                
                with gr.Column(scale=2):
                    video_info = gr.Markdown("Wybierz plik wideo...")
                    preview_image = gr.Image(
                        label="Podgląd pierwszej klatki z markerem",
                        type="numpy"
                    )
            
            # Aktualizacja informacji o wideo
            video_input.change(
                fn=get_video_info,
                inputs=[video_input],
                outputs=[video_info]
            )
            
            # Aktualizacja podglądu
            for inp in [video_input, dict_dropdown, marker_id_input]:
                inp.change(
                    fn=get_first_frame_with_aruco,
                    inputs=[video_input, dict_dropdown, marker_id_input],
                    outputs=[preview_image]
                )
        
        with gr.Tab("⚙️ Parametry"):
            with gr.Row():
                with gr.Column():
                    gr.Markdown("### 📏 Skalowanie")
                    
                    lock_distance_input = gr.Number(
                        value=DEFAULT_LOCK_DISTANCE,
                        label="Stała odległość płaszczyzny [m] (0 = auto)",
                        minimum=0.0,
                        maximum=10.0,
                        step=0.1
                    )
                    
                    const_scale_input = gr.Number(
                        value=0,
                        label="Liczba klatek do mediany Z (0 = wyłączone)",
                        minimum=0,
                        maximum=100,
                        precision=0
                    )
                
                with gr.Column():
                    gr.Markdown("### 📊 Opcje wyjścia")
                    
                    embed_plot_checkbox = gr.Checkbox(
                        value=True,
                        label="Generuj wideo z wykresem"
                    )
                    
                    plot_unit_checkbox = gr.Checkbox(
                        value=True,
                        label="Wykres w centymetrach (False = piksele)"
                    )
                    
                    side_by_side_checkbox = gr.Checkbox(
                        value=True,
                        label="Układ side-by-side (wideo + wykres)"
                    )
                    
                    series_input = gr.Number(
                        value=0,
                        label="Numer serii (0 = auto)",
                        minimum=0,
                        precision=0
                    )
        
        with gr.Tab("▶️ Przetwarzanie"):
            process_btn = gr.Button("🚀 Rozpocznij przetwarzanie", variant="primary", size="lg")
            
            status_output = gr.Markdown("Gotowy do przetwarzania...")
            
            with gr.Row():
                with gr.Column():
                    gr.Markdown("### 📹 Wideo wynikowe")
                    video_output = gr.Video(label="Wideo z adnotacjami")
                    video_plot_output = gr.Video(label="Wideo z wykresem")
                
                with gr.Column():
                    gr.Markdown("### 📊 Wykresy")
                    plot_px_output = gr.Image(label="Wykres wychyleń [px]")
                    plot_cm_output = gr.Image(label="Wykres wychyleń [cm]")
            
            gr.Markdown("### 📥 Pliki do pobrania")
            csv_output = gr.File(label="Dane CSV")
        
        # Obsługa przetwarzania
        process_btn.click(
            fn=process_video,
            inputs=[
                video_input,
                calib_input,
                dict_dropdown,
                marker_id_input,
                marker_size_input,
                lock_distance_input,
                const_scale_input,
                embed_plot_checkbox,
                plot_unit_checkbox,
                side_by_side_checkbox,
                series_input
            ],
            outputs=[
                video_output,
                video_plot_output,
                csv_output,
                plot_px_output,
                plot_cm_output,
                status_output
            ]
        )
        
        gr.Markdown("""
        ---
        ### 📖 Instrukcja użycia:
        
        1. **Wgraj plik wideo** z nagraniem zawierającym marker ArUco
        2. **Opcjonalnie wgraj plik kalibracji** kamery (.npz) dla dokładniejszych pomiarów
        3. **Wybierz słownik ArUco** odpowiedni dla Twojego markera
        4. **Ustaw ID markera** lub pozostaw -1 aby śledzić dowolny marker
        5. **Podaj rozmiar markera** w centymetrach
        6. **Dostosuj parametry** skalowania i opcje wyjścia
        7. **Kliknij "Rozpocznij przetwarzanie"** i poczekaj na wyniki
        
        ### 🎯 Wskazówki:
        
        - Dla najlepszych wyników użyj pliku kalibracji kamery
        - Upewnij się, że marker jest dobrze widoczny i kontrastowy
        - Stała odległość płaszczyzny pomaga w stabilnym skalowaniu
        - Układ side-by-side pozwala na jednoczesny podgląd wideo i wykresu
        """)
    
    return demo

# Uruchomienie aplikacji
if __name__ == "__main__":
    demo = create_interface()
    demo.launch(
        share=False,
        server_name="0.0.0.0",
        server_port=7860,
        show_error=True
    )