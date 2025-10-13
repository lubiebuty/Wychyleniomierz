# 🎬 Podgląd wideo z wykresem - Instrukcja

## ✅ Nowa funkcjonalność dodana!

Po zakończeniu pomiaru wideo z wykresem wychyleń (`out_annotated_with_plot.mp4`) będzie automatycznie wyświetlane w interfejsie GUI.

## 🎯 Jak to działa:

### 1. Przeprowadź kalibrację
- W zakładce "1️⃣ Kalibracja"
- Utwórz folder na wyniki

### 2. Przejdź do pomiarów
- W zakładce "2️⃣ Pomiary"
- Status kalibracji zmieni się na: "✅ Kalibracja zakończona!"

### 3. Wykonaj pomiar
- Wgraj wideo pomiaru
- Podaj nazwę pomiaru
- Kliknij "🚀 Rozpocznij pomiar"

### 4. Podgląd wyników
- Po zakończeniu pomiaru pojawi się sekcja "📹 Podgląd wyników"
- Wideo z wykresem wychyleń będzie automatycznie wyświetlane
- Możesz odtworzyć wideo bezpośrednio w przeglądarce

## 🎬 Co zawiera wideo:

- **Lewa strona**: Oryginalne wideo z naniesionymi adnotacjami
  - Zielony kontur: Wykryty marker ArUco
  - Czerwona kropka: Środek markera
  - Niebieski prostokąt: Obszar poszukiwań (ROI)

- **Prawa strona**: Wykres wychyleń w czasie rzeczywistym
  - Czerwona kropka: Aktualna pozycja na wykresie
  - HUD z informacjami:
    - Czas i numer klatki
    - Pozycja markera (x, y) w pikselach
    - Wychylenia Δx i Δy w pikselach, milimetrach i centymetrach

## 📁 Pliki wygenerowane:

W folderze pomiaru znajdziesz:
- `out_annotated.mp4` - Wideo z adnotacjami (bez wykresu)
- `out_annotated_with_plot.mp4` - **Wideo z wykresem** (wyświetlane w GUI)
- `positions_px.csv` - Dane pozycji
- `deflection_y_px.png` - Wykres wychyleń w pikselach
- `deflection_y_cm.png` - Wykres wychyleń w centymetrach

## 🔄 Kolejne pomiary:

- Kliknij "➕ Dodaj kolejny pomiar"
- Wideo zostanie ukryte
- Możesz wgrać nowe wideo i rozpocząć kolejny pomiar

## 🎯 Korzyści:

1. **Natychmiastowy podgląd** - Nie musisz szukać pliku w folderze
2. **Weryfikacja wyników** - Sprawdź czy marker był dobrze śledzony
3. **Analiza w czasie rzeczywistym** - Zobacz jak zmieniały się wychylenia
4. **Wygoda** - Wszystko w jednym interfejsie

## 🚀 Aplikacja gotowa!

Aplikacja działa pod adresem: **http://localhost:7861**

Możesz teraz:
1. Przeprowadzić kalibrację
2. Wykonać pomiar
3. **Obejrzeć wideo z wykresem bezpośrednio w GUI!** 🎬

---

**Wersja**: 1.1.0  
**Data**: 2024-10-13  
**Nowa funkcja**: Podgląd wideo z wykresem wychyleń w interfejsie GUI
