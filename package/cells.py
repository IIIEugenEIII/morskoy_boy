from enum import Enum

class CellType(Enum):
    """Типы клеток на поле"""
    EMPTY = "~"
    SHIP = "■"
    HIT = "X"
    MISS = "○"
    MINE = "●"
    TRACER = "T"
    SUBMARINE = ("▲")

class ShipType(Enum):
    """Типы кораблей"""
    BATTLESHIP = "Линкор"
    CRUISER = "Крейсер"
    DESTROYER = "Эсминец"
    SUBMARINE = "Подводная лодка"
    MINESWEEPER = "Минный тральщик"