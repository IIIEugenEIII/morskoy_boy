class Ship:
    """Класс корабля"""
    def __init__(self, name, size, ship_type, special_ability=None):
        self.name = name
        self.size = size
        self.ship_type = ship_type
        self.hits = 0
        self.coordinates = []
        self.special_ability = special_ability
        self.used_ability = False

    def is_sunk(self):
        return self.hits >= self.size

    def hit(self):
        self.hits += 1

    def can_use_ability(self):
        return not self.used_ability and not self.is_sunk()

    def __str__(self):
        status = "Потоплен" if self.is_sunk() else f"Жив ({self.size - self.hits}/{self.size})"
        ability = f" | Способность: {self.special_ability}" if self.special_ability else ""
        return f"{self.name}: {status}{ability}"


class Mine:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.triggered = False
        self.blast_radius = 1  # Радиус взрыва 3x3 (от -1 до +1)

    def trigger(self, board, player):
        """Взрыв мины в радиусе 3x3"""
        self.triggered = True
        damage_cells = []

        # НОВОЕ: Взрыв в радиусе 3x3
        for dx in range(-self.blast_radius, self.blast_radius + 1):
            for dy in range(-self.blast_radius, self.blast_radius + 1):
                nx, ny = self.x + dx, self.y + dy
                if 0 <= nx < board.size and 0 <= ny < board.size:
                    damage_cells.append((nx, ny))

        return damage_cells