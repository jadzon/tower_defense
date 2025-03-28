"""
Player character for the Army Defense game
"""
from PyQt6.QtWidgets import QGraphicsItem
from PyQt6.QtGui import QPixmap, QPainter
from PyQt6.QtCore import Qt, QRectF, QTimer


class Player(QGraphicsItem):
    """Player character that can move around the map"""

    def __init__(self, sprite_sheet_path, tile_size):
        super().__init__()

        # Player properties
        self.tile_size = tile_size
        self.speed = 5  # pixels per movement
        self.direction = "down"  # Default direction

        # Animation properties
        self.frame_index = 0
        self.frames = {}
        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self.update_animation)
        self.animation_timer.start(150)  # Update frame every 150ms

        # Load sprite sheet
        self.load_sprite_sheet(sprite_sheet_path)

        # Set initial position
        self.setZValue(10)  # Make sure player is above terrain

    def load_sprite_sheet(self, path):
        """Load and split sprite sheet into individual frames"""
        try:
            # Load the sprite sheet
            sprite_sheet = QPixmap(path)
            if sprite_sheet.isNull():
                print(f"Failed to load sprite sheet from {path}")
                self.create_fallback_sprite()
                return

            # Define frame dimensions (adjust based on your sprite sheet)
            frame_width = 32  # Example - adjust to your sprite sheet
            frame_height = 32  # Example - adjust to your sprite sheet

            # Set directions and frames
            directions = ["down", "left", "right", "up"]
            frames_per_direction = 4

            # Extract frames for each direction
            for i, direction in enumerate(directions):
                self.frames[direction] = []
                row = i

                for col in range(frames_per_direction):
                    x = col * frame_width
                    y = row * frame_height
                    frame = sprite_sheet.copy(x, y, frame_width, frame_height)
                    self.frames[direction].append(frame)

            print(f"Successfully loaded player sprite sheet with {len(directions)} directions")

        except Exception as e:
            print(f"Error loading sprite sheet: {e}")
            self.create_fallback_sprite()

    def create_fallback_sprite(self):
        """Create a simple fallback sprite if loading fails"""
        # Create simple colored squares for each direction
        self.frames = {
            "down": [self._create_colored_sprite(Qt.GlobalColor.blue)],
            "left": [self._create_colored_sprite(Qt.GlobalColor.green)],
            "right": [self._create_colored_sprite(Qt.GlobalColor.yellow)],
            "up": [self._create_colored_sprite(Qt.GlobalColor.red)]
        }
        print("Created fallback sprites")

    def _create_colored_sprite(self, color):
        """Create a simple colored square as fallback"""
        pixmap = QPixmap(32, 32)
        pixmap.fill(Qt.GlobalColor.transparent)
        painter = QPainter(pixmap)
        painter.setBrush(color)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRect(2, 2, 28, 28)  # Smaller than full size to see the edges
        painter.end()
        return pixmap

    def update_animation(self):
        """Update the current animation frame"""
        if self.direction in self.frames:
            frames_count = len(self.frames[self.direction])
            if frames_count > 0:
                self.frame_index = (self.frame_index + 1) % frames_count
                self.update()  # Trigger redraw

    def boundingRect(self):
        """Return the bounding rectangle of the player"""
        return QRectF(0, 0, self.tile_size, self.tile_size)

    def paint(self, painter, option, widget):
        """Paint the current frame of the player"""
        if self.direction in self.frames and len(self.frames[self.direction]) > 0:
            # Get current frame
            current_frame = self.frames[self.direction][self.frame_index]

            # Draw the frame scaled to tile size
            painter.drawPixmap(
                0, 0, self.tile_size, self.tile_size,
                current_frame
            )

    def move(self, direction):
        """Move the player in the specified direction"""
        self.direction = direction

        # Calculate new position based on direction
        if direction == "up":
            self.setY(max(0, self.y() - self.speed))
        elif direction == "down":
            self.setY(self.y() + self.speed)
        elif direction == "left":
            self.setX(max(0, self.x() - self.speed))
        elif direction == "right":
            self.setX(self.x() + self.speed)

        # Start animation if it's not already running
        if not self.animation_timer.isActive():
            self.animation_timer.start(150)