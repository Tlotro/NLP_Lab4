import telebot
import requests
import jsons
from Class_ModelResponse import ModelResponse

# Замените 'YOUR_BOT_TOKEN' на ваш токен от BotFather
API_TOKEN = '7749412595:AAFccFarT69FUCCV8jmiCCWcp_6KuNTfMZs'
bot = telebot.TeleBot(API_TOKEN)
savedcontext = ""

# Команды
@bot.message_handler(commands=['start'])
def send_welcome(message):
    welcome_text = (
        "Привет! Я ваш Telegram бот.\n"
        "Доступные команды:\n"
        "/start - вывод всех доступных команд\n"
        "/model - вывод названия используемой языковой модели\n"
        "/clear - очистка контекста\n"
        "Отправьте любое сообщение, и я отвечу с помощью LLM модели."
    )
    bot.reply_to(message, welcome_text)

@bot.message_handler(commands=['star'])
def send_welcome(message):
    text = (
        "⭐"
    )
    bot.send_message(message.chat.id, text)


@bot.message_handler(commands=['model'])
def send_model_name(message):
    # Отправляем запрос к LM Studio для получения информации о модели
    response = requests.get('http://localhost:1234/v1/models')

    if response.status_code == 200:
        model_info = response.json()
        model_name = model_info['data'][0]['id']
        bot.reply_to(message, f"Используемая модель: {model_name}")
    else:
        bot.reply_to(message, 'Не удалось получить информацию о модели.')

@bot.message_handler(commands=['clear'])
def send_model_name(message):
    global savedcontext
    savedcontext = ""
    bot.send_message(message.chat.id, "Контекст очищен")


@bot.message_handler(func=lambda message: True)
def handle_message(message):
    user_query = message.text
    global savedcontext
    request = {
        "messages": [
          {
            "role": "user",
            "content": "контекст:\n"+savedcontext + "\nзапрос:\n" + message.text
          },
    ]
  }
    savedcontext += message.text + "\n"
    response = requests.post(
        'http://localhost:1234/v1/chat/completions',
        json=request
    )

    if response.status_code == 200:
        model_response :ModelResponse = jsons.loads(response.text, ModelResponse)
        savedcontext += "ответ: " + message.text + "\n"
        bot.reply_to(message, model_response.choices[0].message.content)
    else:
        bot.reply_to(message, 'Произошла ошибка при обращении к модели.')


# Запуск бота
if __name__ == '__main__':
    bot.polling(none_stop=True)