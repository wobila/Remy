import telebot
import requests
from telebot import types

# Загрузка токена бота из файла
with open('token.txt') as f:
    TOKEN = f.read().strip()

# Загрузка API-ключа от Edamam из файла
with open('edamam_api_key.txt') as f:
    API_KEY = f.read().strip()

# Загрузка ID приложения от Edamam из файла
with open('edamam_app_id.txt') as f:
    APP_ID = f.read().strip()

# Создание бота
bot = telebot.TeleBot(TOKEN)

# Словарь с критериями для поиска рецептов
criteria_dict = {
    'По типу блюда': ['breakfast', 'lunch', 'dinner', 'appetizer', 'dessert'],
    'По кухне': ['italian', 'french', 'japanese', 'mexican', 'chinese'],
    'По типу продукта': ['beef', 'fish', 'vegetables', 'fruits', 'dairy']
}

# Функция для поиска рецептов по критериям с использованием API Edamam
def find_recipes_by_criteria(criteria):
    url = f'https://api.edamam.com/search?q={criteria}&app_id={APP_ID}&app_key={API_KEY}'
    print("URL запроса:", url)  # Вывод URL-адреса запроса в консоль

    response = requests.get(url)
    print("Ответ API:", response.text)  # Вывод содержимого ответа API в консоль

    data = response.json()
    recipes = []
    for hit in data.get('hits', []):
        recipe = hit['recipe']
        recipes.append((recipe['label'], recipe['ingredientLines']))
    return recipes


# Обработчик команды /start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    # Создание клавиатуры с кнопками
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for criteria in criteria_dict:
        markup.add(types.KeyboardButton(criteria))
    bot.send_message(message.chat.id, "Привет! Выберите критерии для поиска рецепта:", reply_markup=markup)

# Обработчик текстовых сообщений с выбором критерия
@bot.message_handler(func=lambda message: message.text in criteria_dict.keys())
def handle_criteria(message):
    # Получение выбранного критерия и отправка клавиатуры с кнопками для выбора подкритериев
    criteria = message.text
    subcriteria = criteria_dict[criteria]
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for subcriterion in subcriteria:
        markup.add(types.KeyboardButton(subcriterion))
    markup.add(types.KeyboardButton('Поиск'))  # Добавляем кнопку "Поиск"
    bot.send_message(message.chat.id, f"Выбран критерий: {criteria}. Выберите подкритерии:", reply_markup=markup)

# Обработчик текстовых сообщений с выбором подкритерия
@bot.message_handler(func=lambda message: message.text in [item for sublist in criteria_dict.values() for item in sublist])
def handle_subcriteria(message):
    # Получение выбранных критериев и сохранение их в данных пользователя
    subcriteria = message.text
    bot.user_data = {'selected_criteria': subcriteria}
    bot.send_message(message.chat.id, f"Выбраны критерии: {subcriteria}. Нажмите кнопку 'Поиск', чтобы найти рецепты.",
                     reply_markup=types.ReplyKeyboardMarkup(resize_keyboard=True).add(types.KeyboardButton('Поиск')))

# Обработчик кнопки поиска
@bot.message_handler(func=lambda message: message.text == 'Поиск')
def handle_search(message):
    # Проверяем, есть ли у пользователя выбранные критерии
    if 'selected_criteria' in bot.user_data:
        criteria = bot.user_data['selected_criteria']
        recipes = find_recipes_by_criteria(criteria)
        if recipes:
            for recipe_title, recipe_ingredients in recipes:
                bot.send_message(message.chat.id, f"Рецепт: {recipe_title}")
                bot.send_message(message.chat.id, f"Ингредиенты: {', '.join(recipe_ingredients)}")
        else:
            bot.reply_to(message, "По вашему запросу не найдено рецептов. Попробуйте другие критерии.")
    else:
        bot.reply_to(message, "Пожалуйста, выберите критерии поиска с помощью кнопок.")

# Запуск бота
bot.polling()
