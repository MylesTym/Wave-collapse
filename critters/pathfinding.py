import heapq
import math
from typing import List, Tuple, Dict, Set, Optional
from .map_interface import WFCMapInterface

class PathNode:
    def __init__(self, position: Tuple[int, int], g_cost: float = 0, h_cost: float = 0, parent: Optional['PathNode'] = None):
        self.position = position
        self.g_cost = g_cost
        self.h_cost = h_cost
        self.f_cost = g_cost + h_cost
        self.parent = parent

    def __lt__(self, other):
        if self.f_cost == other.f_cost:
            return self.h_cost < other.h_cost
        return self.f_cost < other.f_cost
    
    def __eq__(self, other):
        return isinstance(other, PathNode) and self.position == other.position
    
    def __hash__(self):
        return hash(self.position)
    

class AStarPathfinder:

        def __init__(self, map_interface: WFCMapInterface):
            self.map_interface = map_interface
            self.max_iterations = 1000 ## prevent infinite loops, may decrease

        def find_path(self, start: Tuple[int, int], goal: Tuple[int, int]) -> List[Tuple[int, int]]:
            if not self.map_interface.is_walkable(*start):
                return[]
            if not self.map_interface.is_walkable(*goal):
                return []
            if start == goal:
                return [start]
            
            #Init
            open_set = []
            closed_set: Set[Tuple[int, int]] = set()
            nodes: Dict[Tuple[int, int], PathNode] = {}
            #Start
            start_node = PathNode(start, 0, self.heuristic(start, goal))
            nodes[start] = start_node
            heapq.heappush(open_set, start_node)

            iterations = 0

            while open_set and iterations < self.max_iterations:
                iterations += 1
                current_node = heapq.heappop(open_set)
                current_pos = current_node.position

                if current_pos == goal:
                    return self.reconstruct_path(current_node)
                closed_set.add(current_pos)

                for neighbor_pos in self.get_neighbors(current_pos):
                    if neighbor_pos in closed_set:
                        continue
                    if not self.map_interface.is_walkable(*neighbor_pos):
                        continue

                    movement_cost = self.get_movement_cost(current_pos, neighbor_pos)
                    tentative_g = current_node.g_cost + movement_cost

                    if neighbor_pos in nodes:
                        neighbor_node = nodes[neighbor_pos]
                        if tentative_g < neighbor_node.g_cost:
                            neighbor_node.g_cost = tentative_g
                            neighbor_node.f_cost = tentative_g + neighbor_node.h_cost
                            neighbor_node.parent = current_node
                            heapq.heappush(open_set, neighbor_node)
                    else:
                        h_cost = self.heuristic(neighbor_pos, goal)
                        neighbor_node = PathNode(neighbor_pos, tentative_g, h_cost, current_node)
                        nodes[neighbor_pos] = neighbor_node
                        heapq.heappush(open_set, neighbor_node)

            return[]
        
        def get_neighbors(self, position: Tuple[int, int]) -> List[Tuple[int, int]]:
            x, y = position
            neighbors = []
            directions = [(0, -1), (1, 0), (0, 1), (-1, 0)]

            for dx, dy in directions:
                new_pos = (x + dx, y + dy)
                if self.map_interface.is_valid_position(*new_pos):
                    neighbors.append(new_pos)

            return neighbors
        
        def get_neighbors_8_dir(self, position: Tuple[int, int]) -> List[Tuple[int, int]]:
            x, y = position
            neighbors = []

            ## 8 directional movement ##
            directions = [
                (0, -1), (1, -1), (1, 0), (1, 1),
                (0, 1), (-1, 1), (-1, 0), (-1, -1)
            ]

            for dx, dy in directions: 
                new_pos = (x +dx, y + dy)
                if self.map_interface.is_valid_position(*new_pos):
                    neighbors.append(new_pos)

            return neighbors
        
        def get_movement_cost(self, from_pos: Tuple[int, int], to_pos: Tuple[int, int]) -> float:
            dx = abs(to_pos[0] - from_pos[0])
            dy = abs(to_pos[1] - from_pos[1])

            if dx == 1 and dy == 1:
                return math.sqrt(2)
            else:
                return 1.0
            
        def heuristic(self, pos: Tuple[int, int], goal: Tuple[int, int]) -> float:
            return abs(pos[0] - goal[0]) + abs(pos[1] - goal[1])
        
        def heuristic_euclidean(self, pos: Tuple[int, int], goal: Tuple[int, int]) -> float:
            dx = pos[0] - goal[0]
            dy = pos[1] - goal[1]
            return math.sqrt(dx * dx + dy * dy)
        
        def reconstruct_path(self, goal_node: PathNode) -> List[Tuple[int, int]]:
            path = []
            current = goal_node

            while current is not None:
                path.append(current.position)
                current = current.parent

            path.reverse()
            return path

        def find_path_8_dir(self, start: Tuple[int, int], goal: Tuple[int, int]) -> List[Tuple[int, int]]:
            if not self.map_interface.is_walkable(*start):
                return []
            if not self.map_interface.is_walkable(*goal):
                return []
            if start == goal:
                return [start]
            
            open_set = []
            closed_set: Set[Tuple[int, int]] = set()
            nodes: Dict[Tuple[int, int], PathNode] = {}

            start_node = PathNode(start, 0, self.heuristic_euclidean(start, goal))
            nodes[start] = start_node
            heapq.heappush(open_set, start_node)
            iterations = 0

            while open_set and iterations < self.max_iterations:
                iterations += 1

                current_node = heapq.heappop(open_set)
                current_pos = current_node.position

                if current_pos == goal:
                    return self.reconstruct_path(current_node)
                closed_set.add(current_pos)

                for neighbor_pos in self.get_neighbors_8_dir(current_pos):
                    if neighbor_pos in closed_set:
                        continue

                    if not self.map_interface.is_walkable(*neighbor_pos):
                        continue

                    movement_cost = self.get_movement_cost(current_pos, neighbor_pos)
                    tentative_g = current_node.g_cost + movement_cost

                    if neighbor_pos in nodes:
                        neighbor_node = nodes[neighbor_pos]
                        if tentative_g < neighbor_node.g_cost:
                            neighbor_node.g_cost = tentative_g
                            neighbor_node.f_cost = tentative_g + neighbor_node.h_cost
                            neighbor_node.parent = current_node
                            heapq.heappush(open_set, neighbor_node)

                    else:
                        h_cost = self.heuristic_euclidean(neighbor_pos, goal)
                        neighbor_node = PathNode(neighbor_pos, tentative_g, h_cost, current_node)
                        nodes[neighbor_pos] = neighbor_node
                        heapq.heappush(open_set, neighbor_node)

            return []
        
        def is_path_clear(self, start: Tuple[int, int], goal: Tuple[ int, int]) -> bool:
            points = self.bresenham_line(start, goal)
            return all(self.map_interface.is_walkable(*point) for point in points)
        
        def bresenham_line(self, start: Tuple[int, int], goal: Tuple[int, int]) -> List[Tuple[int, int]]:
            x0, y0 = start
            x1, y1 = goal

            points = []
            dx = abs(x1 - x0)
            dy = abs(y1 - y0)

            x_step = 1 if x0 < x1 else -1
            y_step = 1 if y0 < y1 else -1

            error = dx - dy

            while True:
                points.append((x0, y0))

                if x0 == x1 and y0 == y1:
                    break
                e2 = 2 * error
                if e2 > -dy:
                    error -= dy
                    x0 += x_step
                if e2 < dx:
                    error += dx
                    y0 += y_step
            return points
