import os
from .player import Player
from package.cells import CellType


class Game:
    """Основной класс игры"""

    def __init__(self):
        self.size = 10
        self.players = []
        self.current_player = 0
        self.game_over = False

    def clear_screen(self):
        """Очистка экрана"""
        os.system('cls' if os.name == 'nt' else 'clear')

    def setup(self):
        """Настройка игры"""
        self.clear_screen()
        print("=" * 50)
        print("        МОРСКОЙ БОЙ С МИНАМИ И ПОДЛОДКАМИ")
        print("=" * 50)
        print("\nОсобенности игры:")
        print("1. Мины - наносят урон при взрыве в радиусе 1 клетки")
        print("2. Подводные лодки - видны только миноискателям")
        print("3. Минные тральщики - обнаруживают и обезвреживают мины и подлодки")
        print("4. Разные корабли имеют специальные способности")
        print("-" * 50)

        # Создаем игроков
        player1_name = input("Введите имя первого игрока: ") or "Игрок 1"
        player2_name = input("Введите имя второго игрока: ") or "Игрок 2"

        self.players.append(Player(player1_name, self.size))
        self.players.append(Player(player2_name, self.size))

        # Расстановка кораблей
        for i, player in enumerate(self.players):
            print(f"\n{player.name}, расставляем корабли...")
            input("Нажмите Enter для автоматической расстановки")
            player.place_ships_randomly()
            player.place_mines_randomly()
            print("Корабли и мины расставлены!")

    def display_boards(self, player_idx):
        """Отображение досок игрока"""
        player = self.players[player_idx]
        enemy = self.players[1 - player_idx]

        print(f"\n{'=' * 60}")
        print(f"ХОД: {player.name}")
        player.display_status()
        print(f"{'=' * 60}")

        print("\nВаше поле:")
        print("Обозначения: ■ - корабли, ▲ - подлодки, ● - мины, X - попадания, ○ - промахи")
        player.board.display(show_ships=True, show_mines=True)

        print(f"\nПоле противника ({enemy.name}):")
        print("Обозначения: X - попадания, ○ - промахи")
        enemy.board.display(show_ships=False, show_mines=False)

    def player_turn(self, player_idx):
        """Очередь хода игрока"""
        player = self.players[player_idx]
        enemy = self.players[1 - player_idx]

        while True:
            self.display_boards(player_idx)

            print("\nДоступные действия:")
            print("1. Сделать выстрел (формат: x y)")
            print("2. Использовать тральщик (формат: тральщик x y)")
            print("   - Обнаруживает и обезвреживает мины и подлодки в радиусе 1 клетки")
            print("3. Показать правила")

            choice = input("\nВаш выбор: ").strip().lower()

            if choice == "3":
                self.show_rules()
                continue

            if choice.startswith("тральщик") or choice.startswith("т"):
                try:
                    parts = choice.split()
                    x, y = int(parts[1]), int(parts[2])
                    success, message = player.use_tracer(x, y, enemy)
                    print(f"\n{message}")
                    if enemy.all_ships_sunk():
                        print(f"\n{'!' * 60}")
                        print(f"ВСЕ КОРАБЛИ ПРОТИВНИКА ПОТОПЛЕНЫ!")
                        print(f"{player.name} ПОБЕДИЛ!")
                        print(f"{'!' * 60}")
                        self.game_over = True
                    if success:
                        return True
                except:
                    print("Ошибка в формате! Используйте: тральщик(т) x y")
                continue

            # Обычный выстрел
            try:
                x, y = map(int, choice.split())

                if not (0 <= x < self.size and 0 <= y < self.size):
                    print("Координаты вне диапазона 0-9!")
                    continue

                # Проверяем подлодки
                cell = enemy.board.get_cell(x, y)
                if cell.cell_type == CellType.SUBMARINE:
                    # Подлодки невидимы для обычных выстрелов
                    print("Промах!")
                    # Помечаем как промах на доске игрока
                    player.enemy_board.get_cell(x, y).set_type(CellType.MISS)
                    return True

                # Обычный выстрел
                valid, message = enemy.board.receive_shot(x, y, enemy)
                if valid:
                    # Обновляем доску врага у игрока
                    enemy_cell = enemy.board.get_cell(x, y)
                    player_cell = player.enemy_board.get_cell(x, y)

                    if enemy_cell.cell_type == CellType.HIT:
                        player_cell.set_type(CellType.HIT)
                    else:
                        player_cell.set_type(CellType.MISS)

                    print(f"\n{message}")

                    # Проверяем потопление всех кораблей
                    if enemy.all_ships_sunk():
                        print(f"\n{'!' * 60}")
                        print(f"ВСЕ КОРАБЛИ ПРОТИВНИКА ПОТОПЛЕНЫ!")
                        print(f"{player.name} ПОБЕДИЛ!")
                        print(f"{'!' * 60}")
                        self.game_over = True

                    return True
                else:
                    print(f"\n{message}")

            except ValueError:
                print("Ошибка ввода! Используйте формат: x y")

    def show_rules(self):
        """Показать правила игры"""
        print("\n" + "=" * 60)
        print("ПРАВИЛА ИГРЫ:")
        print("=" * 60)
        print("\nЦель игры: потопить все корабли противника.")
        print("\nОсобенности:")
        print("1. Мины (●):")
        print("   - Наносят урон в радиусе 1 клетки при взрыве")
        print("   - Невидимы до подрыва")
        print("   - Каждый игрок начинает с 5 минами")
        print("   - Могут быть обезврежены тральщиком")

        print("\n2. Подводные лодки (▲):")
        print("   - Невидимы для обычных выстрелов")
        print("   - Видны и могут быть уничтожены только тральщиком")
        print("   - Занимают 1 клетку")

        print("\n3. Минные тральщики (T):")
        print("   - Обнаруживают и обезвреживают мины и подлодки в радиусе 1 клетки")
        print("   - Мины удаляются с поля")
        print("   - Подлодки немедленно уничтожаются")
        print("   - Использование: 'тральщик x y' или 'т x y'")

        print("\n4. Специальные способности кораблей:")
        print("   - Тральщики: обнаруживают и обезвреживают мины и подлодки")

        print("\nУправление:")
        print("   - Выстрел: введите координаты (x y)")
        print("   - Тральщик: введите 'тральщик x y' или 'т x y'")
        print("   - Координаты: от 0 до 9")
        print("=" * 60)
        input("\nНажмите Enter для продолжения...")

    def play(self):
        """Основной игровой цикл"""
        self.setup()

        while not self.game_over:
            self.player_turn(self.current_player)

            if not self.game_over:
                input("\nНажмите Enter для передачи хода...")
                self.clear_screen()
                self.current_player = 1 - self.current_player

        print("\nИгра завершена!")
        play_again = input("\nХотите сыграть еще? (да/нет): ").lower()
        if play_again.startswith('д'):
            self.__init__()
            self.play()