#!/usr/bin/env python3
"""
GUI dla Wychyleniomierza - Aplikacja do kalibracji kamery i pomiaru wychyleń
Wykorzystuje Gradio do tworzenia interfejsu graficznego
"""

import gradio as gr
import os
import shutil
import numpy as np
from pathlib import Path
import datetime
import subprocess
import sys
import cv2

# Import modułów programu
import Generowanie_wzorca as gen_wzorca
import Kalibracja as kalibracja_module
import Wychyleniomierz as wychyleniomierz_module


class WychyleniomierzGUI:
    def __init__(self):
        self.calibration_file_path = None
        self.calibration_folder = None
        self.results_base_folder = None
        self.current_calibration_report = None
        
    # ========== OKNO 1: KALIBRACJA ==========
    
    def download_pattern(self):
        """Generuje i zwraca ścieżkę do wzorca kalibracyjnego"""
        try:
            # Generuj wzorzec w folderze patterns
            pattern_path = gen_wzorca.generate_charuco_jpg()
            if os.path.exists(pattern_path):
                return pattern_path, "✅ Wzorzec kalibracyjny wygenerowany pomyślnie"
            else:
                return None, "❌ Błąd podczas generowania wzorca"
        except Exception as e:
            return None, f"❌ Błąd: {str(e)}"
    
    def validate_npz_file(self, file):
        """Sprawdza czy plik ma rozszerzenie .npz"""
        if file is None:
            return None, "⚠️ Nie wybrano pliku"
        
        file_path = file.name if hasattr(file, 'name') else str(file)
        if not file_path.endswith('.npz'):
            return None, "❌ Błąd: Wybierz plik z rozszerzeniem .npz"
        
        self.calibration_file_path = file_path
        return file_path, f"✅ Załadowano plik: {os.path.basename(file_path)}"
    
    def process_calibration_video(self, video_file, series_name, frameskip):
        """Przetwarza wideo kalibracyjne"""
        if video_file is None:
            return "❌ Nie wybrano pliku wideo", None
        
        if not series_name or series_name.strip() == "":
            return "❌ Proszę podać nazwę serii kalibracyjnej", None
        
        try:
            frameskip = int(frameskip)
            if frameskip < 1:
                frameskip = 1
        except:
            return "❌ Frameskip musi być liczbą całkowitą większą od 0", None
        
        video_path = video_file.name if hasattr(video_file, 'name') else str(video_file)
        
        # Uruchom kalibrację z podanymi parametrami
        try:
            report = self.run_calibration(video_path, series_name, frameskip)
            return report, "success"
        except Exception as e:
            return f"❌ Błąd podczas kalibracji: {str(e)}", None
    
    def run_calibration(self, video_path, series_name, frameskip):
        """Wykonuje proces kalibracji"""
        # Utwórz folder serii
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        series_folder_name = f"{series_name}_{timestamp}"
        series_base = Path("serie_kalibracji")
        series_base.mkdir(exist_ok=True)
        series_folder = series_base / series_folder_name
        series_folder.mkdir(exist_ok=True)
        
        # Utwórz foldery wyjściowe
        calib_output = series_folder / "pliki_kalibracji"
        debug_output = series_folder / "pliki_debug"
        calib_output.mkdir(exist_ok=True)
        debug_output.mkdir(exist_ok=True)
        
        # Modyfikuj parametry w module kalibracji
        original_video = kalibracja_module.SOURCE_VIDEO
        original_frameskip = kalibracja_module.FRAME_SKIP
        original_output_dir = kalibracja_module.OUTPUT_DIR
        original_debug_dir = kalibracja_module.DEBUG_DIR
        
        kalibracja_module.SOURCE_VIDEO = video_path
        kalibracja_module.FRAME_SKIP = frameskip
        kalibracja_module.OUTPUT_DIR = calib_output
        kalibracja_module.DEBUG_DIR = debug_output
        
        try:
            # Wykonaj kalibrację
            board = kalibracja_module.create_charuco_board()
            detector = kalibracja_module.create_charuco_detector(board)
            
            # Otwórz wideo
            cap = cv2.VideoCapture(str(video_path))
            if not cap.isOpened():
                return f"❌ Nie można otworzyć wideo: {video_path}"
            
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            
            # Kolekcja danych
            all_charuco_corners = []
            all_charuco_ids = []
            image_size = None
            
            frame_idx = 0
            used_frames = 0
            total_markers = 0
            total_corners = 0
            
            # Przetwarzaj klatki
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                frame_idx += 1
                
                # Próbkowanie
                if frame_idx % frameskip != 0:
                    continue
                
                # Konwersja do grayscale
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                
                if image_size is None:
                    image_size = gray.shape[::-1]
                
                # Wykryj rogi ChArUco
                charuco_corners, charuco_ids, marker_corners, marker_ids = kalibracja_module.detect_charuco_corners(detector, gray)
                
                # Policz wykryte elementy
                num_markers = len(marker_ids) if marker_ids is not None else 0
                num_corners = len(charuco_corners) if charuco_corners is not None else 0
                
                # Sprawdź czy znaleziono wystarczająco rogów
                if charuco_corners is not None and charuco_ids is not None and len(charuco_corners) >= kalibracja_module.MIN_CHARUCO_CORNERS:
                    all_charuco_corners.append(charuco_corners)
                    all_charuco_ids.append(charuco_ids)
                    used_frames += 1
                    
                    total_markers += num_markers
                    total_corners += num_corners
                    
                    # Zapisz debug frame (pierwsze 10)
                    if used_frames <= 10:
                        debug_frame = frame.copy()
                        
                        # Rysuj markery
                        if marker_corners is not None and marker_ids is not None:
                            cv2.aruco.drawDetectedMarkers(debug_frame, marker_corners, marker_ids)
                        
                        # Rysuj rogi ChArUco
                        cv2.aruco.drawDetectedCornersCharuco(debug_frame, charuco_corners, charuco_ids, (0, 255, 0))
                        
                        cv2.imwrite(
                            str(debug_output / f"charuco_{used_frames:03d}_m{num_markers}_c{num_corners}.jpg"),
                            debug_frame
                        )
            
            cap.release()
            
            # Sprawdź czy mamy wystarczająco danych
            if used_frames < kalibracja_module.MIN_FRAMES:
                report = f"❌ Za mało dobrych klatek!\n\n"
                report += f"Potrzeba minimum: {kalibracja_module.MIN_FRAMES}\n"
                report += f"Znaleziono: {used_frames}\n\n"
                report += f"Spróbuj zmniejszyć frameskip lub użyć dłuższego wideo."
                return report
            
            # KALIBRACJA
            rms, camera_matrix, dist_coeffs, rvecs, tvecs = kalibracja_module.calibrate_camera_charuco(
                all_charuco_corners,
                all_charuco_ids,
                board,
                image_size
            )
            
            # Zapisz wyniki
            kalibracja_module.save_calibration_results(camera_matrix, dist_coeffs, rms, image_size)
            
            # Zapisz ścieżkę do pliku kalibracyjnego
            npz_file = calib_output / "charuco_calibration.npz"
            if npz_file.exists():
                self.calibration_file_path = str(npz_file)
            
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
                'squares_x': kalibracja_module.SQUARES_X,
                'squares_y': kalibracja_module.SQUARES_Y,
                'square_length': kalibracja_module.SQUARE_LENGTH * 1000,
                'marker_length': kalibracja_module.MARKER_LENGTH * 1000,
                'dictionary': kalibracja_module.DICT_NAME,
                'legacy_pattern': kalibracja_module.LEGACY_PATTERN
            }
            
            processing_params = {
                'frame_skip': frameskip,
                'min_charuco_corners': kalibracja_module.MIN_CHARUCO_CORNERS,
                'min_frames': kalibracja_module.MIN_FRAMES,
                'preprocessing': 'CLAHE + Bilateral + Sharpening',
                'save_debug_frames': True
            }
            
            # Lista plików
            calib_files = list(calib_output.iterdir()) if calib_output.exists() else []
            debug_files = list(debug_output.iterdir()) if debug_output.exists() else []
            
            output_files = {
                'calibration_files': [str(f) for f in calib_files if f.is_file()],
                'debug_files': [str(f) for f in debug_files if f.is_file()],
                'series_files': []
            }
            
            # Utwórz szczegółowy raport
            report_path = kalibracja_module.create_detailed_report(
                series_folder, video_path, calibration_results, detection_stats,
                board_params, processing_params, output_files
            )
            
            # Odczytaj raport
            if report_path.exists():
                with open(report_path, 'r', encoding='utf-8') as f:
                    report = f.read()
            else:
                report = "✅ Kalibracja zakończona pomyślnie!\n\n"
                report += f"📁 Folder: {series_folder}\n"
                report += f"RMS error: {rms:.6f} pikseli\n"
                report += f"Użyto {used_frames} klatek\n"
            
            # Zapisz folder jako bieżący
            self.calibration_folder = series_folder
            self.current_calibration_report = report
            
            return report
            
        except Exception as e:
            return f"❌ Błąd podczas kalibracji: {str(e)}\n\nSzczegóły: {repr(e)}"
            
        finally:
            # Przywróć oryginalne parametry
            kalibracja_module.SOURCE_VIDEO = original_video
            kalibracja_module.FRAME_SKIP = original_frameskip
            kalibracja_module.OUTPUT_DIR = original_output_dir
            kalibracja_module.DEBUG_DIR = original_debug_dir
    
    def ask_repeat_calibration(self, report_text):
        """Wyświetla raport i pyta czy powtórzyć kalibrację"""
        return report_text
    
    def select_results_folder(self):
        """Pozwala użytkownikowi wybrać folder na wyniki"""
        # W Gradio nie możemy bezpośrednio otworzyć dialogu wyboru folderu
        # Użytkownik poda nazwę, a my utworzymy folder
        return "Podaj nazwę folderu dla wyników w następnym kroku"
    
    def create_results_folder(self, folder_name):
        """Tworzy folder na wyniki pomiarów"""
        if not folder_name or folder_name.strip() == "":
            return "❌ Proszę podać nazwę folderu"
        
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        folder_name_full = f"{folder_name}_{timestamp}"
        results_folder = Path(folder_name_full)
        results_folder.mkdir(exist_ok=True)
        
        # Skopiuj plik kalibracyjny do podfolderu
        if self.calibration_file_path:
            calib_subfolder = results_folder / "kalibracja"
            calib_subfolder.mkdir(exist_ok=True)
            shutil.copy2(self.calibration_file_path, calib_subfolder)
        
        self.results_base_folder = results_folder
        return f"✅ Utworzono folder: {results_folder}\n\n🎯 GOTOWE! Przejdź do zakładki '2️⃣ Pomiary' aby rozpocząć analizę wideo."
    
    # ========== OKNO 2: POMIARY ==========
    
    def process_measurement_video(self, video_file, measurement_name):
        """Przetwarza wideo pomiarowe"""
        if video_file is None:
            return "❌ Nie wybrano pliku wideo", None, None
        
        if not measurement_name or measurement_name.strip() == "":
            return "❌ Proszę podać nazwę pomiaru", None, None
        
        if self.calibration_file_path is None:
            return "❌ Brak pliku kalibracyjnego. Najpierw przeprowadź kalibrację lub wgraj plik .npz", None, None
        
        if self.results_base_folder is None:
            return "❌ Nie wybrano folderu wynikowego. Najpierw zakończ proces kalibracji.", None, None
        
        # Sprawdź czy to jest plik, nie folder
        if hasattr(video_file, 'name'):
            video_path = video_file.name
        else:
            video_path = str(video_file)
        
        # Sprawdź czy ścieżka wskazuje na plik, nie folder
        if os.path.isdir(video_path):
            return f"❌ Błąd: Wybrano folder zamiast pliku wideo: {video_path}", None, None
        
        try:
            results, output_video_path = self.run_measurement(video_path, measurement_name)
            return results, "success", output_video_path
        except Exception as e:
            return f"❌ Błąd podczas pomiaru: {str(e)}", None, None
    
    def run_measurement(self, video_path, measurement_name):
        """Wykonuje pomiar wychyleń"""
        # Utwórz podfolder dla tego pomiaru
        measurement_folder = self.results_base_folder / measurement_name
        measurement_folder.mkdir(exist_ok=True)
        
        # Załaduj kalibrację
        try:
            with np.load(self.calibration_file_path) as calib:
                K = calib["camera_matrix"]
                D = calib["dist_coeffs"]
        except Exception as e:
            return f"❌ Błąd wczytywania kalibracji: {str(e)}"
        
        # Ustaw parametry w module wychyleniomierza
        out_video_path = measurement_folder / "out_annotated.mp4"
        
        # Uruchom tracker
        tracker = wychyleniomierz_module.ArucoTracker(
            video_path=video_path,
            dict_name=wychyleniomierz_module.ARUCO_DICT,
            marker_id=wychyleniomierz_module.MARKER_ID,
            out_path=str(out_video_path),
            camera_matrix=K,
            dist_coeffs=D,
            out_dir=measurement_folder
        )
        
        tracker.run()
        
        # Sprawdź czy wygenerowano wideo z wykresem (z fall-backiem)
        plot_video_path = measurement_folder / "out_annotated_with_plot.mp4"
        output_video_path = None

        print(f"🔍 Sprawdzam wideo: {plot_video_path}")
        print(f"🔍 Plik istnieje: {plot_video_path.exists()}")

        if plot_video_path.exists():
            output_video_path = str(plot_video_path)
            print(f"✅ Wideo znalezione: {output_video_path}")
        else:
            # Fallback: spróbuj znaleźć dowolne mp4 w folderze pomiaru
            print(f"❌ Wideo nie znalezione: {plot_video_path}")
            mp4_candidates = sorted([p for p in measurement_folder.glob("*.mp4")])
            for cand in mp4_candidates:
                # Preferuj właściwą nazwę jeśli istnieje
                if "out_annotated_with_plot" in cand.name:
                    output_video_path = str(cand)
                    break
            if output_video_path is None and mp4_candidates:
                # Ostateczny fallback: pierwsze napotkane mp4 (np. out_annotated.mp4)
                output_video_path = str(mp4_candidates[0])
            print(f"📁 Kandydaci MP4: {[p.name for p in mp4_candidates]}")
            print(f"➡️ Wybrano do podglądu: {output_video_path}")
        
        # Przygotuj raport wyników
        results = f"✅ Pomiar zakończony pomyślnie!\n\n"
        results += f"📁 Folder wyników: {measurement_folder}\n\n"
        results += f"Wygenerowane pliki:\n"
        
        for file in measurement_folder.iterdir():
            if file.is_file():
                results += f"  📄 {file.name}\n"
        
        if output_video_path:
            results += f"\n🎬 Wideo z wykresem dostępne poniżej!"
        
        return results, output_video_path
    
    def process_measurement_with_video(self, video_file, measurement_name):
        """Przetwarza wideo pomiarowe i zwraca wyniki oraz aktualizację podglądu wideo"""
        results, status, video_path = self.process_measurement_video(video_file, measurement_name)
        
        print(f"🔍 Debug process_measurement_with_video:")
        print(f"  - status: {status}")
        print(f"  - video_path: {video_path}")
        print(f"  - video_path is not None: {video_path is not None}")
        
        # Jeśli pomiar się powiódł i mamy wideo, pokaż je
        if status == "success" and video_path:
            print(f"✅ Wyświetlam wideo: {video_path}")
            return results, measurement_name, gr.update(value=video_path, visible=True)
        else:
            print(f"❌ Nie wyświetlam wideo - status: {status}, video_path: {video_path}")
            return results, measurement_name, gr.update(value=None, visible=False)
    
    # ========== BUDOWA INTERFEJSU ==========
    
    def build_interface(self):
        """Buduje interfejs Gradio"""
        
        with gr.Blocks(title="Wychyleniomierz - System kalibracji i pomiarów", theme=gr.themes.Soft()) as app:
            gr.Markdown("# 🎯 Wychyleniomierz - System kalibracji i pomiarów")
            gr.Markdown("System do kalibracji kamery i pomiaru wychyleń z użyciem markerów ArUco")
            
            with gr.Tabs():
                # ===== TAB 1: KALIBRACJA =====
                with gr.Tab("1️⃣ Kalibracja"):
                    gr.Markdown("## Krok 1: Wzorzec kalibracyjny")
                    
                    with gr.Row():
                        with gr.Column():
                            btn_download_pattern = gr.Button("📥 Pobierz wzorzec kalibracyjny", variant="primary")
                            pattern_output = gr.File(label="Wzorzec do pobrania", interactive=False)
                            pattern_status = gr.Textbox(label="Status", interactive=False)
                    
                    gr.Markdown("---")
                    gr.Markdown("## Krok 2: Plik kalibracji")
                    gr.Markdown("**Wybierz jedną z opcji:**")
                    
                    with gr.Row():
                        with gr.Column():
                            gr.Markdown("### ✅ Opcja A: Wgraj gotowy plik kalibracji (.npz)")
                            upload_calib_file = gr.File(
                                label="Przeciągnij plik .npz lub kliknij aby wybrać",
                                file_types=[".npz"],
                                type="filepath"
                            )
                            calib_file_status = gr.Textbox(label="Status pliku kalibracji", interactive=False)
                        
                        with gr.Column():
                            gr.Markdown("### 📹 Opcja B: Nagraj wideo kalibracyjne")
                            upload_calib_video = gr.File(
                                label="Przeciągnij wideo lub kliknij aby wybrać",
                                file_types=[".mp4", ".mov", ".avi", ".MOV"],
                                type="filepath"
                            )
                            calib_video_status = gr.Textbox(label="Status wideo", interactive=False)
                    
                    # Panel kalibracji (pokazuje się po wgraniu wideo)
                    with gr.Group(visible=True) as calib_params_group:
                        gr.Markdown("### ⚙️ Parametry kalibracji")
                        
                        series_name_input = gr.Textbox(
                            label="Nazwa serii kalibracyjnej",
                            placeholder="np. kalibracja_laboratorium_1",
                            value="seria_kalibracji"
                        )
                        
                        frameskip_input = gr.Slider(
                            minimum=1,
                            maximum=30,
                            value=15,
                            step=1,
                            label="Frameskip (co ile klatek)",
                            info="Im większy frameskip, tym szybsza kalibracja, ale mniejsza dokładność"
                        )
                        
                        gr.Markdown("ℹ️ **Informacja:** Im większy frameskip, tym szybsza kalibracja, ale mniejsza dokładność. Zalecane: 10-15 dla standardowej kalibracji.")
                        
                        btn_start_calibration = gr.Button("🚀 Rozpocznij kalibrację", variant="primary", size="lg")
                    
                    # Wyniki kalibracji
                    calibration_report = gr.Textbox(
                        label="Raport kalibracji",
                        lines=20,
                        interactive=False
                    )
                    
                    with gr.Row():
                        btn_repeat_calib = gr.Button("🔄 Powtórz kalibrację", variant="secondary")
                        btn_accept_calib = gr.Button("✅ Akceptuj i przejdź dalej", variant="primary")
                    
                    # Wybór folderu wyników
                    with gr.Group(visible=False) as results_folder_group:
                        gr.Markdown("### 📁 Folder na wyniki pomiarów")
                        results_folder_name = gr.Textbox(
                            label="Nazwa folderu na wyniki",
                            placeholder="np. pomiary_2024_10_13",
                            value="wyniki_pomiarow"
                        )
                        btn_create_results_folder = gr.Button("📁 Utwórz folder", variant="primary")
                        results_folder_status = gr.Textbox(label="Status", interactive=False)
                        
                        gr.Markdown("---")
                        gr.Markdown("### 🎯 Następny krok")
                        gr.Markdown("Po utworzeniu folderu przejdź do zakładki **'2️⃣ Pomiary'** aby rozpocząć analizę wideo.")
                
                # ===== TAB 2: POMIARY =====
                with gr.Tab("2️⃣ Pomiary"):
                    gr.Markdown("## Pomiar wychyleń")
                    gr.Markdown("Wgraj wideo z markerem ArUco do analizy wychyleń")
                    
                    # Status kalibracji
                    calibration_status = gr.Textbox(
                        label="Status kalibracji",
                        value="⚠️ Najpierw przeprowadź kalibrację w zakładce '1️⃣ Kalibracja'",
                        interactive=False
                    )
                    
                    upload_measurement_video = gr.File(
                        label="📹 Wgraj plik wideo pomiaru",
                        file_types=[".mp4", ".mov", ".avi", ".MOV"],
                        type="filepath"
                    )
                    
                    measurement_name_input = gr.Textbox(
                        label="Nazwa pomiaru",
                        placeholder="np. test_1_obciazenie_50kg",
                        value="pomiar_1"
                    )
                    
                    btn_start_measurement = gr.Button("🚀 Rozpocznij pomiar", variant="primary", size="lg")
                    
                    measurement_results = gr.Textbox(
                        label="Wyniki pomiaru",
                        lines=10,
                        interactive=False
                    )
                    
                    # Podgląd wygenerowanego wideo
                    gr.Markdown("### 📹 Podgląd wyników")
                    video_preview = gr.Video(
                        label="Wideo z wykresem wychyleń",
                        interactive=False,
                        visible=False
                    )
                    
                    # Usuwamy dodatkowy stan widoczności; będziemy aktualizować video bezpośrednio
                    
                    btn_next_measurement = gr.Button("➕ Dodaj kolejny pomiar", variant="secondary")
            
            # ===== CALLBACKS =====
            
            # Pobierz wzorzec
            btn_download_pattern.click(
                fn=self.download_pattern,
                inputs=[],
                outputs=[pattern_output, pattern_status]
            )
            
            # Walidacja pliku kalibracji
            upload_calib_file.change(
                fn=self.validate_npz_file,
                inputs=[upload_calib_file],
                outputs=[upload_calib_file, calib_file_status]
            )
            
            # Upload wideo kalibracyjnego
            upload_calib_video.change(
                fn=lambda x: "✅ Wideo załadowane. Uzupełnij parametry i rozpocznij kalibrację." if x else "",
                inputs=[upload_calib_video],
                outputs=[calib_video_status]
            )
            
            # Rozpocznij kalibrację
            btn_start_calibration.click(
                fn=self.process_calibration_video,
                inputs=[upload_calib_video, series_name_input, frameskip_input],
                outputs=[calibration_report, calib_video_status]
            )
            
            # Powtórz kalibrację
            btn_repeat_calib.click(
                fn=lambda: ("", "", 15),
                inputs=[],
                outputs=[calibration_report, series_name_input, frameskip_input]
            )
            
            # Akceptuj kalibrację i przejdź do tworzenia folderu
            btn_accept_calib.click(
                fn=lambda: gr.update(visible=True),
                inputs=[],
                outputs=[results_folder_group]
            )
            
            # Utwórz folder wyników
            btn_create_results_folder.click(
                fn=self.create_results_folder,
                inputs=[results_folder_name],
                outputs=[results_folder_status]
            )
            
            # Aktualizuj status kalibracji po utworzeniu folderu
            btn_create_results_folder.click(
                fn=lambda: "✅ Kalibracja zakończona! Możesz rozpocząć pomiary.",
                inputs=[],
                outputs=[calibration_status]
            )
            
            # Rozpocznij pomiar
            btn_start_measurement.click(
                fn=self.process_measurement_with_video,
                inputs=[upload_measurement_video, measurement_name_input],
                outputs=[measurement_results, measurement_name_input, video_preview]
            )
            
            # Następny pomiar - resetuj wszystkie pola
            def reset_measurement_fields():
                print("🔄 Resetowanie pól pomiaru")
                return None, "", gr.update(value=None, visible=False)
            
            btn_next_measurement.click(
                fn=reset_measurement_fields,
                inputs=[],
                outputs=[upload_measurement_video, measurement_name_input, video_preview]
            )
        
        return app


def find_free_port(start_port=7860, max_attempts=20):
    """Znajduje wolny port zaczynając od start_port"""
    import socket
    
    for port in range(start_port, start_port + max_attempts):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('localhost', port))
                return port
        except OSError:
            continue
    return None

def main():
    """Główna funkcja uruchamiająca GUI"""
    gui = WychyleniomierzGUI()
    app = gui.build_interface()
    
    # Znajdź wolny port
    port = find_free_port(7860, 20)
    if port is None:
        print("❌ Nie można znaleźć wolnego portu!")
        return
    
    print(f"🚀 Uruchamianie aplikacji na porcie {port}")
    print(f"📱 Aplikacja będzie dostępna pod adresem: http://localhost:{port}")
    
    # Uruchom aplikację
    app.launch(
        server_name="0.0.0.0",
        server_port=port,
        share=False,
        inbrowser=True
    )


if __name__ == "__main__":
    main()

