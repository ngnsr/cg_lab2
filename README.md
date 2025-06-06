# Isothetic Polygon Decomposition & Visualization

This project provides an interactive GUI for creating and **decomposing isothetic polygons** — polygons with all edges parallel to the coordinate axes. Once a polygon is completed, it is automatically **decomposed into non-overlapping rectangles**.

<p align="center">
  <img src="/docs/assets/app.png" alt="App" width="500"/><br>
  <em>App Overview</em>
</p>

<p align="center">
  <img src="/docs/assets/orig1.png" alt="Isothetic Polygon 1" width="500"/><br>
  <em>Isothetic Polygon 1 (Randomly generated with 100 points)</em>
</p>

<p align="center">
  <img src="/docs/assets/dec1.png" alt="Isothetic Polygon Decomposed 1" width="500"/><br>
  <em>Isothetic Polygon Decomposed 1</em>
</p>

<p align="center">
  <img src="/docs/assets/orig2.png" alt="Isothetic Polygon 2 with hole" width="500"/><br>
  <em>Isothetic Polygon 2 (With hole)</em>
</p>

<p align="center">
  <img src="/docs/assets/dec2.png" alt="Isothetic Polygon Decomposed 2" width="500"/><br>
  <em>Isothetic Polygon Decomposed 2</em>
</p>

<p align="center">
  <img src="/docs/assets/orig3.png" alt="Isothetic Polygon 3 with hole and island" width="500"/><br>
  <em>Isothetic Polygon 3 (With hole and island)</em>
</p>

<p align="center">
  <img src="/docs/assets/dec3.png" alt="Isothetic Polygon Decomposed 3" width="500"/><br>
  <em>Isothetic Polygon Decomposed 3</em>
</p>

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
