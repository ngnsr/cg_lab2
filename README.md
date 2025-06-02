# Isothetic Polygon Decomposition & Visualization

This project provides an interactive GUI for creating and **decomposing isothetic polygons** — polygons with all edges parallel to the coordinate axes. Once a polygon is completed, it is automatically **decomposed into non-overlapping rectangles**.

## ✨ Features

- **Grid-Aligned Drawing**: Add vertices constrained to axis-aligned directions (isothetic constraint).
- **Automatic Decomposition**: A single completed polygon is automatically decomposed into rectangles.
- **Interactive Interface**: Add points, visualize decomposition, zoom and pan.
- **JSON Import/Export**: Save and load polygon data using JSON.
- **Undo Support**: Undo the last point or remove the entire polygon.
- **Single Polygon Mode**: Only one polygon can exist at a time.

## 🛠 Installation

### 1. Clone the Repository

```bash
git clone https://github.com/ngnsr/cg_lab2.git
cd cg_lab2
```

### 2. Create a Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

#### Dependencies

- `PySide6` — for the graphical user interface
- `sortedcontainers` — for efficient coordinate sorting

## 🚀 Running the Application

```bash
python main.py
```

## 🧭 Usage

- **Add Points**: Click on the canvas to add axis-aligned points. A green guide line helps alignment.
- **Complete Polygon**: Select first point and press 'Finish polygon'.
- **Decomposition**: The polygon is automatically decomposed into rectangles once completed.
- **Import/Export**: Use JSON files to load or save polygon data.
- **Undo**: Remove the last added point or clear the entire polygon.
- **Zoom & Pan**: Scroll to zoom, drag with the mouse to pan across the canvas.

## 📌 Notes

- Only **isothetic polygons** are supported.
- Only one polygon can be active at a time.
