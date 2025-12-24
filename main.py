from package.game import Game

def main():
    """Главная функция"""
    game = Game()
    try:
        game.play()
    except KeyboardInterrupt:
        print("\n\nИгра прервана. До свидания!")
    except Exception as e:
        print(f"\nПроизошла ошибка: {e}")

if __name__ == "__main__":
    main()