"""
Terrain tile classes for the game map
"""
from PyQt6.QtWidgets import QGraphicsItem
from PyQt6.QtCore import QRectF, Qt
from src.config import TERRAIN_STATS

class TerrainTile(QGraphicsItem):
    """Base class for all terrain tiles"""
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
    """Water terrain - impassable"""
    def get_stats(self):
        return TERRAIN_STATS["water"]


class GrassTile(TerrainTile):
    """Grass terrain - normal movement"""
    def get_stats(self):
        return TERRAIN_STATS["grass"]


class SandTile(TerrainTile):
    """Sand terrain - slow movement"""
    def get_stats(self):
        return TERRAIN_STATS["sand"]