import random


def get_random_coordinates(size, used_coordinates):
    """Получение случайных координат, которые не использовались"""
    while True:
        x = random.randint(0, size - 1)
        y = random.randint(0, size - 1)
        if (x, y) not in used_coordinates:
            return x, y

def validate_coordinates(x, y, size):
    """Проверка валидности координат"""
    return 0 <= x < size and 0 <= y < size

def parse_input(input_str):
    """Парсинг ввода пользователя"""
    try:
        parts = input_str.strip().split()
        if len(parts) == 2:
            x, y = map(int, parts)
            return 'shot', x, y
        elif len(parts) == 3 and parts[0].lower() == 'тральщик' or parts[0].lower() == '2':
            x, y = map(int, parts[1:])
            return 'tracer', x, y
    except ValueError:
        pass
    return 'invalid', None, None