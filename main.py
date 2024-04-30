import telebot
import requests
from telebot import types

with open('token.txt') as f:
    TOKEN = f.read().strip()

with open('edamam_api_key.txt') as f:
    API_KEY = f.read().strip()

with open('edamam_app_id.txt') as f:
    APP_ID = f.read().strip()

bot = telebot.TeleBot(TOKEN)

criteria_dict = {
    'По типу блюда': ['breakfast', 'lunch', 'dinner', 'appetizer', 'dessert'],
    'По кухне': ['italian', 'french', 'japanese', 'mexican', 'chinese'],
    'По типу продукта': ['beef', 'fish', 'vegetables', 'fruits', 'dairy']
}


def find_recipes_by_criteria(criteria):
    url = f'https://api.edamam.com/search?q={criteria}&app_id={APP_ID}&app_key={API_KEY}'
    print("URL запроса:", url)

    response = requests.get(url)
    print("Ответ API:", response.text)

    data = response.json()
    recipes = []
    for hit in data.get('hits', []):
        recipe = hit['recipe']
        recipes.append((recipe['label'], recipe['ingredientLines'], recipe['url']))
    return recipes


# Обработчик команды /start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for criteria in criteria_dict:
        markup.add(types.KeyboardButton(criteria))
    bot.send_message(message.chat.id, "Привет! Выберите критерии для поиска рецепта:", reply_markup=markup)


@bot.message_handler(func=lambda message: message.text in criteria_dict.keys())
def handle_criteria(message):
    criteria = message.text
    subcriteria = criteria_dict[criteria]
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for subcriterion in subcriteria:
        markup.add(types.KeyboardButton(subcriterion))
    markup.add(types.KeyboardButton('Поиск'))
    bot.send_message(message.chat.id, f"Выбран критерий: {criteria}. Выберите подкритерии:", reply_markup=markup)


@bot.message_handler(
    func=lambda message: message.text in [item for sublist in criteria_dict.values() for item in sublist])
def handle_subcriteria(message):
    subcriteria = message.text
    bot.user_data = {'selected_criteria': subcriteria}
    bot.send_message(message.chat.id, f"Выбраны критерии: {subcriteria}. Нажмите кнопку 'Поиск', чтобы найти рецепты.",
                     reply_markup=types.ReplyKeyboardMarkup(resize_keyboard=True).add(types.KeyboardButton('Поиск')))


# Обработчик кнопки поиска
@bot.message_handler(func=lambda message: message.text == 'Поиск')
def handle_search(message):
    if 'selected_criteria' in bot.user_data:
        criteria = bot.user_data['selected_criteria']
        recipes = find_recipes_by_criteria(criteria)
        if recipes:
            for recipe_title, recipe_ingredients, recipe_url in recipes:
                response_message = f"**Рецепт:** {recipe_title}\n\n**Ингредиенты:**\n{', '.join(recipe_ingredients)}\n\n[Подробнее]({recipe_url})"
                bot.send_message(message.chat.id, response_message, parse_mode='Markdown')
        else:
            bot.reply_to(message, "По вашему запросу не найдено рецептов. Попробуйте другие критерии.")
    else:
        bot.reply_to(message, "Пожалуйста, выберите критерии поиска с помощью кнопок.")


bot.polling()
