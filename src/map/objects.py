"""
Interactive map objects like trees and rocks
"""
from PyQt6.QtWidgets import QGraphicsItem
from PyQt6.QtCore import QRectF, Qt, QRect
from PyQt6.QtGui import QPixmap, QBrush
from src.config import OBJECT_STATS

class InteractionItem(QGraphicsItem):
    """Base class for interactive map objects"""
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
    """Tree object - blocks movement, provides defense"""
    def __init__(self, x, y, size, texture_manager):
        # Use tree pixmap if available, otherwise fallback to brush
        texture = texture_manager.get('tree_pixmap', texture_manager.get('tree'))
        super().__init__(x, y, size, texture)

        # Set Z value to ensure trees appear above terrain
        self.setZValue(1)

    def get_stats(self):
        return OBJECT_STATS["tree"]


class Rock(InteractionItem):
    """Rock object - slows movement, provides defense"""
    def __init__(self, x, y, size, texture_manager):
        # Use rock pixmap if available, otherwise fallback to brush
        texture = texture_manager.get('rock_pixmap', texture_manager.get('rock'))
        super().__init__(x, y, size, texture)

        # Set Z value to ensure rocks appear above terrain
        self.setZValue(1)

    def get_stats(self):
        return OBJECT_STATS["rock"]