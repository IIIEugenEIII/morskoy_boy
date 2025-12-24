import random
from package.board import Board
from .ships import Ship
from package.cells import ShipType, CellType


class Player:
    """Класс игрока"""

    def __init__(self, name, board_size=10):
        self.name = name
        self.board = Board(board_size)
        self.enemy_board = Board(board_size)
        self.ships = []
        self.mines_count = 5
        self.initialize_ships()

    def initialize_ships(self):
        """Инициализация флота"""
        ship_configs = [
            (ShipType.BATTLESHIP, 4, None),
            (ShipType.CRUISER, 3, None),
            (ShipType.CRUISER, 3, None),
            (ShipType.DESTROYER, 2, None),
            (ShipType.DESTROYER, 2, None),
            (ShipType.DESTROYER, 2, None),
            (ShipType.SUBMARINE, 1, "Невидим для обычных выстрелов, виден только тральщику"),
            (ShipType.SUBMARINE, 1, "Невидим для обычных выстрелов, виден только тральщику"),
        ]

        for i, (ship_type, size, ability) in enumerate(ship_configs):
            ship_name = f"{ship_type.value} {i + 1}"
            self.ships.append(Ship(ship_name, size, ship_type, ability))

    def place_ships_randomly(self):
        """Случайная расстановка кораблей"""
        for ship in self.ships:
            placed = False
            attempts = 0

            while not placed and attempts < 100:
                x = random.randint(0, self.board.size - 1)
                y = random.randint(0, self.board.size - 1)
                horizontal = random.choice([True, False])
                placed = self.board.place_ship(ship, x, y, horizontal)
                attempts += 1

            if not placed:
                print(f"Не удалось разместить {ship.name}")

    def place_mines_randomly(self):
        """Случайная расстановка мин"""
        mines_placed = 0
        while mines_placed < self.mines_count:
            x = random.randint(0, self.board.size - 1)
            y = random.randint(0, self.board.size - 1)
            if self.board.place_mine(x, y):
                mines_placed += 1

    def all_ships_sunk(self):
        """Проверка, потоплены ли все корабли"""
        for ship in self.ships:
            print(f"Корабль {ship.name} потоплен: {ship.is_sunk()}")
        return all(ship.is_sunk() for ship in self.ships)

    def use_tracer(self, x, y, enemy):
        """Использование минного тральщика"""
        if not (0 <= x < self.board.size and 0 <= y < self.board.size):
            return False, "Неверные координаты!"

        # Проверяем, не использовали ли уже тральщик здесь
        cell = self.enemy_board.get_cell(x, y)
        if cell and cell.cell_type == CellType.TRACER:
            return False, "Здесь уже использован тральщик!"

        detected = []
        neutralized = []

        # Помечаем клетку как использованный тральщик
        self.enemy_board.get_cell(x, y).set_type(CellType.TRACER)

        # Проверяем радиус 3x3
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                nx, ny = x + dx, y + dy
                if 0 <= nx < enemy.board.size and 0 <= ny < enemy.board.size:
                    enemy_cell = enemy.board.get_cell(nx, ny)
                    player_cell = self.enemy_board.get_cell(nx, ny)

                    if enemy_cell:
                        # Обнаружение и обезвреживание мин
                        if enemy_cell.has_mine and enemy_cell.mine and not enemy_cell.mine.triggered:
                            detected.append(("Мина", nx, ny))
                            # Обезвреживаем мину
                            enemy_cell.mine.triggered = True
                            enemy_cell.has_mine = False
                            enemy_cell.mine = None
                            neutralized.append(("Мина", nx, ny))

                            # Обновляем отображение у обоих игроков
                            if enemy_cell.revealed:
                                enemy_cell.cell_type = CellType.EMPTY
                            else:
                                enemy_cell.cell_type = CellType.EMPTY

                            if player_cell:
                                player_cell.revealed = True
                                player_cell.cell_type = CellType.EMPTY
                                player_cell.has_mine = False
                                player_cell.mine = None

                        # Обнаружение и обезвреживание подлодок
                        elif enemy_cell.cell_type == CellType.SUBMARINE and not enemy_cell.revealed:
                            detected.append(("Подлодка", nx, ny))
                            # Находим и "топим" подлодку
                            for ship in enemy.ships:
                                if ship.ship_type == ShipType.SUBMARINE and (nx, ny) in ship.coordinates:
                                    ship.hit()
                                    neutralized.append(("Подлодка", nx, ny))
                                    break

                            # Обновляем клетку
                            enemy_cell.set_type(CellType.HIT)
                            enemy_cell.revealed = True

                            if player_cell:
                                player_cell.set_type(CellType.HIT)
                                player_cell.revealed = True

        # Формируем сообщение
        if detected:
            message_parts = []
            if neutralized:
                message_parts.append(
                    "Обезврежено: " + ", ".join([f"{item[0]} на ({item[1]},{item[2]})" for item in neutralized]))
            if detected != neutralized:
                message_parts.append("Обнаружено: " + ", ".join(
                    [f"{item[0]} на ({item[1]},{item[2]})" for item in detected if item not in neutralized]))
            message = "\n".join(message_parts)
        else:
            message = "Ничего не обнаружено"

        return True, message

    def display_status(self):
        """Отображение статуса игрока"""
        print(f"\n{self.name}:")
        print(f"  Корабли:")
        for ship in self.ships:
            print(f"    - {ship}")