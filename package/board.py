from .cells import CellType, ShipType
from .ships import Mine

class Cell:
    """Класс клетки поля"""

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.cell_type = CellType.EMPTY
        self.revealed = False
        self.has_mine = False
        self.mine = None

    def set_mine(self, mine):
        """Установить мину в клетку"""
        self.has_mine = True
        self.mine = mine
        self.cell_type = CellType.MINE

    def set_type(self, cell_type):
        self.cell_type = cell_type
        if cell_type in [CellType.HIT, CellType.MISS, CellType.TRACER]:
            self.revealed = True

    def __str__(self):
        return self.cell_type.value

    def display(self, show_ships=False, show_mines=False):
        """Отображение клетки с учетом настроек видимости"""
        # Если клетка раскрыта (в нее стреляли)
        if self.revealed:
            return self.cell_type.value

        # Если не раскрыта, но нужно показать корабли
        if self.cell_type == CellType.SHIP and show_ships:
            return self.cell_type.value

        # Если не раскрыта, но нужно показать мины
        if self.has_mine and show_mines:
            return CellType.MINE.value

        # Если это подлодка и показываем корабли
        if self.cell_type == CellType.SUBMARINE and show_ships:
            return CellType.SUBMARINE.value

        # Во всех остальных случаях показываем как пустую
        return CellType.EMPTY.value


class Board:
    """Игровое поле"""

    def __init__(self, size=10):
        self.size = size
        self.grid = [[Cell(x, y) for x in range(size)] for y in range(size)]
        self.mines = []
        self.ships = []

    def display(self, show_ships=False, show_mines=False):
        """Отображение поля"""
        print("  " + " ".join(str(i) for i in range(self.size)))
        for y in range(self.size):
            row = f"{y}|"
            for x in range(self.size):
                row += self.grid[y][x].display(show_ships, show_mines) + " "
            print(row)

    def get_cell(self, x, y):
        """Получение клетки по координатам"""
        if 0 <= x < self.size and 0 <= y < self.size:
            return self.grid[y][x]
        return None

    def place_ship(self, ship, x, y, horizontal):
        """Размещение корабля на поле"""
        coordinates = []

        for i in range(ship.size):
            nx = x + (i if horizontal else 0)
            ny = y + (0 if horizontal else i)

            if nx >= self.size or ny >= self.size:
                return False

            # Проверка на соседние корабли
            for dx in [-1, 0, 1]:
                for dy in [-1, 0, 1]:
                    check_x, check_y = nx + dx, ny + dy
                    if 0 <= check_x < self.size and 0 <= check_y < self.size:
                        if self.grid[check_y][check_x].cell_type == CellType.SHIP:
                            return False

            coordinates.append((nx, ny))

        # Размещаем корабль
        for cx, cy in coordinates:
            self.grid[cy][cx].cell_type = CellType.SHIP
            if ship.ship_type is ShipType.SUBMARINE:
                self.grid[cy][cx].cell_type = CellType.SUBMARINE

        # Сохраняем координаты
        ship.coordinates = coordinates
        self.ships.append(ship)
        return True

    def place_mine(self, x, y):
        cell = self.get_cell(x, y)
        if cell and cell.cell_type == CellType.EMPTY:
            mine = Mine(x, y)
            cell.set_mine(mine)
            self.mines.append(mine)
            return True
        return False

    def check_mine(self, x, y, attacking_player):
        """Проверка на наличие мины - взрыв в радиусе 3x3, наносит урон атакующему"""
        cell = self.get_cell(x, y)
        if cell and cell.has_mine and cell.mine and not cell.mine.triggered:
            damage_cells = []
            affected_ships = []  # Корабли, получившие урон

            # Радиус 3x3 (от -1 до +1 от центра)
            for dx in [-1, 0, 1]:
                for dy in [-1, 0, 1]:
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < self.size and 0 <= ny < self.size:
                        target_cell = self.get_cell(nx, ny)
                        if target_cell:
                            damage_cells.append((nx, ny))

                            # Если есть корабль владельца поля - наносим урон ВЛАДЕЛЬЦУ МИНЫ
                            # (тот, на чьем поле стоит мина, получает урон по своим кораблям)
                            if target_cell.cell_type in [CellType.SHIP, CellType.SUBMARINE]:
                                # Находим корабль владельца этого поля
                                for ship in self.ships:  # self.ships - корабли владельца поля
                                    if (nx, ny) in ship.coordinates and ship not in affected_ships:
                                        ship.hit()
                                        affected_ships.append(ship)
                                        # Помечаем клетку как попадание
                                        target_cell.set_type(CellType.HIT)
                                        break
                            else:
                                # Пустая клетка или мина - помечаем как промах
                                target_cell.set_type(CellType.MISS)

            # Помечаем мину как сработавшую
            cell.mine.triggered = True
            cell.cell_type = CellType.MISS

            return damage_cells
        return []

    def is_valid_shot(self, x, y):
        """Проверка валидности выстрела"""
        cell = self.get_cell(x, y)
        if not cell:
            return False
        return cell.cell_type not in [CellType.HIT, CellType.MISS]

    def receive_shot(self, x, y, player):
        """Обработка выстрела"""
        cell = self.get_cell(x, y)
        if not cell:
            return False, "Выстрел за пределы поля!"

        if not self.is_valid_shot(x, y):
            return False, "Сюда уже стреляли!"

        # Проверка на мину
        mine_damage = self.check_mine(x, y, player)
        if mine_damage:
            return True, f"Подрыв мины! Затронуто {len(mine_damage)} клеток."

        if cell.cell_type in [CellType.SHIP, CellType.SUBMARINE]:
            cell.set_type(CellType.HIT)
            # Находим корабль
            for ship in self.ships:
                if (x, y) in ship.coordinates:
                    ship.hit()
                    if ship.is_sunk():
                        return True, f"Попадание! {ship.name} потоплен!"
                    return True, "Попадание!"

        cell.set_type(CellType.MISS)
        return True, "Промах!"