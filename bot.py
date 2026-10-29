import telebot
from config import DATABASE, TOKEN
from logic import FoodDatabase

bot = telebot.TeleBot(TOKEN)
db = FoodDatabase(DATABASE)
db.create_tables()

# 1. Обработчик команды /start (приветствие)
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(
        message.chat.id,'''
Привет! Я бот для подсчета калорий. 
Введите название продукта, и я скажу вам, сколько калорий в нем содержится.

Команды:
1. Для добавления нового продукта в базу данных используйте команду /add.
2. Для получения инструкции по использованию бота используйте команду /help.
''')

# 2. Обработчик команды /help (инструкция по использованию бота)
@bot.message_handler(commands=['help'])
def help(message):
    bot.send_message(
        message.chat.id,'''
Команды:
/start - приветствие
/help - инструкция по использованию бота
/add - добавление нового продукта в базу данных
Чтобы узнать количество калорий в продукте, просто введите его название.
''')

# 3. Обработчик текстовых сообщений (все, что не начинается со слэша)
@bot.message_handler(func=lambda message: message.text and not message.text.startswith('/'))
def check_food(message):
    # Получаем название продукта из сообщения пользователя
    food_name = message.text.strip().lower()
    result = db.get_food_info(food_name)

    # Проверяем, найден ли продукт в базе данных, и отправляем соответствующее сообщение пользователю
    if result:
        calories, unit = result
        bot.send_message(
            message.chat.id, f"В продукте {food_name}: {calories} ккал на {unit}."
        )
    else:
        bot.send_message(message.chat.id, "Я не знаю такой продукт 😔")

# 4. Обработчик команды /add (добавление нового продукта в базу данных)
@bot.message_handler(commands=['add'])
def add_food(message):
    # Пользователь написал /add, спрашиваем название
    msg = bot.send_message(
        message.chat.id,'''
Введите название продукта, калории и единицу измерения через пробел.
1. Название продукта может состоять из нескольких слов.
2. Калории должны быть числом.
3. Единицы измерения: г (грамм) или шт (штука).
Пример: гречка 343 100г
''')
    # Регистрируем следующий шаг: перенаправляем ответ в функцию process_add_food
    bot.register_next_step_handler(msg, process_add_food)

def process_add_food(message):
    # Получаем текст сообщения и разбиваем его на части
    message_parts = message.text.lower().split()

    # Проверяем, что сообщение содержит хотя бы 3 части (название, калории и единица измерения)
    if len(message_parts) < 3:
        bot.send_message(message.chat.id, '''
Неверный формат ввода!
Пожалуйста, введите название продукта, калории и единицу измерения через пробел.
Пример: гречка 343 100г''')
        return

    if len(message_parts) > 3:
        bot.send_message(message.chat.id, '''
Неверный формат ввода!
Пожалуйста, введите название продукта, калории и единицу измерения через пробел.
Пример: гречка 343 100г''')
        return

    # Разделяем название продукта, калории и единицу измерения
    name, calories, unit = message_parts

    # Проверяем, что калории являются числом
    if calories.isdigit() == False:
        bot.send_message(message.chat.id, '''
Неверный формат калорий!
Пожалуйста, введите число ккалорий.''')
        return
    
    # Отделим цифры от букв:
    number_part = ''
    alpha_part = ''
    for char in unit:
        if char.isdigit():
            number_part += char
        else:
            alpha_part += char

    # Проверяем, что единица измерения является "г" или "шт"
    if alpha_part not in ['г', 'шт']:
        bot.send_message(message.chat.id, '''
Неверная единица измерения!
Пожалуйста, используйте "г" для грамм или "шт" для штуки.''')
        return

    # Деление количество до 100г, если полшьзователь ввел больше 100г, чтобы хранить в базе данных количество калорий на 100г.
    if alpha_part == 'г' and int(number_part) != 0:
        calories = int(calories) * 100 / int(number_part)
        unit = '100г'

    # Деление количество до 1шт, если полшьзователь ввел больше 1шт, чтобы хранить в базе данных количество калорий на 1шт.
    elif alpha_part == 'шт' and int(number_part) != 0:
        calories = int(calories) / int(number_part)
        unit = '1шт'

    else:
        bot.send_message(message.chat.id, '''
Неверное количество!
Пожалуйста, введите количество больше 0.''')

    # Добавляем продукт в базу данных и отправляем сообщение пользователю о результате. При ошибки отправляем сообщение об ошибке.
    try:
        db.add_food(name, int(calories), unit)
        bot.send_message(message.chat.id, f"✅ Продукт {name} успешно добавлен в базу данных.")

    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Произошла ошибка при добавлении продукта: {str(e)}")

# Сделать удаленеие продукта из базы данных по названию.

# Сделать вывод всех продуктов в базе данных с их калориями и единицами измерения.

# Подумать над структурой базы данных для разный групп продуктов (например, фрукты, овощи, мясо и т.д.) и их калорийностью.
# Возможно, стоит добавить поле "категория" в таблицу food.

# 5. Запуск бота
if __name__ == '__main__':
    print('Бот запущен...')
    bot.infinity_polling()