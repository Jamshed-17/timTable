import telebot
from telebot import types
from main import Is_t_group

bot = telebot.TeleBot("7136769737:AAEZhLglJIQtGr88HEjqUW8sfx2lYglVHAo")
'''@bot.message_handler(commands=['start'])
def start_message(message):
  bot.send_message(message.chat.id, Is_t_group(16), parse_mode="Markdown")'''

@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("Понедельник")
    btn2 = types.KeyboardButton("Вторник")
    btn3 = types.KeyboardButton("Среда")
    btn4 = types.KeyboardButton("Четверг")
    btn5 = types.KeyboardButton("Пятница")
    btn6 = types.KeyboardButton("Суббота")
    markup.add(btn1, btn2, btn3, btn4, btn5, btn6)
    bot.send_message(message.chat.id, text="Привет, {0.first_name}! На какой день недели тебе выдать расписание?".format(message.from_user), reply_markup=markup)


@bot.message_handler(content_types=['text'])
def func(message):
    if(message.text == "Понедельник"):
        bot.send_message(message.chat.id, text=Is_t_group(16, 0), parse_mode="Markdown")
    elif(message.text == "Вторник"):
        bot.send_message(message.chat.id, text=Is_t_group(16, 1), parse_mode="Markdown")
    elif (message.text == "Среда"):
        bot.send_message(message.chat.id, text=Is_t_group(16, 2), parse_mode="Markdown")
    elif (message.text == "Четверг"):
        bot.send_message(message.chat.id, text=Is_t_group(16, 3), parse_mode="Markdown")
    elif (message.text == "Пятница"):
        bot.send_message(message.chat.id, text=Is_t_group(16, 4), parse_mode="Markdown")
    elif (message.text == "Суббота"):
        bot.send_message(message.chat.id, text=Is_t_group(16, 5), parse_mode="Markdown")

bot.infinity_polling()