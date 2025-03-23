import time

def timer(seconds):
    if not isinstance(seconds, int):
        raise ValueError("Ошибка: Введите целое число секунд. Если нужно дробное время, используйте библиотеку time.")

    for i in range(seconds, 0, -1):
        print(f"{i} секунд осталось...")
        time.sleep(1)

    print("Время вышло!")