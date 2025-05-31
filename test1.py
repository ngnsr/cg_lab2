import numpy as np
import matplotlib.pyplot as plt
from typing import List, Tuple, Optional
import math

class Point:
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y
    
    def __repr__(self):
        return f"Point({self.x:.2f}, {self.y:.2f})"
    
    def distance_to(self, other):
        return math.sqrt((self.x - other.x)**2 + (self.y - other.y)**2)

class Rectangle:
    def __init__(self, vertices: List[Point]):
        self.vertices = vertices  # Чотири вершини прямокутника
        # Обчислюємо ширину, висоту та площу
        self.width = self.vertices[1].distance_to(self.vertices[0])
        self.height = self.vertices[2].distance_to(self.vertices[1])
        self.area = self.width * self.height
    
    def __repr__(self):
        return f"Rectangle(area={self.area:.2f}, width={self.width:.2f}, height={self.height:.2f})"
    
    def get_vertices(self):
        return self.vertices

class ConvexHullRectangleFinder:
    def __init__(self, convex_hull: List[Point]):
        self.hull = convex_hull
        self.n = len(convex_hull)
        
    def find_max_inscribed_rectangle_rotated(self) -> Optional[Rectangle]:
        """Знаходить максимальний вписаний прямокутник із довільною орієнтацією."""
        max_rectangle = None
        max_area = 0
        alpha = 0  # Початковий кут (паралельно осі OX)
        total_alpha = 0  # Загальний кут обертання
        epsilon = 1e-6  # Маленький запас для помилок з плаваючою точкою

        # Початковий прямокутник (для alpha = 0)
        initial_rect = self._find_rectangle_axis_aligned()
        if initial_rect:
            max_rectangle = initial_rect
            max_area = initial_rect.area

        # Ітеративно розглядаємо всі напрямки
        visited_edges = [0, 0, 0]  # Індекси ребер для трьох вершин (A, B, C)
        current_points = [self.hull[0], self.hull[1], self.hull[2]]  # Початкові точки A, B, C

        while True:
            # Знаходимо мінімальний кут повороту для зміщення однієї з вершин до наступної вершини багатокутника
            sigma, next_points, next_edges = self._find_min_rotation_angle(current_points, visited_edges, alpha)
            if sigma is None:  # Усі напрямки розглянуто
                break

            # Оновлюємо загальний кут обертання
            total_alpha += sigma
            if total_alpha > 2 * math.pi + epsilon:
                break

            # Знаходимо максимальний прямокутник для діапазону [alpha, alpha + sigma]
            rect = self._find_rectangle_for_angle_range(alpha, alpha + sigma, next_points, next_edges)
            if rect and rect.area > max_area:
                max_area = rect.area
                max_rectangle = rect

            # Оновлюємо кут і точки
            alpha += sigma
            current_points = next_points
            visited_edges = next_edges

        return max_rectangle
    
    def _find_rectangle_axis_aligned(self) -> Optional[Rectangle]:
        """Знаходить максимальний прямокутник, паралельний осям (початковий етап)."""
        rect_type1 = self._find_rectangle_with_secant_line(from_top=True)
        rect_type2 = self._find_rectangle_with_secant_line(from_top=False)
        
        if rect_type1 and rect_type2:
            return rect_type1 if rect_type1.area >= rect_type2.area else rect_type2
        return rect_type1 or rect_type2
    
    def _find_min_rotation_angle(self, points: List[Point], edges: List[int], alpha: float) -> Tuple[Optional[float], List[Point], List[int]]:
        """Знаходить мінімальний кут повороту для зміщення однієї з вершин до наступної вершини багатокутника."""
        min_sigma = float('inf')
        next_points = points.copy()
        next_edges = edges.copy()
        min_idx = -1
        
        # Центр прямокутника (приблизно центр мас трьох точок)
        center = Point(sum(p.x for p in points) / 3, sum(p.y for p in points) / 3)
        
        for i in range(3):
            curr_point = points[i]
            curr_edge = edges[i]
            next_vertex = self.hull[(curr_edge + 1) % self.n]
            
            # Обчислюємо кут повороту до наступної вершини
            curr_vec = (curr_point.x - center.x, curr_point.y - center.y)
            next_vec = (next_vertex.x - center.x, next_vertex.y - center.y)
            
            curr_angle = math.atan2(curr_vec[1], curr_vec[0])
            next_angle = math.atan2(next_vec[1], next_vec[0])
            sigma = next_angle - curr_angle
            if sigma < 0:
                sigma += 2 * math.pi
            
            if sigma < min_sigma:
                min_sigma = sigma
                min_idx = i
                next_points[i] = next_vertex
                next_edges[i] = (curr_edge + 1) % self.n
        
        if min_idx == -1:
            return None, points, edges
        
        return min_sigma, next_points, next_edges
    
    def _find_rectangle_for_angle_range(self, alpha_start: float, alpha_end: float, points: List[Point], edges: List[int]) -> Optional[Rectangle]:
        """Знаходить максимальний прямокутник для діапазону кутів [alpha_start, alpha_end]."""
        # Вектори напрямків для сторін прямокутника
        dir1 = (math.cos(alpha_start), math.sin(alpha_start))  # Основна вісь
        dir2 = (-math.sin(alpha_start), math.cos(alpha_start))  # Перпендикулярна вісь
        
        # Знаходимо екстремальні точки для кожної сторони
        min_d1, max_d1 = float('inf'), float('-inf')
        min_d2, max_d2 = float('inf'), float('-inf')
        min_d1_point, max_d1_point = None, None
        min_d2_point, max_d2_point = None, None
        
        for p in self.hull:
            proj1 = p.x * dir1[0] + p.y * dir1[1]
            proj2 = p.x * dir2[0] + p.y * dir2[1]
            
            if proj1 < min_d1:
                min_d1 = proj1
                min_d1_point = p
            if proj1 > max_d1:
                max_d1 = proj1
                max_d1_point = p
            if proj2 < min_d2:
                min_d2 = proj2
                min_d2_point = p
            if proj2 > max_d2:
                max_d2 = proj2
                max_d2_point = p
        
        # Формуємо вершини прямокутника
        vertices = [
            Point(min_d1_point.x, min_d1_point.y),  # A
            Point(max_d1_point.x, max_d1_point.y),  # B
            Point(max_d1_point.x + (max_d2 - min_d2) * dir2[0], max_d1_point.y + (max_d2 - min_d2) * dir2[1]),  # C
            Point(min_d1_point.x + (max_d2 - min_d2) * dir2[0], min_d1_point.y + (max_d2 - min_d2) * dir2[1])   # D
        ]
        
        # Перевіряємо вкладеність четвертої вершини
        if self._point_in_polygon(vertices[3]):
            return Rectangle(vertices)
        # Пробуємо протилежний напрямок (alpha + 180°)
        dir1 = (math.cos(alpha_start + math.pi), math.sin(alpha_start + math.pi))
        dir2 = (-math.sin(alpha_start + math.pi), math.cos(alpha_start + math.pi))
        
        min_d1, max_d1 = float('inf'), float('-inf')
        min_d2, max_d2 = float('inf'), float('-inf')
        min_d1_point, max_d1_point = None, None
        min_d2_point, max_d2_point = None, None
        
        for p in self.hull:
            proj1 = p.x * dir1[0] + p.y * dir1[1]
            proj2 = p.x * dir2[0] + p.y * dir2[1]
            
            if proj1 < min_d1:
                min_d1 = proj1
                min_d1_point = p
            if proj1 > max_d1:
                max_d1 = proj1
                max_d1_point = p
            if proj2 < min_d2:
                min_d2 = proj2
                min_d2_point = p
            if proj2 > max_d2:
                max_d2 = proj2
                max_d2_point = p
        
        vertices = [
            Point(min_d1_point.x, min_d1_point.y),
            Point(max_d1_point.x, max_d1_point.y),
            Point(max_d1_point.x + (max_d2 - min_d2) * dir2[0], max_d1_point.y + (max_d2 - min_d2) * dir2[1]),
            Point(min_d1_point.x + (max_d2 - min_d2) * dir2[0], min_d1_point.y + (max_d2 - min_d2) * dir2[1])
        ]
        
        if self._point_in_polygon(vertices[3]):
            return Rectangle(vertices)
        return None
    
    def _find_rectangle_with_secant_line(self, from_top: bool) -> Optional[Rectangle]:
        """Знаходить прямокутник за допомогою січної прямої (для осей OX/OY)."""
        start_y = max(p.y for p in self.hull) if from_top else min(p.y for p in self.hull)
        end_y = min(p.y for p in self.hull) if from_top else max(p.y for p in self.hull)
        y_step = -0.01 if from_top else 0.01
        
        max_rectangle = None
        current_y = start_y
        
        while (from_top and current_y >= end_y) or (not from_top and current_y <= end_y):
            intersections = self._find_secant_intersections(current_y)
            
            if len(intersections) >= 2:
                rect = self._build_rectangle_at_y(current_y, intersections, from_top)
                if rect and (not max_rectangle or rect.area > max_rectangle.area):
                    max_rectangle = rect
            current_y += y_step
        
        return max_rectangle
    
    def _find_secant_intersections(self, y: float) -> List[Point]:
        """Знаходить точки перетину горизонтальної лінії з багатокутником."""
        intersections = []
        for i in range(self.n):
            p1 = self.hull[i]
            p2 = self.hull[(i + 1) % self.n]
            if (p1.y <= y <= p2.y) or (p2.y <= y <= p1.y):
                if abs(p1.y - p2.y) < 1e-9:
                    intersections.extend([p1, p2])
                else:
                    t = (y - p1.y) / (p2.y - p1.y)
                    x = p1.x + t * (p2.x - p1.x)
                    intersections.append(Point(x, y))
        
        intersections.sort(key=lambda p: p.x)
        unique_intersections = []
        for p in intersections:
            if not unique_intersections or abs(p.x - unique_intersections[-1].x) > 1e-9:
                unique_intersections.append(p)
        return unique_intersections
    
    def _build_rectangle_at_y(self, y: float, intersections: List[Point], from_top: bool) -> Optional[Rectangle]:
        """Будує максимальний прямокутник для заданого y."""
        if len(intersections) < 2:
            return None
        left_x = intersections[0].x
        right_x = intersections[-1].x
        if from_top:
            bottom_y = self._find_max_bottom_y(left_x, right_x, y)
            if bottom_y is None:
                return None
            vertices = [
                Point(left_x, bottom_y),
                Point(right_x, bottom_y),
                Point(right_x, y),
                Point(left_x, y)
            ]
            return Rectangle(vertices)
        else:
            top_y = self._find_min_top_y(left_x, right_x, y)
            if top_y is None:
                return None
            vertices = [
                Point(left_x, y),
                Point(right_x, y),
                Point(right_x, top_y),
                Point(left_x, top_y)
            ]
            return Rectangle(vertices)
    
    def _find_max_bottom_y(self, left_x: float, right_x: float, top_y: float) -> Optional[float]:
        """Знаходить найни:

жчу можливу y-координату для нижньої сторони прямокутника."""
        max_bottom_y = float('-inf')
        for i in range(self.n):
            p1 = self.hull[i]
            p2 = self.hull[(i + 1) % self.n]
            constraint_y = self._get_y_constraint_from_edge(p1, p2, left_x, right_x, top_y, True)
            if constraint_y is not None:
                max_bottom_y = max(max_bottom_y, constraint_y)
        return max_bottom_y if max_bottom_y != float('-inf') else None
    
    def _find_min_top_y(self, left_x: float, right_x: float, bottom_y: float) -> Optional[float]:
        """Знаходить найвищу можливу y-координату для верхньої сторони прямокутника."""
        min_top_y = float('inf')
        for i in range(self.n):
            p1 = self.hull[i]
            p2 = self.hull[(i + 1) % self.n]
            constraint_y = self._get_y_constraint_from_edge(p1, p2, left_x, right_x, bottom_y, False)
            if constraint_y is not None:
                min_top_y = min(min_top_y, constraint_y)
        return min_top_y if min_top_y != float('inf') else None
    
    def _get_y_constraint_from_edge(self, p1: Point, p2: Point, left_x: float, right_x: float, 
                                  fixed_y: float, is_bottom: bool) -> Optional[float]:
        """Отримує обмеження y від ребра багатокутника."""
        min_edge_x = min(p1.x, p2.x)
        max_edge_x = max(p1.x, p2.x)
        if max_edge_x < left_x or min_edge_x > right_x:
            return None
        if abs(p1.x - p2.x) < 1e-9:
            if left_x <= p1.x <= right_x:
                return min(p1.y, p2.y) if is_bottom else max(p1.y, p2.y)
            return None
        edge_min_y = min(p1.y, p2.y)
        edge_max_y = max(p1.y, p2.y)
        if is_bottom:
            return edge_max_y if edge_max_y < fixed_y else None
        else:
            return edge_min_y if edge_min_y > fixed_y else None
    
    def _point_in_polygon(self, point: Point) -> bool:
        """Перевіряє, чи точка знаходиться всередині багатокутника."""
        x, y = point.x, point.y
        n = len(self.hull)
        inside = False
        p1x, p1y = self.hull[0].x, self.hull[0].y
        for i in range(1, n + 1):
            p2x, p2y = self.hull[i % n].x, self.hull[i % n].y
            if y > min(p1y, p2y):
                if y <= max(p1y, p2y):
                    if x <= max(p1x, p2x):
                        if p1y != p2y:
                            xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                        if p1x == p2x or x <= xinters:
                            inside = not inside
            p1x, p1y = p2x, p2y
        return inside

