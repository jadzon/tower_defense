from PyQt6 import QtWidgets
from PyQt6.QtGui import QBrush, QColor, QPixmap
from PyQt6.QtWidgets import QApplication, QMainWindow, QGraphicsScene, QGraphicsView, QGraphicsItem
from PyQt6.QtCore import QRectF, Qt, QEvent, QPoint, QRect
import random
import sys
import os
import math


class MyWindow(QMainWindow):
    def __init__(self):
        super(MyWindow, self).__init__()
        self.setWindowTitle("Army Defense")
        self.initScreen()
        self.initGameBoard()

    def initScreen(self):
        screen = QApplication.primaryScreen()
        available_geometry = screen.availableGeometry()

        width = int(available_geometry.width() * 0.8)
        height = int(available_geometry.height() * 0.8)
        x = int(width * 0.1)
        y = int(height * 0.1)

        self.setGeometry(x, y, width, height)
        print(f"Setting window at: {x},{y} with size {width}x{height}")

    def initGameBoard(self):
        self.scene = QGraphicsScene(self)
        self.view = QGraphicsView(self.scene, self)
        self.view.setGeometry(0, 0, self.width(), self.height())


        self.view.setMouseTracking(True)


        self.view.setDragMode(QGraphicsView.DragMode.NoDrag)


        self.is_middle_pressed = False
        self.last_pos = None


        self.loadTilesetTextures()

        self.generateMap()
        map_width = self.grid_size * self.tile_size
        map_height = self.grid_size * self.tile_size
        self.scene.setSceneRect(0, 0, map_width, map_height)


        self.view.fitInView(self.scene.sceneRect(), Qt.AspectRatioMode.KeepAspectRatio)


        self.initial_transform = self.view.transform()


        self.view.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.view.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)


        self.view.viewport().installEventFilter(self)

    def loadTilesetTextures(self):
        self.textures = {}

        # Main terrain tileset paths
        tileset_path = "./assets/textures/tiles.png"
        water_tile_path = "./assets/textures/water_tile.png"

        # Object texture paths
        tree_path = "./assets/textures/Small Forest Asset Pack/Trees/Tree-2/Tree-2-4.png"
        rock_path = "./assets/textures/Small Forest Asset Pack/Stones/Stone-1.png"

        # Fallback colors if textures not found
        if not os.path.exists(tileset_path):
            print(f"Tileset not found at {tileset_path}, using fallback colors")

            # Terrain fallbacks
            self.textures['grass'] = QBrush(QColor(50, 180, 50))
            self.textures['water'] = QBrush(QColor(0, 0, 150))
            self.textures['sand'] = QBrush(QColor(240, 220, 130))

            # Object fallbacks
            self.textures['tree'] = QBrush(QColor(0, 100, 0))  # Dark green for trees
            self.textures['rock'] = QBrush(QColor(120, 120, 120))  # Gray for rocks
            return

        # Load the terrain tilesets
        tileset = QPixmap(tileset_path)
        if tileset.isNull():
            print("Error while loading terrain tileset")
            return

        water_tile = QPixmap(water_tile_path)
        if water_tile.isNull():
            print("Error while loading water tileset")
            return

        # Extract terrain textures
        meadow_tile = tileset.copy(QRect(0, 0, 16, 16))
        self.textures['grass'] = QBrush(meadow_tile)

        ocean_tile = water_tile.copy(QRect(0, 0, 16, 16))
        self.textures['water'] = QBrush(ocean_tile)

        sand_tile = tileset.copy(QRect(144, 32, 16, 16))
        self.textures['sand'] = QBrush(sand_tile)

        # Load object pixmaps directly (not as brushes)
        if os.path.exists(tree_path):
            tree_pixmap = QPixmap(tree_path)
            if not tree_pixmap.isNull():
                # Store the pixmap directly instead of a brush
                self.textures['tree_pixmap'] = tree_pixmap
                print("Successfully loaded tree texture")
            else:
                print("Error loading tree texture, using fallback")
                self.textures['tree'] = QBrush(QColor(0, 100, 0))  # Dark green fallback
        else:
            print(f"Tree texture not found at {tree_path}, using fallback color")
            self.textures['tree'] = QBrush(QColor(0, 100, 0))  # Dark green fallback

        if os.path.exists(rock_path):
            rock_pixmap = QPixmap(rock_path)
            if not rock_pixmap.isNull():
                # Store the pixmap directly instead of a brush
                self.textures['rock_pixmap'] = rock_pixmap
                print("Successfully loaded rock texture")
            else:
                print("Error loading rock texture, using fallback")
                self.textures['rock'] = QBrush(QColor(120, 120, 120))  # Gray fallback
        else:
            print(f"Rock texture not found at {rock_path}, using fallback color")
            self.textures['rock'] = QBrush(QColor(120, 120, 120))  # Gray fallback

        print("Successfully loaded textures!")

    def generateMap(self):
        self.grid_size = 60
        self.tile_size = min(self.width(), self.height()) // self.grid_size
        self.grid = [[None for x in range(self.grid_size)] for y in range(self.grid_size)]

        # Track objects for removal
        self.map_objects = {}

        # 1. START WITH ALL WATER
        # Fill the entire map with water first
        for y in range(self.grid_size):
            for x in range(self.grid_size):
                self.grid[y][x] = WaterTile(x, y, self.tile_size, self.textures['water'])
                self.scene.addItem(self.grid[y][x])

        # 2. CREATE MAIN ISLAND (CIRCULAR SHAPE)
        center_x = self.grid_size // 2
        center_y = self.grid_size // 2

        # Island radius (about 40% of map size)
        island_radius = int(self.grid_size * 0.4)

        # Create the main island (with grass)
        for y in range(self.grid_size):
            for x in range(self.grid_size):
                # Calculate distance from center
                distance = math.sqrt((x - center_x) ** 2 + (y - center_y) ** 2)

                # REDUCED NOISE for cleaner coastlines
                edge_noise = random.uniform(-1.5, 1.5)  # Reduced from -3,3 for less jagged edges

                # If within the island radius (with less noise)
                if distance < island_radius + edge_noise:
                    # Remove the water tile
                    self.scene.removeItem(self.grid[y][x])

                    # Replace with grass
                    self.grid[y][x] = GrassTile(x, y, self.tile_size, self.textures['grass'])
                    self.scene.addItem(self.grid[y][x])

        # 3. ADD INLAND LAKES (1-2 larger lakes instead of many small ones)
        num_lakes = random.randint(1, 2)

        for _ in range(num_lakes):
            # Random position inside the island
            angle = random.random() * 2 * math.pi
            distance = random.random() * (island_radius * 0.5)  # Keep lakes in inner 50% of island

            lake_x = int(center_x + distance * math.cos(angle))
            lake_y = int(center_y + distance * math.sin(angle))

            # Larger lake size for more substantial features
            lake_radius = random.randint(3, 6)

            # Create the lake
            for y in range(max(0, lake_y - lake_radius), min(self.grid_size, lake_y + lake_radius + 1)):
                for x in range(max(0, lake_x - lake_radius), min(self.grid_size, lake_x + lake_radius + 1)):
                    # Circular shape for lake
                    dist_from_lake_center = math.sqrt((x - lake_x) ** 2 + (y - lake_y) ** 2)

                    # LESS NOISE for cleaner lake shorelines
                    lake_edge_noise = random.uniform(-0.3, 0.3)  # Very minimal noise

                    if dist_from_lake_center < lake_radius + lake_edge_noise:
                        # Only replace if it's grass (don't create lakes in water)
                        if isinstance(self.grid[y][x], GrassTile):
                            self.scene.removeItem(self.grid[y][x])
                            self.grid[y][x] = WaterTile(x, y, self.tile_size, self.textures['water'])
                            self.scene.addItem(self.grid[y][x])

        # 4. ADD BEACHES WITH COHESIVE SHAPES
        self.add_consistent_beaches()

        # 5. REMOVE ISOLATED TILES (sand "hairs")
        self.remove_isolated_tiles()

        # 6. ADD SOME DESERT AREAS (more cohesive)
        self.add_smooth_desert()

        # 7. ADD TREES AND ROCKS
        self.add_trees_and_rocks()

    def add_consistent_beaches(self):
        """Make all water bordered by sand, with different beach widths for ocean vs lakes"""
        # 1. Identify and tag water tiles as ocean or lake
        ocean_tiles = []
        lake_tiles = []

        # First, tag all edge water as "ocean"
        for y in range(self.grid_size):
            for x in range(self.grid_size):
                if isinstance(self.grid[y][x], WaterTile):
                    # Water at the edges is ocean
                    if x < 5 or y < 5 or x >= self.grid_size - 5 or y >= self.grid_size - 5:
                        ocean_tiles.append((x, y))

        # Flood fill from the ocean edges to identify all ocean water
        visited = set(ocean_tiles)
        queue = list(ocean_tiles)
        while queue:
            x, y = queue.pop(0)

            # Check adjacent water tiles
            for dy in [-1, 0, 1]:
                for dx in [-1, 0, 1]:
                    nx, ny = x + dx, y + dy

                    # Skip diagonals for better flood fill
                    if abs(dx) == 1 and abs(dy) == 1:
                        continue

                    # Check bounds and if it's water not already visited
                    if (0 <= nx < self.grid_size and 0 <= ny < self.grid_size and
                            isinstance(self.grid[ny][nx], WaterTile) and
                            (nx, ny) not in visited):
                        visited.add((nx, ny))
                        queue.append((nx, ny))
                        ocean_tiles.append((nx, ny))

        # All remaining water is lakes
        for y in range(self.grid_size):
            for x in range(self.grid_size):
                if isinstance(self.grid[y][x], WaterTile) and (x, y) not in visited:
                    lake_tiles.append((x, y))

        # 2. Create beaches for oceans (wider beaches)
        ocean_beach_candidates = set()

        for x, y in ocean_tiles:
            # First ring of beach (always present)
            for dy in range(-1, 2):
                for dx in range(-1, 2):
                    nx, ny = x + dx, y + dy

                    # Check bounds
                    if 0 <= nx < self.grid_size and 0 <= ny < self.grid_size:
                        # Only convert grass to sand
                        if isinstance(self.grid[ny][nx], GrassTile):
                            ocean_beach_candidates.add((nx, ny))

        # Apply first ring of ocean beaches
        for x, y in ocean_beach_candidates:
            if isinstance(self.grid[y][x], GrassTile):  # Double-check it's still grass
                self.scene.removeItem(self.grid[y][x])
                self.grid[y][x] = SandTile(x, y, self.tile_size, self.textures['sand'])
                self.scene.addItem(self.grid[y][x])

        # Second ring of beach only for oceans (for wider beaches)
        # But only where it creates natural shapes
        ocean_second_ring = set()

        for x, y in ocean_beach_candidates:
            # Only certain directions for more natural beaches
            for dy, dx in [(0, 1), (1, 0), (0, -1), (-1, 0)]:  # Cardinal directions only
                nx, ny = x + dx, y + dy

                # Check bounds
                if 0 <= nx < self.grid_size and 0 <= ny < self.grid_size:
                    # Only consider grass tiles
                    if isinstance(self.grid[ny][nx], GrassTile):
                        # Count nearby sand tiles to ensure cohesion
                        sand_neighbors = 0
                        for ndy in range(-1, 2):
                            for ndx in range(-1, 2):
                                nnx, nny = nx + ndx, ny + ndy
                                if 0 <= nnx < self.grid_size and 0 <= nny < self.grid_size:
                                    if isinstance(self.grid[nny][nnx], SandTile):
                                        sand_neighbors += 1

                        # Only add to second ring if it would connect to enough sand
                        if sand_neighbors >= 3:  # Need more sand neighbors for cohesion
                            ocean_second_ring.add((nx, ny))

        # Apply second ring for ocean beaches
        for x, y in ocean_second_ring:
            if isinstance(self.grid[y][x], GrassTile):  # Double-check it's still grass
                self.scene.removeItem(self.grid[y][x])
                self.grid[y][x] = SandTile(x, y, self.tile_size, self.textures['sand'])
                self.scene.addItem(self.grid[y][x])

        # 3. Create beaches for lakes (narrower beaches)
        lake_beach_candidates = set()

        for x, y in lake_tiles:
            # Narrower beach for lakes - only direct adjacency
            for dy, dx in [(0, 1), (1, 0), (0, -1), (-1, 0), (1, 1), (-1, -1), (1, -1), (-1, 1)]:
                nx, ny = x + dx, y + dy

                # Check bounds
                if 0 <= nx < self.grid_size and 0 <= ny < self.grid_size:
                    # Only convert grass to sand
                    if isinstance(self.grid[ny][nx], GrassTile):
                        lake_beach_candidates.add((nx, ny))

        # Apply lake beaches
        for x, y in lake_beach_candidates:
            if isinstance(self.grid[y][x], GrassTile):  # Double-check it's still grass
                self.scene.removeItem(self.grid[y][x])
                self.grid[y][x] = SandTile(x, y, self.tile_size, self.textures['sand'])
                self.scene.addItem(self.grid[y][x])

    def remove_isolated_tiles(self):
        """Remove isolated single tiles and weird formations to create cleaner transitions"""
        # Run multiple passes for better smoothing
        for _ in range(3):  # Increased to 3 passes for even more smoothing
            # 1. Remove isolated sand tiles and "hairy" protrusions
            isolated_sand = []

            for y in range(1, self.grid_size - 1):
                for x in range(1, self.grid_size - 1):
                    # Only look at sand tiles
                    if not isinstance(self.grid[y][x], SandTile):
                        continue

                    # Count neighbors by type and their arrangement
                    water_count = 0
                    sand_count = 0
                    grass_count = 0

                    # Track sand in cardinal directions (more important for detecting "hairs")
                    cardinal_sand = 0

                    for dy in range(-1, 2):
                        for dx in range(-1, 2):
                            if dx == 0 and dy == 0:
                                continue  # Skip self

                            nx, ny = x + dx, y + dy
                            if 0 <= nx < self.grid_size and 0 <= ny < self.grid_size:
                                if isinstance(self.grid[ny][nx], WaterTile):
                                    water_count += 1
                                elif isinstance(self.grid[ny][nx], SandTile):
                                    sand_count += 1
                                    # Check if cardinal direction (non-diagonal)
                                    if dx == 0 or dy == 0:
                                        cardinal_sand += 1
                                elif isinstance(self.grid[ny][nx], GrassTile):
                                    grass_count += 1

                    # More aggressive detection of island formations and protrusions
                    should_remove = False

                    # Case 1: Sand with very few sand neighbors, not touching water
                    if sand_count <= 2 and water_count == 0:
                        should_remove = True

                    # Case 2: Sand with only diagonal sand connections (creates zigzags)
                    elif cardinal_sand == 0 and sand_count > 0:
                        should_remove = True

                    # Case 3: Single-tile protrusions (looks like a thin 1-tile "antenna")
                    elif sand_count == 1 and grass_count >= 6:
                        should_remove = True

                    # Keep all sand next to water (important for beaches)
                    if water_count > 0:
                        should_remove = False

                    if should_remove:
                        isolated_sand.append((x, y))

            # Replace isolated sand with grass
            for x, y in isolated_sand:
                self.scene.removeItem(self.grid[y][x])
                self.grid[y][x] = GrassTile(x, y, self.tile_size, self.textures['grass'])
                self.scene.addItem(self.grid[y][x])

            # 2. Fill small "holes" in sand to create more cohesive beaches
            isolated_grass = []

            for y in range(1, self.grid_size - 1):
                for x in range(1, self.grid_size - 1):
                    # Only look at grass tiles
                    if not isinstance(self.grid[y][x], GrassTile):
                        continue

                    # Count sand neighbors and their arrangement
                    sand_count = 0
                    sand_directions = set()  # Track which directions have sand

                    for dy in range(-1, 2):
                        for dx in range(-1, 2):
                            if dx == 0 and dy == 0:
                                continue

                            nx, ny = x + dx, y + dy
                            if 0 <= nx < self.grid_size and 0 <= ny < self.grid_size:
                                if isinstance(self.grid[ny][nx], SandTile):
                                    sand_count += 1
                                    sand_directions.add((dx, dy))

                    # If mostly surrounded by sand, convert to sand
                    # More criteria to fill in gaps that create jagged edges
                    if sand_count >= 5:  # More sand around it than not
                        isolated_grass.append((x, y))
                    # Also fill in "natural" concave beach shapes
                    elif sand_count >= 3:
                        # Look for specific patterns that create unnaturally jagged coastlines
                        # Check if sand forms an L-shape or U-shape around this grass
                        n = (0, -1) in sand_directions
                        s = (0, 1) in sand_directions
                        e = (1, 0) in sand_directions
                        w = (-1, 0) in sand_directions
                        ne = (1, -1) in sand_directions
                        nw = (-1, -1) in sand_directions
                        se = (1, 1) in sand_directions
                        sw = (-1, 1) in sand_directions

                        # L-shapes and U-shapes create unnatural jagged edges
                        if (n and e and (not ne)) or (n and w and (not nw)) or \
                                (s and e and (not se)) or (s and w and (not sw)):
                            isolated_grass.append((x, y))

            # Replace isolated grass within sand areas
            for x, y in isolated_grass:
                self.scene.removeItem(self.grid[y][x])
                self.grid[y][x] = SandTile(x, y, self.tile_size, self.textures['sand'])
                self.scene.addItem(self.grid[y][x])

    def add_smooth_desert(self):
        """Add a cohesive desert area (not random patches)"""
        # Create a single, substantial desert region
        desert_size = random.randint(5, 8)  # Slightly smaller for better control

        # Find a suitable starting point on grass, away from water
        found_start = False
        start_x, start_y = 0, 0
        attempts = 0

        while not found_start and attempts < 50:
            # Try to find a position on the inner part of the island
            angle = random.random() * 2 * math.pi
            distance = random.random() * 0.25 * self.grid_size  # Inner 25% of map

            x = int(self.grid_size // 2 + distance * math.cos(angle))
            y = int(self.grid_size // 2 + distance * math.sin(angle))

            # Ensure in bounds
            if 0 <= x < self.grid_size and 0 <= y < self.grid_size:
                # Check if it's grass and not near water
                if isinstance(self.grid[y][x], GrassTile):
                    # Check an area around the potential desert center
                    has_water_nearby = False
                    for dy in range(-6, 7):
                        for dx in range(-6, 7):
                            nx, ny = x + dx, y + dy
                            if 0 <= nx < self.grid_size and 0 <= ny < self.grid_size:
                                if isinstance(self.grid[ny][nx], WaterTile):
                                    has_water_nearby = True
                                    break
                        if has_water_nearby:
                            break

                    if not has_water_nearby:
                        start_x, start_y = x, y
                        found_start = True

            attempts += 1

        if not found_start:
            return  # Skip desert if no suitable location found

        # Create a more blob-like desert using distance-based approach
        desert_cells = set()

        # Calculate a base shape using an ellipse or blob
        # We'll use random parameters to create an organic desert shape
        a = random.uniform(1.0, 1.5)  # Horizontal stretch
        b = random.uniform(1.0, 1.5)  # Vertical stretch
        rotation = random.uniform(0, math.pi)  # Random rotation

        # Define the maximum radius of the desert
        max_radius = desert_size * 1.5

        # Generate the desert shape
        for y in range(max(0, start_y - int(max_radius)),
                       min(self.grid_size, start_y + int(max_radius) + 1)):
            for x in range(max(0, start_x - int(max_radius)),
                           min(self.grid_size, start_x + int(max_radius) + 1)):

                # Skip if not grass
                if not isinstance(self.grid[y][x], GrassTile):
                    continue

                # Calculate distance to desert center (with transformation for blob shape)
                dx = x - start_x
                dy = y - start_y

                # Apply rotation
                rotated_x = dx * math.cos(rotation) - dy * math.sin(rotation)
                rotated_y = dx * math.sin(rotation) + dy * math.cos(rotation)

                # Apply stretching
                stretched_x = rotated_x / a
                stretched_y = rotated_y / b

                # Calculate distance with the transformation
                distance = math.sqrt(stretched_x ** 2 + stretched_y ** 2)

                # Add noise for natural edges
                edge_noise = random.uniform(-1.0, 1.0)

                # Add to desert if within radius
                if distance < desert_size + edge_noise:
                    desert_cells.add((x, y))

        # Convert all chosen cells to sand
        for x, y in desert_cells:
            self.scene.removeItem(self.grid[y][x])
            self.grid[y][x] = SandTile(x, y, self.tile_size, self.textures['sand'])
            self.scene.addItem(self.grid[y][x])

        # Expand desert to fill small gaps
        extra_cells = set()
        for x, y in desert_cells:
            for dy in [-1, 0, 1]:
                for dx in [-1, 0, 1]:
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < self.grid_size and 0 <= ny < self.grid_size:
                        if isinstance(self.grid[ny][nx], GrassTile):
                            # Count sand neighbors
                            sand_count = 0
                            for ndy in [-1, 0, 1]:
                                for ndx in [-1, 0, 1]:
                                    nnx, nny = nx + ndx, ny + ndy
                                    if 0 <= nnx < self.grid_size and 0 <= nny < self.grid_size:
                                        if (nnx, nny) in desert_cells:
                                            sand_count += 1

                            # If surrounded by mostly sand, add to desert
                            if sand_count >= 5:
                                extra_cells.add((nx, ny))

        # Add the extra cells
        for x, y in extra_cells:
            self.scene.removeItem(self.grid[y][x])
            self.grid[y][x] = SandTile(x, y, self.tile_size, self.textures['sand'])
            self.scene.addItem(self.grid[y][x])

        # Smooth the desert edges
        self.smooth_desert_edges()

    def smooth_desert_edges(self):
        """Make desert edges more natural by removing isolated tiles"""
        # Identify isolated desert patches (sand surrounded mostly by grass)
        isolated_sand = []

        for y in range(1, self.grid_size - 1):
            for x in range(1, self.grid_size - 1):
                # Skip if not sand or next to water
                if not isinstance(self.grid[y][x], SandTile):
                    continue

                # Check if this sand is not beach (not next to water)
                is_beach = False
                for dy in range(-1, 2):
                    for dx in range(-1, 2):
                        nx, ny = x + dx, y + dy
                        if 0 <= nx < self.grid_size and 0 <= ny < self.grid_size:
                            if isinstance(self.grid[ny][nx], WaterTile):
                                is_beach = True
                                break
                    if is_beach:
                        break

                if is_beach:
                    continue  # Don't touch beaches

                # Count sand vs grass neighbors
                sand_count = 0
                for dy in range(-1, 2):
                    for dx in range(-1, 2):
                        if dx == 0 and dy == 0:
                            continue

                        nx, ny = x + dx, y + dy
                        if 0 <= nx < self.grid_size and 0 <= ny < self.grid_size:
                            if isinstance(self.grid[ny][nx], SandTile):
                                sand_count += 1

                # If mostly isolated, convert back to grass
                if sand_count <= 2:  # Handles thin "hairs"
                    isolated_sand.append((x, y))

        # Convert isolated sand back to grass
        for x, y in isolated_sand:
            self.scene.removeItem(self.grid[y][x])
            self.grid[y][x] = GrassTile(x, y, self.tile_size, self.textures['grass'])
            self.scene.addItem(self.grid[y][x])

        # Fill small grass holes in desert
        isolated_grass = []

        for y in range(1, self.grid_size - 1):
            for x in range(1, self.grid_size - 1):
                if not isinstance(self.grid[y][x], GrassTile):
                    continue

                # Count sand neighbors (non-beach sand)
                sand_count = 0
                for dy in range(-1, 2):
                    for dx in range(-1, 2):
                        if dx == 0 and dy == 0:
                            continue

                        nx, ny = x + dx, y + dy
                        if 0 <= nx < self.grid_size and 0 <= ny < self.grid_size:
                            if isinstance(self.grid[ny][nx], SandTile):
                                # Check if this is non-beach sand
                                is_beach_sand = False
                                for ndy in range(-1, 2):
                                    for ndx in range(-1, 2):
                                        nnx, nny = nx + ndx, ny + ndy
                                        if 0 <= nnx < self.grid_size and 0 <= nny < self.grid_size:
                                            if isinstance(self.grid[nny][nnx], WaterTile):
                                                is_beach_sand = True
                                                break
                                    if is_beach_sand:
                                        break

                                if not is_beach_sand:
                                    sand_count += 1

                # If surrounded by desert sand, fill the hole
                if sand_count >= 5:
                    isolated_grass.append((x, y))

        # Convert isolated grass to sand
        for x, y in isolated_grass:
            self.scene.removeItem(self.grid[y][x])
            self.grid[y][x] = SandTile(x, y, self.tile_size, self.textures['sand'])
            self.scene.addItem(self.grid[y][x])

    def add_trees_and_rocks(self):
        """Add trees in dense forests and scattered across the map, with very few rocks"""

        # PART 1: DENSE FORESTS
        # Create forest regions for dense tree clusters
        num_forests = random.randint(3, 5)  # More forests
        forest_centers = []

        # Find good forest centers on grass
        center_x, center_y = self.grid_size // 2, self.grid_size // 2

        for _ in range(num_forests):
            # Choose random angle and distance from center
            angle = random.random() * 2 * math.pi
            distance = random.random() * 0.4 * self.grid_size  # Slightly larger area

            forest_x = int(center_x + distance * math.cos(angle))
            forest_y = int(center_y + distance * math.sin(angle))

            # Make sure it's in bounds and on grass
            if (0 <= forest_x < self.grid_size and
                    0 <= forest_y < self.grid_size and
                    isinstance(self.grid[forest_y][forest_x], GrassTile)):
                forest_radius = random.randint(5, 9)  # Larger forests
                forest_centers.append((forest_x, forest_y, forest_radius))

        # PART 2: PLACE TREES (BOTH IN FORESTS AND SCATTERED)
        for y in range(self.grid_size):
            for x in range(self.grid_size):
                # Skip if not grass or already has an object
                if (not isinstance(self.grid[y][x], GrassTile) or
                        (x, y) in self.map_objects):
                    continue

                # Check if near water (trees don't grow immediately adjacent to water)
                near_water = False
                for dy in range(-1, 2):
                    for dx in range(-1, 2):
                        nx, ny = x + dx, y + dy
                        if 0 <= nx < self.grid_size and 0 <= ny < self.grid_size:
                            if isinstance(self.grid[ny][nx], WaterTile):
                                near_water = True
                                break
                    if near_water:
                        break

                if near_water:
                    continue  # Skip tiles next to water

                # Calculate forest influence for dense forests
                forest_influence = 0
                for fx, fy, radius in forest_centers:
                    distance = math.sqrt((x - fx) ** 2 + (y - fy) ** 2)
                    if distance < radius * 1.5:  # Compact forest
                        # Stronger influence near center
                        influence = max(0, 1.0 - (distance / radius))
                        forest_influence = max(forest_influence, influence)

                # Tree chance combines forest density and background distribution
                # 1. High chance (up to 95%) near forest centers
                # 2. Base chance (15%) everywhere else on grass
                tree_chance = max(forest_influence * 0.95, 0.15)

                if random.random() < tree_chance:
                    # Create tree with tree texture
                    tree = Tree(x, y, self.tile_size, self.textures)
                    self.scene.addItem(tree)
                    self.map_objects[(x, y)] = tree

        # PART 3: PLACE ROCKS (EXACTLY 3 IF POSSIBLE)
        # Place exactly 3 rocks in distinct locations
        num_rocks = 3  # Fixed number of rocks

        # Find all valid spots for rocks (grass or sand, not already occupied)
        available_spots = []

        for y in range(5, self.grid_size - 5):
            for x in range(5, self.grid_size - 5):
                # Skip if water or already has object
                if (isinstance(self.grid[y][x], WaterTile) or (x, y) in self.map_objects):
                    continue

                # Add grass and sand locations
                if isinstance(self.grid[y][x], GrassTile) or isinstance(self.grid[y][x], SandTile):
                    available_spots.append((x, y))

        # If we have enough spots, place exactly 3 rocks
        if available_spots:
            # Divide the map into rough quadrants to spread out the rocks
            # This helps ensure the rocks aren't all clustered together
            quadrants = [[] for _ in range(4)]

            mid_x = self.grid_size // 2
            mid_y = self.grid_size // 2

            # Assign spots to quadrants
            for x, y in available_spots:
                if x < mid_x and y < mid_y:
                    quadrants[0].append((x, y))  # Top-left
                elif x >= mid_x and y < mid_y:
                    quadrants[1].append((x, y))  # Top-right
                elif x < mid_x and y >= mid_y:
                    quadrants[2].append((x, y))  # Bottom-left
                else:
                    quadrants[3].append((x, y))  # Bottom-right

            # Select up to 3 rocks, trying to get one from each non-empty quadrant first
            rock_positions = []

            # First, get one rock from each quadrant if possible
            non_empty_quadrants = [q for q in quadrants if q]
            for quadrant in non_empty_quadrants[:num_rocks]:
                if quadrant:
                    pos = random.choice(quadrant)
                    rock_positions.append(pos)

            # If we still need more rocks, choose from all remaining spots
            remaining_spots = [spot for spot in available_spots if spot not in rock_positions]
            additional_needed = num_rocks - len(rock_positions)

            if additional_needed > 0 and remaining_spots:
                random.shuffle(remaining_spots)
                rock_positions.extend(remaining_spots[:additional_needed])

            # Place the rocks
            for x, y in rock_positions:
                rock = Rock(x, y, self.tile_size, self.textures)
                self.scene.addItem(rock)
                self.map_objects[(x, y)] = rock

    def eventFilter(self, source, event):
        if source is self.view.viewport():
            # Handle mouse wheel events for zooming
            if event.type() == QEvent.Type.Wheel:
                # Get the mouse position
                mouse_pos = self.view.mapToScene(event.position().toPoint())

                # Only handle zoom in (positive scroll)
                if event.angleDelta().y() > 0:
                    # Zoom in
                    scale_factor = 1.15  # 15% scale per scroll step
                    self.view.scale(scale_factor, scale_factor)

                    # Center view on mouse position
                    self.view.centerOn(mouse_pos)
                else:
                    # For zoom out, check if we're at or below initial scale
                    current_scale = self.view.transform().m11()  # Get current horizontal scale
                    initial_scale = self.initial_transform.m11()  # Get initial horizontal scale

                    if current_scale > initial_scale:
                        # Only zoom out if we're still more zoomed in than the start
                        scale_factor = 1.15
                        self.view.scale(1 / scale_factor, 1 / scale_factor)
                        self.view.centerOn(mouse_pos)
                    else:
                        # Reset to initial transform (showing full map)
                        self.view.setTransform(self.initial_transform)

                # Set the scroll limits after zooming
                self.limitScroll()
                return True  # Event handled

            # Handle middle mouse button press
            elif event.type() == QEvent.Type.MouseButtonPress and event.button() == Qt.MouseButton.MiddleButton:
                self.is_middle_pressed = True
                self.last_pos = event.position().toPoint()
                return True

            # Handle middle mouse button release
            elif event.type() == QEvent.Type.MouseButtonRelease and event.button() == Qt.MouseButton.MiddleButton:
                self.is_middle_pressed = False
                self.last_pos = None
                return True

            # Handle mouse movement for dragging
            elif event.type() == QEvent.Type.MouseMove and self.is_middle_pressed and self.last_pos is not None:
                # Get current position
                current_pos = event.position().toPoint()

                # Calculate difference
                dx = current_pos.x() - self.last_pos.x()
                dy = current_pos.y() - self.last_pos.y()

                # Store new position
                self.last_pos = current_pos

                # Move the view using scrollbars (the most reliable way)
                self.view.horizontalScrollBar().setValue(
                    self.view.horizontalScrollBar().value() - dx)
                self.view.verticalScrollBar().setValue(
                    self.view.verticalScrollBar().value() - dy)

                return True

        return super(MyWindow, self).eventFilter(source, event)

    def limitScroll(self):
        # Calculate the visible scene rect
        visible_rect = self.view.mapToScene(self.view.viewport().rect()).boundingRect()
        scene_rect = self.scene.sceneRect()

        # If visible rect is larger than scene, center the view
        if visible_rect.width() <= scene_rect.width() and visible_rect.height() <= scene_rect.height():
            # Calculate the bounds to keep the view within the scene
            x = max(0, min(visible_rect.left(), scene_rect.right() - visible_rect.width()))
            y = max(0, min(visible_rect.top(), scene_rect.bottom() - visible_rect.height()))

            # Update the view position if needed
            if x != visible_rect.left() or y != visible_rect.top():
                self.view.centerOn(x + visible_rect.width() / 2, y + visible_rect.height() / 2)


class InteractionItem(QGraphicsItem):
    def __init__(self, x, y, size, texture, parent=None):
        super(InteractionItem, self).__init__(parent)

        self.x = x
        self.y = y
        self.size = size
        self.texture = texture
        self.is_pixmap = isinstance(texture, QPixmap)
        self.setPos(x * size, y * size)

        # Enable selection for interaction
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, True)

    def boundingRect(self):
        return QRectF(0, 0, self.size, self.size)

    def paint(self, painter, option, widget):
        # Different drawing method based on texture type
        if self.is_pixmap:
            # Calculate the scaled size to fit within the tile
            # Leave small margin around the edges (10%)
            margin = self.size * 0.1
            draw_size = self.size - 2 * margin

            # Draw the pixmap scaled to fit within the tile
            painter.drawPixmap(
                QRect(int(margin), int(margin), int(draw_size), int(draw_size)),
                self.texture
            )

            # Highlight selection if needed
            if self.isSelected():
                painter.setPen(Qt.PenStyle.DashLine)
                painter.setBrush(QBrush())  # No fill
                painter.drawRect(margin, margin, draw_size, draw_size)
        else:
            # For brush textures (fallback)
            painter.setBrush(self.texture)
            painter.setPen(Qt.PenStyle.NoPen)

            # Draw with margin for better visibility
            margin = self.size * 0.15
            painter.drawRect(margin, margin, self.size - 2 * margin, self.size - 2 * margin)

            # Highlight if selected
            if self.isSelected():
                painter.setPen(Qt.PenStyle.DashLine)
                painter.drawRect(margin, margin, self.size - 2 * margin, self.size - 2 * margin)

    def remove(self):
        """Remove this item from the scene"""
        if self.scene():
            # Get the grid position before removal
            grid_x = int(self.x)
            grid_y = int(self.y)

            # Remove from scene
            self.scene().removeItem(self)

            # Try to notify the main window about the removal
            main_window = None

            # Look for the main window through scene views
            if self.scene() and self.scene().views():
                view = self.scene().views()[0]
                main_window = view.window()

            # If we found the main window and it has a map_objects dictionary
            if main_window and hasattr(main_window, 'map_objects'):
                # Remove from the tracking dictionary if it exists
                if (grid_x, grid_y) in main_window.map_objects:
                    del main_window.map_objects[(grid_x, grid_y)]
                    print(f"Removed object at ({grid_x}, {grid_y})")

            return True

        return False

    def mousePressEvent(self, event):
        """Handle mouse press events on this item"""
        super().mousePressEvent(event)

        # Select this item when clicked
        self.setSelected(True)

        # If it's a left click, handle it specially (e.g., for removal)
        if event.button() == Qt.MouseButton.LeftButton:
            self.remove()


class Tree(InteractionItem):
    def __init__(self, x, y, size, texture_manager):
        # Use tree pixmap if available, otherwise fallback to brush
        texture = texture_manager.get('tree_pixmap', texture_manager.get('tree'))
        super().__init__(x, y, size, texture)

        # Set Z value to ensure trees appear above terrain
        self.setZValue(1)

    def get_stats(self):
        return {
            "movement_cost": 999,  # Impassable
            "defense_bonus": 2,
            "attack_penalty": 0
        }


class Rock(InteractionItem):
    def __init__(self, x, y, size, texture_manager):
        # Use rock pixmap if available, otherwise fallback to brush
        texture = texture_manager.get('rock_pixmap', texture_manager.get('rock'))
        super().__init__(x, y, size, texture)

        # Set Z value to ensure rocks appear above terrain
        self.setZValue(1)

    def get_stats(self):
        return {
            "movement_cost": 2,
            "defense_bonus": 3,
            "attack_penalty": 1
        }

class TerrainTile(QGraphicsItem):
    def __init__(self, x, y, size, texture, parent=None):
        super(TerrainTile, self).__init__(parent)

        self.x = x
        self.y = y
        self.size = size
        self.texture = texture
        self.setPos(x * size, y * size)

    def boundingRect(self):
        return QRectF(0, 0, self.size, self.size)

    def paint(self, painter, option, widget):
        # Draw the terrain with the texture
        painter.setBrush(self.texture)
        painter.setPen(Qt.PenStyle.NoPen)  # No outline
        painter.drawRect(0, 0, self.size, self.size)

    def get_stats(self):
        return {}


class WaterTile(TerrainTile):
    def get_stats(self):
        return {
            "movement_cost": 999,  # Impassable
            "defense_bonus": 0,
            "attack_penalty": 0
        }
class GrassTile(TerrainTile):
    def get_stats(self):
        return {
            "movement_cost": 1,
            "defense_bonus": 0,
            "attack_penalty": 0
        }


class SandTile(TerrainTile):
    def get_stats(self):
        return {
            "movement_cost": 2,
            "defense_bonus": 0,
            "attack_penalty": 1
        }


def window():
    app = QApplication(sys.argv)
    win = MyWindow()
    win.show()
    sys.exit(app.exec())


window()