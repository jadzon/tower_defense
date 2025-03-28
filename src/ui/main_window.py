"""
Main window for the Army Defense game
"""
import os
import math

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QGraphicsScene, QGraphicsView,
    QFrame, QVBoxLayout, QWidget, QMessageBox
)
from PyQt6.QtGui import QBrush, QColor, QPixmap
from PyQt6.QtCore import Qt, QEvent, QPoint, QRect

from src.map.map_generator import MapGenerator
from src.config import TILESET_PATH, WATER_TILE_PATH, TREE_PATH, ROCK_PATH, AVATAR_PATH
from src.ui.bottom_panel import BottomPanel
from src.player import Player


class MyWindow(QMainWindow):
    """Main game window"""

    def __init__(self):
        super(MyWindow, self).__init__()
        self.setWindowTitle("Army Defense")
        self.initScreen()
        self.initGameBoard()
        self.connectUIEvents()

    def connectUIEvents(self):
        """Connect UI events to handler methods"""
        self.bottom_panel.build_clicked.connect(self.onBuildClicked)

    def onBuildClicked(self):
        """Handle build button click"""
        QMessageBox.information(self, "Build Mode", "Build mode activated!\nSelect a location on the map to build.")
        # Here you would enable build mode and wait for map clicks

    def initScreen(self):
        """Initialize window size and position"""
        screen = QApplication.primaryScreen()
        available_geometry = screen.availableGeometry()

        width = int(available_geometry.width() * 0.8)
        height = int(available_geometry.height() * 0.8)
        x = int(width * 0.1)
        y = int(height * 0.1)

        self.setGeometry(x, y, width, height)
        print(f"Setting window at: {x},{y} with size {width}x{height}")

        # Create a central widget and layout for organization
        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        self.setStyleSheet("background-color: black;")

    def add_player(self):
        """Add the player character to the scene"""
        # Path to your sprite sheet - update this to your actual path
        sprite_sheet_path = "./assets/player_sprites.png"  # Adjust to your sprite location

        # Create player
        self.player = Player(sprite_sheet_path, self.tile_size)

        # Find a suitable starting position (grass tile)
        start_x, start_y = None, None

        # Try to find a grass tile near the center
        center_x, center_y = self.grid_size // 2, self.grid_size // 2
        search_radius = 5

        for y in range(center_y - search_radius, center_y + search_radius):
            for x in range(center_x - search_radius, center_x + search_radius):
                if 0 <= x < self.grid_size and 0 <= y < self.grid_size:
                    from src.map.terrain import GrassTile
                    if isinstance(self.grid[y][x], GrassTile):
                        start_x, start_y = x, y
                        break
            if start_x is not None:
                break

        # If no grass tile found, use center
        if start_x is None:
            start_x, start_y = center_x, center_y

        # Position player at the found tile
        self.player.setPos(start_x * self.tile_size, start_y * self.tile_size)

        # Add player to scene
        self.scene.addItem(self.player)

        # Focus the player to receive keyboard events
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setFocus()

        print(f"Player added at position ({start_x}, {start_y})")

    def initGameBoard(self):
        """Initialize the game board with scene, view, and map"""
        # Setup scene and view
        self.scene = QGraphicsScene(self)
        self.view = QGraphicsView(self.scene, self)
        self.view.setFrameShape(QFrame.Shape.NoFrame)

        # Add view to layout
        self.main_layout.addWidget(self.view, 1)

        # Enable mouse tracking for interactions
        self.view.setMouseTracking(True)
        self.view.setDragMode(QGraphicsView.DragMode.NoDrag)

        # Mouse tracking variables
        self.is_middle_pressed = False
        self.last_pos = None

        # Load textures and generate map
        self.loadTilesetTextures()

        self.grid_size = 60
        self.tile_size = min(self.width(), self.height()) // self.grid_size

        # Create map generator
        self.map_generator = MapGenerator(self.scene, self.textures, self.grid_size)

        # Generate the map
        map_width, map_height = self.map_generator.generate_map(self.tile_size)

        # Get references to the grid and map objects
        self.grid = self.map_generator.get_grid()
        self.map_objects = self.map_generator.get_map_objects()

        # Add player to the scene
        self.add_player()

        # Set scene boundaries
        self.scene.setSceneRect(0, 0, map_width, map_height)

        # Set initial view
        self.view.fitInView(self.scene.sceneRect(), Qt.AspectRatioMode.KeepAspectRatio)
        self.initial_transform = self.view.transform()

        # Hide scrollbars
        self.view.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.view.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        # Create simple bottom panel
        self.bottom_panel = BottomPanel(self)

        # Set avatar from tree texture (as a placeholder example)
        if 'avatar_pixmap' in self.textures:
            self.bottom_panel.set_avatar(self.textures['avatar_pixmap'])

        # Add bottom panel to the main layout
        self.main_layout.addWidget(self.bottom_panel, 0)

        # Install event filter for handling mouse events
        self.view.viewport().installEventFilter(self)

    def loadTilesetTextures(self):
        """Load textures for terrain and objects"""
        self.textures = {}

        # Update paths to the new asset structure
        tileset_path = TILESET_PATH
        water_tile_path = WATER_TILE_PATH
        tree_path = TREE_PATH
        rock_path = ROCK_PATH
        avatar_path = AVATAR_PATH

        # Fallback colors if textures not found
        if not os.path.exists(tileset_path):
            print(f"Tileset not found at {tileset_path}, ERROR BIG L")

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
                self.textures['tree_pixmap'] = tree_pixmap
                print("Successfully loaded tree texture")
            else:
                print("Error loading tree texture, using fallback")
                self.textures['tree'] = QBrush(QColor(0, 100, 0))
        else:
            print(f"Tree texture not found at {tree_path}, using fallback color")
            self.textures['tree'] = QBrush(QColor(0, 100, 0))

        if os.path.exists(rock_path):
            rock_pixmap = QPixmap(rock_path)
            if not rock_pixmap.isNull():
                self.textures['rock_pixmap'] = rock_pixmap
                print("Successfully loaded rock texture")
            else:
                print("Error loading rock texture, using fallback")
                self.textures['rock'] = QBrush(QColor(120, 120, 120))
        else:
            print(f"Rock texture not found at {rock_path}, using fallback color")
            self.textures['rock'] = QBrush(QColor(120, 120, 120))

        if os.path.exists(avatar_path):
            avatar_pixmap = QPixmap(avatar_path)
            if not avatar_pixmap.isNull():
                self.textures['avatar_pixmap'] = avatar_pixmap
                print("Successfully loaded avatar texture")
            else:
                print("Error loading avatar texture")

        print("Successfully loaded textures!")

    def eventFilter(self, source, event):
        """Handle mouse events for map interaction"""
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
        """Limit scrolling to keep the view within the scene boundaries"""
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

    def resizeEvent(self, event):
        """Handle window resize events"""
        super().resizeEvent(event)
        # Adjust the view to fit the scene when resized
        self.view.fitInView(self.scene.sceneRect(), Qt.AspectRatioMode.KeepAspectRatio)

    def keyPressEvent(self, event):
        """Handle keyboard input for player movement"""
        if not hasattr(self, 'player'):
            return

        if event.key() == Qt.Key.Key_W:
            self.player.move("up")
        elif event.key() == Qt.Key.Key_S:
            self.player.move("down")
        elif event.key() == Qt.Key.Key_A:
            self.player.move("left")
        elif event.key() == Qt.Key.Key_D:
            self.player.move("right")

        # Make sure player stays visible in view
        self.view.ensureVisible(self.player)

        # Make sure we call the parent class implementation
        super().keyPressEvent(event)