def graham_scan(points: List[Point]) -> List[Point]:
    """Алгоритм Грехема для побудови опуклої оболонки."""
    def cross_product(o, a, b):
        return (a.x - o.x) * (b.y - o.y) - (a.y - o.y) * (b.x - o.x)
    
    def polar_angle(p0, p1):
        return math.atan2(p1.y - p0.y, p1.x - p0.x)
    
    start = min(points, key=lambda p: (p.y, p.x))
    sorted_points = sorted([p for p in points if p != start], 
                          key=lambda p: (polar_angle(start, p), start.distance_to(p)))
    
    hull = [start]
    for p in sorted_points:
        while len(hull) > 1 and cross_product(hull[-2], hull[-1], p) < 0:
            hull.pop()
        hull.append(p)
    
    return hull

def visualize_result(hull: List[Point], rectangle: Rectangle):
    """Візуалізація результату."""
    fig, ax = plt.subplots(1, 1, figsize=(10, 8))
    
    hull_x = [p.x for p in hull] + [hull[0].x]
    hull_y = [p.y for p in hull] + [hull[0].y]
    ax.plot(hull_x, hull_y, 'b-', linewidth=2, label='Опукла оболонка')
    ax.scatter([p.x for p in hull], [p.y for p in hull], c='blue', s=50)
    
    rect_vertices = rectangle.get_vertices()
    rect_x = [v.x for v in rect_vertices] + [rect_vertices[0].x]
    rect_y = [v.y for v in rect_vertices] + [rect_vertices[0].y]
    ax.plot(rect_x, rect_y, 'r-', linewidth=2, label=f'Максимальний прямокутник (площа: {rectangle.area:.2f})')
    ax.fill(rect_x, rect_y, alpha=0.3, color='red')
    
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_title('Максимальний вписаний прямокутник в опуклу оболонку')
    ax.legend()
    ax.grid(True, alpha=0.3)
    ax.set_aspect('equal')
    
    plt.tight_layout()
    plt.show()

# Приклад використання
if __name__ == "__main__":
    np.random.seed(42)
    n_points = 15
    points = []
    
    points = [
        Point(0, 0),      # A
        Point(2, 1),      # B
        Point(1, 3),      # C
        Point(-1, 2)      # D
    ]
    
    print(f"Згенеровано {len(points)} точок")
    
    hull = graham_scan(points)
    print(f"Опукла оболонка містить {len(hull)} точок")
    
    finder = ConvexHullRectangleFinder(hull)
    max_rectangle = finder.find_max_inscribed_rectangle_rotated()
    
    if max_rectangle:
        print(f"Знайдений прямокутник: {max_rectangle}")
        print(f"Розміри: {max_rectangle.width:.2f} x {max_rectangle.height:.2f}")
        print(f"Площа: {max_rectangle.area:.2f}")
        visualize_result(hull, max_rectangle)
    else:
        print("Не вдалося знайти вписаний прямокутник")