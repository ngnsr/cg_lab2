import time
import random
import math
import math
import json
from typing import List, Tuple
from PySide6.QtWidgets import QGraphicsView, QGraphicsScene, QLabel
from PySide6.QtCore import Qt, QPointF, QRectF, Signal
from PySide6.QtGui import QPen, QBrush, QColor, QPainter, QFont, QPolygonF
from collections import defaultdict
from utils import decompose_polygon_sweep, generate_large_isothetic_polygon

def is_horizontal(p1, p2):
    return abs(p1[1] - p2[1]) < 0.001

def is_vertical(p1, p2):
    return abs(p1[0] - p2[0]) < 0.001

def rect_from_strip(y1, y2, segments):
    """Побудова прямокутників між горизонтальними лініями y1 та y2"""
    rectangles = []
    segments.sort()
    i = 0
    while i < len(segments):
        x_start = segments[i][0]
        x_end = segments[i][1]
        # Об'єднання суміжних відрізків
        i += 1
        while i < len(segments) and segments[i][0] <= x_end:
            x_end = max(x_end, segments[i][1])
            i += 1
        rectangles.append(((x_start, y1), (x_end, y2)))
    return rectangles

class GridView(QGraphicsView):
    toast = Signal(str)  # Signal for showing toast messages
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Polygon management variables
        self.polygon_points = []  # List of QPointF for polygon vertices
        self.current_polygon = None  # Will be a QGraphicsPolygonItem
        self.point_items = []  # List to keep track of point markers
        self.finished_polygon = None  # The completed polygon
        self.decomposition_rectangles = []  # Store decomposition rectangles
        
        # Create scene with generous bounds
        self.scene = QGraphicsScene(self)
        self.scene.setSceneRect(-10000, -10000, 20000, 20000)
        self.setScene(self.scene)
        
        # Remove scrollbars
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        # Grid settings
        self.base_grid_size = 50
        self.scale_factor = 1.0
        self.zoom_factor = 1.2
        
        # Axis snapping threshold (in scene units)
        self.axis_snap_threshold = 0.1
        
        # Last mouse position for panning
        self.last_mouse_pos = QPointF()
        
        # Enable mouse tracking to get hover events
        self.setMouseTracking(True)
        
        # Rendering settings
        self.setRenderHint(QPainter.Antialiasing)
        self.setDragMode(QGraphicsView.NoDrag)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.AnchorUnderMouse)
        
        # Visual settings
        self.setBackgroundBrush(QBrush(QColor(240, 240, 240)))
        
        # Create a QLabel for coordinates display (fixed size, not affected by zoom)
        self.coords_label = QLabel(self)
        self.coords_label.setFont(QFont("Arial", 12, QFont.Bold))
        self.coords_label.setStyleSheet("""
            background-color: rgba(40, 40, 40, 220); 
            color: white;
            padding: 8px; 
            border: 2px solid #555;
            border-radius: 4px;
        """)
        self.coords_label.move(10, self.height() - 40)
        self.coords_label.setText("Coordinates: (0.00, 0.00)")  # Initial text
        self.coords_label.adjustSize()
        self.coords_label.show()
        
        # Create a QLabel for grid size info display
        self.grid_info_label = QLabel(self)
        self.grid_info_label.setFont(QFont("Arial", 10))
        self.grid_info_label.setStyleSheet("""
            background-color: rgba(40, 40, 40, 200); 
            color: white;
            padding: 4px; 
            border: 1px solid #555;
            border-radius: 3px;
        """)
        self.grid_info_label.move(10, 10)
        self.grid_info_label.setText("Grid: 50.0px | Scale: 1.0000x")  # Initial text
        self.grid_info_label.adjustSize()
        self.grid_info_label.show()
        
        # Nearest grid point variables
        self.nearest_grid_point = QPointF(0, 0)
        self.highlight_radius = 5  # Radius of the green highlight circle
        self.highlight_nearest = False  # Whether to show the highlight
        self.highlight_max_distance = 30  # Maximum pixel distance to show highlight

        # Initial view
        self.centerOn(0, 0)
    
    def resizeEvent(self, event):
        """Handle resize events to reposition the labels"""
        super().resizeEvent(event)
        self.coords_label.move(10, self.height() - 50)
        self.grid_info_label.move(10, 10)
    
    def get_adaptive_grid_size(self):
        """Calculate the grid size based on current zoom level"""
        transform = self.transform()
        current_scale = transform.m11()
        
        if current_scale <= 0.01:
            return 1000
        elif current_scale <= 0.1:
            return 100
        elif current_scale <= 1:
            return 50
        elif current_scale <= 10:
            return 10
        elif current_scale <= 100:
            return 1
        else:
            return 0.1
    
    def find_nearest_grid_point(self, scene_pos):
        """Find the nearest grid intersection point to the given scene position"""
        grid_size = self.get_adaptive_grid_size()
        grid_x = round(scene_pos.x() / grid_size) * grid_size
        grid_y = round(scene_pos.y() / grid_size) * grid_size
        return QPointF(grid_x, grid_y)
    
    def drawForeground(self, painter, rect):
        """Draw foreground elements including the green highlight dot"""
        super().drawForeground(painter, rect)
        
        if self.highlight_nearest:
            transform = self.transform()
            current_scale = transform.m11()
            scaled_radius = self.highlight_radius / current_scale
            highlight_pen = QPen(QColor(0, 180, 0))
            highlight_pen.setWidthF(2 / current_scale)
            painter.setPen(highlight_pen)
            highlight_brush = QBrush(QColor(0, 255, 0, 180))
            painter.setBrush(highlight_brush)
            painter.drawEllipse(self.nearest_grid_point, scaled_radius, scaled_radius)
    
    def drawBackground(self, painter, rect):
        """Custom background drawing to create the grid"""
        super().drawBackground(painter, rect)
        
        transform = self.transform()
        current_scale = transform.m11()
        effective_grid_size = self.get_adaptive_grid_size()
        visible_rect = self.mapToScene(self.viewport().rect()).boundingRect()
        
        left = math.floor(visible_rect.left() / effective_grid_size) * effective_grid_size
        top = math.floor(visible_rect.top() / effective_grid_size) * effective_grid_size
        right = math.ceil(visible_rect.right() / effective_grid_size) * effective_grid_size
        bottom = math.ceil(visible_rect.bottom() / effective_grid_size) * effective_grid_size
        
        pen_width = min(0.5 / current_scale, 0.5)
        thin_pen = QPen(QColor(200, 200, 200))
        thin_pen.setWidthF(pen_width)
        thick_pen = QPen(QColor(120, 120, 120))
        thick_pen.setWidthF(pen_width * 2)
        
        if effective_grid_size < 0.00001:
            effective_grid_size = 0.00001
        step = effective_grid_size
        
        y = top
        while y <= bottom:
            major_line = round(y / effective_grid_size) % 5 == 0
            painter.setPen(thick_pen if major_line else thin_pen)
            painter.drawLine(left, y, right, y)
            y += step
            
        x = left
        while x <= right:
            major_line = round(x / effective_grid_size) % 5 == 0
            painter.setPen(thick_pen if major_line else thin_pen)
            painter.drawLine(x, top, x, bottom)
            x += step
            
        axis_pen = QPen(QColor(0, 0, 0))
        axis_width = max(2 / current_scale, 0.5)
        axis_pen.setWidthF(axis_width)
        painter.setPen(axis_pen)
        painter.drawLine(0, top, 0, bottom)
        painter.drawLine(left, 0, right, 0)
        
        self.grid_info_label.setText(f"Grid: {effective_grid_size:.1f}px | Scale: {current_scale:.4f}x")
        self.grid_info_label.adjustSize()
    
    def mouseMoveEvent(self, event):
        """Handle mouse move events"""
        scene_pos = self.mapToScene(event.pos())
        current_scale = self.transform().m11()
        adjusted_threshold = self.axis_snap_threshold / current_scale
        
        if abs(scene_pos.x()) < adjusted_threshold:
            scene_pos.setX(0)
        if abs(scene_pos.y()) < adjusted_threshold:
            scene_pos.setY(0)
        
        self.nearest_grid_point = self.find_nearest_grid_point(scene_pos)
        nearest_point_in_view = self.mapFromScene(self.nearest_grid_point)
        mouse_pos_in_view = event.pos()
        dx = nearest_point_in_view.x() - mouse_pos_in_view.x()
        dy = nearest_point_in_view.y() - mouse_pos_in_view.y()
        distance = math.sqrt(dx*dx + dy*dy)
        self.highlight_nearest = distance <= self.highlight_max_distance
        
        rounded_x = round(scene_pos.x(), 2)
        rounded_y = round(-scene_pos.y(), 2)
        self.coords_label.setText(f"Coordinates: ({rounded_x}, {rounded_y})")
        self.coords_label.adjustSize()
        
        if event.buttons() & Qt.RightButton:
            delta = self.mapToScene(event.pos()) - self.mapToScene(self.last_mouse_pos)
            self.last_mouse_pos = event.pos()
            self.translate(-delta.x(), -delta.y())
        
        self.viewport().update()
        super().mouseMoveEvent(event)
    
    def mouseReleaseEvent(self, event):
        """Handle mouse release events"""
        if event.button() == Qt.RightButton:
            self.setCursor(Qt.ArrowCursor)
        super().mouseReleaseEvent(event)
    
    def wheelEvent(self, event):
        """Handle wheel events for zooming"""
        zoom_in = event.angleDelta().y() > 0
        current_scale = self.transform().m11()
        
        if zoom_in:
            if current_scale < 1000:
                self.scale_factor *= self.zoom_factor
                self.scale(self.zoom_factor, self.zoom_factor)
        else:
            if current_scale > 0.001:
                self.scale_factor /= self.zoom_factor
                self.scale(1 / self.zoom_factor, 1 / self.zoom_factor)
        
        self.viewport().update()
    
    def update_polygon(self):
        """Update the polygon with current points"""
        if self.current_polygon:
            self.scene.removeItem(self.current_polygon)
            self.current_polygon = None
        
        if len(self.polygon_points) >= 2:
            poly = QPolygonF(self.polygon_points)
            self.current_polygon = self.scene.addPolygon(
                poly,
                QPen(QColor(0, 0, 255, 200), 2/self.transform().m11()),
                QBrush(QColor(0, 0, 255, 50))
            )
    
    def remove_last_point(self):
        """Remove the last added point"""
        if self.polygon_points:
            removed_point = self.polygon_points.pop()
            if self.point_items:
                last_marker = self.point_items.pop()
                self.scene.removeItem(last_marker)
            self.update_polygon()
            print(f"Removed point: ({removed_point.x()}, {removed_point.y()})")
    
    def center_on_point(self, x, y):
        """Center the view on a specific point"""
        self.centerOn(x, y)
        print(f"Centered on point: ({x}, {y})")
    
    def mousePressEvent(self, event):
        """Handle mouse press events"""
        if event.button() == Qt.RightButton:
            self.setDragMode(QGraphicsView.NoDrag)
            self.last_mouse_pos = event.globalPosition().toPoint()
            self.setCursor(Qt.ClosedHandCursor)
        elif event.button() == Qt.LeftButton:
            if self.highlight_nearest:
                x, y = self.nearest_grid_point.x(), self.nearest_grid_point.y()
                print(f"Selected grid point: ({x}, {y})")
                self.add_polygon_point(x, y)
        super().mousePressEvent(event)
    
    def is_isothetic_direction(self, last_point, new_point):
        """Check if the direction from last_point to new_point is horizontal or vertical"""
        return (abs(last_point.x() - new_point.x()) < 0.001) or (abs(last_point.y() - new_point.y()) < 0.001)
    
    def add_polygon_point(self, x, y):
        """Add a point to the current polygon with isothetic validation"""
        # Check if polygon is already finished
        if self.finished_polygon is not None:
            self.toast.emit("Polygon already finished. Clear to start a new one.")
            return False
            
        new_point = QPointF(x, y)
        
        if self.polygon_points:
            last_point = self.polygon_points[-1]
            if not self.is_isothetic_direction(last_point, new_point):
                self.toast.emit("Invalid point: not horizontal or vertical from last point")
                print(f"Invalid point: ({x}, {y}) - not horizontal or vertical from last point")
                return False
        
        self.polygon_points.append(new_point)
        point_marker = self.scene.addEllipse(
            x - 5/self.transform().m11(), 
            y - 5/self.transform().m11(), 
            10/self.transform().m11(), 
            10/self.transform().m11(), 
            QPen(QColor(255, 0, 0)), 
            QBrush(QColor(255, 0, 0, 200))
        )
        self.point_items.append(point_marker)
        self.update_polygon()
        print(f"Added point: ({x}, {y})")
        return True
    
    def finalize_polygon(self):
        """Finalize the current polygon"""
        if len(self.polygon_points) < 3:
            self.toast.emit("Polygon must have at least 3 points")
            print("Cannot finalize polygon: must have at least 3 points")
            return
        
        start_point = self.polygon_points[0]
        last_point = self.polygon_points[-1]
        if abs(start_point.x() - last_point.x()) > 0.001 or abs(start_point.y() - last_point.y()) > 0.001:
            self.toast.emit("Polygon must be closed by selecting the starting point")
            print("Cannot finalize polygon: last point must match the starting point")
            return
        
        # Store the finished polygon
        self.finished_polygon = [QPointF(p) for p in self.polygon_points[:-1]]  # Remove duplicate closing point
        
        # Update visual representation
        if self.current_polygon:
            self.scene.removeItem(self.current_polygon)
            poly = QPolygonF(self.finished_polygon)
            self.current_polygon = self.scene.addPolygon(
                poly,
                QPen(QColor(0, 150, 0, 255), 3/self.transform().m11()),
                # QBrush(QColor(0, 255, 0, 100))
            )
        
        # Clear point markers and working polygon
        for marker in self.point_items:
            self.scene.removeItem(marker)
        self.point_items = []
        self.polygon_points = []
        
        self.toast.emit("Polygon finalized! Use 'Decompose to Rectangles' to see the breakdown.")
        print("Polygon finalized")
    
    def clear_polygon(self):
        """Швидко очищає сцену та всі пов’язані дані."""
        self.scene.clear()  # миттєво видаляє всі графічні елементи

        # Скидаємо лише змінні
        self.point_items.clear()
        self.polygon_points.clear()
        self.decomposition_rectangles.clear()
        self.current_polygon = None
        self.finished_polygon = None

        self.toast.emit("Polygon cleared")
        print("Polygon cleared")
    
    def decompose_polygon(self):
        start = round(time.time() * 1000)
        """Decompose the finished polygon into rectangles"""
        if self.finished_polygon is None:
            self.toast.emit("No finished polygon to decompose. Finish a polygon first.")
            return
        
        # Clear previous decomposition
        for rect_item in self.decomposition_rectangles:
            self.scene.removeItem(rect_item)
        self.decomposition_rectangles.clear()
        
        # Convert QPointF to tuples for the algorithm
        polygon_tuples = [(p.x(), p.y()) for p in self.finished_polygon]
        
        # Apply decomposition algorithm
        try:
            # rectangles = decompose_polygon(polygon_tuples)
            rectangles = decompose_polygon_sweep(polygon_tuples)
            
            if rectangles:
                # Visualize rectangles
                for i, ((x1, y1), (x2, y2)) in enumerate(rectangles):
                    rect = QRectF(x1, y1, x2 - x1, y2 - y1)
                    
                    # Different colors for each rectangle
                    colors = [
                        QColor(255, 100, 100, 150),  # Light red
                        QColor(100, 255, 100, 150),  # Light green
                        QColor(100, 100, 255, 150),  # Light blue
                        QColor(255, 255, 100, 150),  # Light yellow
                        QColor(255, 100, 255, 150),  # Light magenta
                        QColor(100, 255, 255, 150),  # Light cyan
                    ]
                    
                    color = colors[i % len(colors)]
                    
                    rect_item = self.scene.addRect(
                        rect,
                        QPen(QColor(0, 0, 0, 200), 2/self.transform().m11()),
                        QBrush(color)
                    )
                    self.decomposition_rectangles.append(rect_item)
                
                self.toast.emit(f"Decomposed into {len(rectangles)} rectangles")
                print(f"Decomposed polygon into {len(rectangles)} rectangles")
                # print(rectangles)
            else:
                self.toast.emit("No rectangles found in decomposition")
                print("No rectangles found in decomposition")
                
        except Exception as e:
            self.toast.emit(f"Decomposition failed: {str(e)}")
            print(f"Decomposition error: {e}")
    

    def generate_large_polygon(self):
        """Генерує один ізотетичний багатокутник з приблизно 10 000 вершин."""
        self.clear_polygon()

        # Параметри
        num_vertices = 10_000
        grid_size = self.get_adaptive_grid_size()
        start_x = round(random.uniform(-1000, 1000) / grid_size) * grid_size
        start_y = round(random.uniform(-1000, 1000) / grid_size) * grid_size
        current_x, current_y = start_x, start_y
        is_horizontal = random.choice([True, False])
        points = [QPointF(current_x, current_y)]

        for _ in range(num_vertices - 1):
            step = random.uniform(grid_size * 2, grid_size * 5)
            if is_horizontal:
                current_x += random.choice([-step, step])
                current_x = round(current_x / grid_size) * grid_size
            else:
                current_y += random.choice([-step, step])
                current_y = round(current_y / grid_size) * grid_size
            points.append(QPointF(current_x, current_y))
            is_horizontal = not is_horizontal

        # Замикання багатокутника
        if abs(current_x - start_x) < 0.001:
            points.append(QPointF(start_x, start_y))
        elif abs(current_y - start_y) < 0.001:
            points.append(QPointF(start_x, start_y))
        else:
            points.append(QPointF(current_x, start_y))
            points.append(QPointF(start_x, start_y))

        self.polygon_points = points
        self.update_polygon()
        self.finalize_polygon()

        self.toast.emit(f"Generated 1 large isothetic polygon with {len(points)} vertices")
        print(f"Generated 1 large isothetic polygon with {len(points)} vertices")
        self.viewport().update()


    def export_data(self, filename):
        """Export polygon and decomposition data to JSON file"""
        data = {
            "polygon": [],
            "rectangles": []
        }
        
        if self.finished_polygon:
            data["polygon"] = [(p.x(), p.y()) for p in self.finished_polygon]
        
        # Export rectangle data if decomposition exists
        if self.decomposition_rectangles:
            polygon_tuples = [(p.x(), p.y()) for p in self.finished_polygon]
            rectangles = decompose_polygon_sweep(polygon_tuples)
            data["rectangles"] = [{"top_left": [x1, y1], "bottom_right": [x2, y2]} 
                                for (x1, y1), (x2, y2) in rectangles]
        
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"Data exported to {filename}")

    def import_data(self, filename):
        """Import polygon data from JSON file"""
        try:
            with open(filename, 'r') as f:
                data = json.load(f)
            
            if "polygon" not in data or not data["polygon"]:
                raise ValueError("No polygon data found in file")
            
            # Clear existing data
            self.clear_polygon()
            
            # Import polygon points
            polygon_points = data["polygon"]
            for x, y in polygon_points:
                self.add_polygon_point(x, y)
            
            # Close the polygon by adding the first point again
            if polygon_points:
                first_x, first_y = polygon_points[0]
                self.add_polygon_point(first_x, first_y)
            
            # Finalize the polygon
            self.finalize_polygon()
            
            # If rectangles data exists, show decomposition
            if "rectangles" in data and data["rectangles"]:
                self.decompose_polygon()
            
            print(f"Data imported from {filename}")
            
        except Exception as e:
            raise Exception(f"Import failed: {str(e)}")