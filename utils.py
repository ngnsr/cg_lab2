import time
import math
import random
from typing import List, Tuple
from sortedcontainers import SortedList

def decompose_polygon_sweep(polygon: List[Tuple[int, int]]) -> List[Tuple[Tuple[int, int], Tuple[int, int]]]:
    start = round(time.time() * 1000)
    """Розбивка ізотетичного полігону на прямокутники з оптимізованою складністю O(n log n)."""
    if len(polygon) < 3:
        return []

    events = []
    n = len(polygon)
    for i in range(n):
        p1 = polygon[i]
        p2 = polygon[(i + 1) % n]
        if p1[0] == p2[0]:  # Вертикальне ребро
            y_start, y_end = min(p1[1], p2[1]), max(p1[1], p2[1])
            events.append((y_start, 'start', p1[0]))  # Початок ребра
            events.append((y_end, 'end', p1[0]))      # Кінець ребра

    # Сортуємо події за Y-координатою
    events.sort()  # O(n log n)

    rectangles = []
    active_edges = SortedList()  # Використовуємо SortedList для активних ребер
    prev_y = None

    # Обробляємо події
    for y, event_type, x in events:
        if prev_y is not None and active_edges:
            # Замість перебору всіх пар, ми знаємо, що ребра чергуються (ліве-праве-ліве-...)
            # Тому ми можемо просто взяти парні та непарні індекси
            edges = list(active_edges)
            for i in range(0, len(edges) - 1, 2):
                x_start = edges[i]
                x_end = edges[i + 1]
                rectangles.append(((x_start, prev_y), (x_end, y)))

        # Оновлюємо активні ребра
        if event_type == 'start':
            active_edges.add(x)  # O(log k)
        else:  # event_type == 'end'
            active_edges.remove(x)  # O(log k)

        prev_y = y

    print('Took : ', round(time.time() * 1000) - start, 'ms')
    return rectangles


def generate_large_isothetic_polygon(num_vertices=10000, min_distance=10):
    """
    Генерує ізотетичний багатокутник з приблизно заданою кількістю вершин.
    
    Args:
        num_vertices: Приблизна кількість вершин у багатокутнику
        min_distance: Мінімальна відстань між сусідніми вершинами
    
    Returns:
        List[Tuple[int, int]]: Список координат вершин багатокутника
    """
    # Визначаємо базовий розмір і центр
    base_size = 5000
    center_x, center_y = 0, 0
    
    # Кількість "зубців" на кожній стороні
    teeth_per_side = math.ceil(num_vertices / 16)
    
    # Розмір одного "зубця"
    tooth_size = max(base_size // (teeth_per_side), min_distance * 4)
    
    points = []
    
    # Функція для додавання точки, уникаючи дублікатів
    def add_point(x, y):
        if not points or (points[-1][0] != x or points[-1][1] != y):
            points.append((x, y))
    
    # Нижня сторона (зліва направо)
    x = center_x - base_size
    y = center_y - base_size
    add_point(x, y)
    
    for i in range(teeth_per_side):
        # Крок вправо
        x += tooth_size
        add_point(x, y)
        
        # Крок вгору
        y_offset = random.randint(max(min_distance, tooth_size // 4), tooth_size // 2)
        add_point(x, y + y_offset)
        
        # Ще крок вправо
        x += tooth_size
        add_point(x, y + y_offset)
        
        # Крок вниз (повернення на базову лінію)
        add_point(x, y)
    
    # Правий нижній кут
    x = center_x + base_size
    add_point(x, y)
    
    # Права сторона (знизу вгору)
    for i in range(teeth_per_side):
        # Крок вгору
        y += tooth_size
        add_point(x, y)
        
        # Крок вліво
        x_offset = random.randint(max(min_distance, tooth_size // 4), tooth_size // 2)
        add_point(x - x_offset, y)
        
        # Ще крок вгору
        y += tooth_size
        add_point(x - x_offset, y)
        
        # Крок вправо (повернення на базову лінію)
        add_point(x, y)
    
    # Правий верхній кут
    y = center_y + base_size
    add_point(x, y)
    
    # Верхня сторона (справа наліво)
    for i in range(teeth_per_side):
        # Крок вліво
        x -= tooth_size
        add_point(x, y)
        
        # Крок вниз
        y_offset = random.randint(max(min_distance, tooth_size // 4), tooth_size // 2)
        add_point(x, y - y_offset)
        
        # Ще крок вліво
        x -= tooth_size
        add_point(x, y - y_offset)
        
        # Крок вгору (повернення на базову лінію)
        add_point(x, y)
    
    # Лівий верхній кут
    x = center_x - base_size
    add_point(x, y)
    
    # Ліва сторона (зверху вниз)
    for i in range(teeth_per_side):
        # Крок вниз
        y -= tooth_size
        add_point(x, y)
        
        # Крок вправо
        x_offset = random.randint(max(min_distance, tooth_size // 4), tooth_size // 2)
        add_point(x + x_offset, y)
        
        # Ще крок вниз
        y -= tooth_size
        add_point(x + x_offset, y)
        
        # Крок вліво (повернення на базову лінію)
        add_point(x, y)
    
    # Не додаємо останню точку, якщо вона співпадає з першою
    if points[0] != (x, y):
        add_point(points[0][0], points[0][1])
    
    return points