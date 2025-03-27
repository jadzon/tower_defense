from PyQt6 import QtWidgets
from PyQt6.QtGui import QBrush, QColor, QPixmap
from PyQt6.QtWidgets import QApplication, QMainWindow, QGraphicsScene, QGraphicsView, QGraphicsItem
from PyQt6.QtCore import QRectF, Qt, QEvent, QPoint, QRect
import random
import sys
import os


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

        tileset_path = "./textures/tiles.png"
        water_tile_path = "./textures/water_tile.png"

        if not os.path.exists(tileset_path):
            print(f"Tileset not found at {tileset_path}, using fallback colors")

            self.textures['meadow'] = QBrush(QColor(50, 180, 50))
            self.textures['ocean'] = QBrush(QColor(0, 0, 150))
            self.textures['sand'] = QBrush(QColor(240, 220, 130))
            self.textures['lake'] = QBrush(QColor(0, 100, 255))
            return

        # Load the tileset
        tileset = QPixmap(tileset_path)
        if tileset.isNull():
            print("error while loading tileset")
        water_tile = QPixmap(water_tile_path)
        if tileset.isNull():
            print("error while loading tileset")

        meadow_tile = tileset.copy(QRect(0, 0, 16, 16))
        self.textures['meadow'] = QBrush(meadow_tile)

        ocean_tile = water_tile.copy(QRect(0, 0, 16, 16))
        self.textures['ocean'] = QBrush(ocean_tile)

        sand_tile = tileset.copy(QRect(144, 32, 16, 16))
        self.textures['sand'] = QBrush(sand_tile)

        lake_tile = tileset.copy(QRect(384, 32, 32, 32))
        self.textures['lake'] = QBrush(lake_tile)

        print("Successfully loaded textures from tileset!")

    def generateMap(self):
        self.grid_size = 20
        self.tile_size = min(self.width(), self.height()) // self.grid_size
        self.grid = [[None for x in range(self.grid_size)] for y in range(self.grid_size)]

        # Add some variety to the map
        for y in range(self.grid_size):
            for x in range(self.grid_size):
                # Outer edge is ocean
                if x < 2 or y < 2 or x >= self.grid_size - 2 or y >= self.grid_size - 2:
                    tile = OceanTile(x, y, self.tile_size, self.textures['ocean'])

                # Add some random sand patches
                elif random.random() < 0.1:  # 10% chance for sand
                    tile = SandTile(x, y, self.tile_size, self.textures['sand'])

                else:
                    tile = MeadowTile(x, y, self.tile_size, self.textures['meadow'])

                self.grid[y][x] = tile
                self.scene.addItem(tile)

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


class OceanTile(TerrainTile):
    def get_stats(self):
        return {
            "movement_cost": 999,  # Impassable
            "defense_bonus": 0,
            "attack_penalty": 0
        }


class LakeTile(TerrainTile):
    def get_stats(self):
        return {
            "movement_cost": 4,
            "defense_bonus": 1,
            "attack_penalty": 2
        }


class MeadowTile(TerrainTile):
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