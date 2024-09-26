import telebot
from main import Is_t_group

bot = telebot.TeleBot("7136769737:AAEZhLglJIQtGr88HEjqUW8sfx2lYglVHAo")
@bot.message_handler(commands=['start'])
def start_message(message):
  bot.send_message(message.chat.id, Is_t_group(16), parse_mode="Markdown")

bot.infinity_polling()