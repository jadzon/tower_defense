"""
Game configuration and constants
"""

# Paths
TILESET_PATH = "./assets/textures/tiles.png"
WATER_TILE_PATH = "./assets/textures/water_tile.png"
TREE_PATH = "./assets/textures/forest/Trees/Tree-2/Tree-2-4.png"
ROCK_PATH = "./assets/textures/forest/Stones/Stone-1.png"
AVATAR_PATH = "./assets/textures/avatar.png"

# Map generation settings
DEFAULT_GRID_SIZE = 60
ISLAND_RADIUS_FACTOR = 0.4  # Percentage of grid size
LAKE_COUNT_RANGE = (1, 2)
FOREST_COUNT_RANGE = (3, 5)
ROCK_COUNT = 3

# Terrain attributes
TERRAIN_STATS = {
    "water": {
        "movement_cost": 999,  # Impassable
        "defense_bonus": 0,
        "attack_penalty": 0
    },
    "grass": {
        "movement_cost": 1,
        "defense_bonus": 0,
        "attack_penalty": 0
    },
    "sand": {
        "movement_cost": 2,
        "defense_bonus": 0,
        "attack_penalty": 1
    }
}

# Object attributes
OBJECT_STATS = {
    "tree": {
        "movement_cost": 4,
        "defense_bonus": 2,
        "attack_penalty": 0
    },
    "rock": {
        "movement_cost": 2,
        "defense_bonus": 3,
        "attack_penalty": 1
    }
}