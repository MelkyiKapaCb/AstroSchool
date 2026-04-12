import random

def guess_the_number():
    # Генерация случайного числа от 1 до 100
    secret_number = random.randint(1, 2)
    attempts = 0

    print("Добро пожаловать в игру 'Угадай число'!")
    print("Я загадал число от 1 до 2. Попробуй угадать.")

    while True:
        try:
            # Получаем догадку от пользователя
            guess = int(input("Введите число: "))
            attempts += 1
            # Проверяем догадку
            if guess < secret_number:
                print("Больше!")
            elif guess > secret_number:
                print("Меньше!")
            else:
                print(f"Поздравляю! Ты угадал число {secret_number} за {attempts} попыток.")
                break  # Выход из цикла при правильном ответе
        except ValueError:
            print("Ошибка: пожалуйста, введите целое число.")

if __name__ == "__main__":
    guess_the_number()