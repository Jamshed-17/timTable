import telebot
from telebot import types
from main import Is_t_group, Group_ID

bot = telebot.TeleBot("7931500372:AAF28kr9FZgftLFkBKHXmW7J3VqnGYKseEQ")

"""@bot.message_handler(commands=['Group_list'])
def group(message):
  bot.send_message(message.chat.id, text="Напиши название своей группы (большими без побелов)".format(message.from_user))
  group_name = message.upper()
  GroupId = Group_ID(group_name)"""



@bot.message_handler(commands=['start'])
def main(message):
  bot.send_message(message.chat.id, text="""Напиши название своей группы. На выбор: 
  
1АС1 \t 1ИС1 \t 1С1 \t 1ТО1 \t1ТО2

2АС1 \t 2ИС1 \t 2ИС2 \t 2ОС1 \t 2С1

3АС1 \t 3ИС1 \t 3ИС2 \t 3ОС1 \t 3С1 \t 3Э1

4ИС1 \t 4ОС1 \t 4С1 \t 4ИС2 \t 4АС1""".format(message.from_user))
  bot.register_next_step_handler(message, getIdGroup);

"""def start(message):
  markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
  butn1 = types.KeyboardButton("1 курс")
  butn2 = types.KeyboardButton("2 курс")
  butn3 = types.KeyboardButton("3 курс")
  butn4 = types.KeyboardButton("4 курс")
  markup.add(butn1, butn2, butn3, butn4,)
  bot.send_message(message.chat.id, text="Выбери свой курс".format(message.from_user), reply_markup=markup)
  bot.register_next_step_handler(message, firstKurs);

def firstKurs(message):
  markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
  gr1 = types.KeyboardButton("1АС1")
  gr2 = types.KeyboardButton("1ИС1")
  gr3 = types.KeyboardButton("1С1")
  gr4 = types.KeyboardButton("1ТО1")
  gr5 = types.KeyboardButton("1ТО2")
  markup.add(gr1, gr2, gr3, gr4, gr5)
  bot.send_message(message.chat.id, text="Выбери группу".format(message.from_user),reply_markup=markup)"""



def getIdGroup(message):
  global GroupId
  GroupId = Group_ID(message.text)
  markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
  btn1 = types.KeyboardButton("Понедельник")
  btn2 = types.KeyboardButton("Вторник")
  btn3 = types.KeyboardButton("Среда")
  btn4 = types.KeyboardButton("Четверг")
  btn5 = types.KeyboardButton("Пятница")
  btn6 = types.KeyboardButton("Суббота")
  btn7 = types.KeyboardButton("Вся неделя")
  btn8 = types.KeyboardButton("Сменить группу")
  markup.add(btn1, btn2, btn3, btn4, btn5, btn6, btn7, btn8)
  bot.send_message(message.chat.id, text="На какой день недели тебе выдать расписание?".format(message.from_user), reply_markup=markup)


@bot.message_handler(content_types=['text'])
def func(message):
  try:
    if(message.text == "Понедельник"):
        bot.send_message(message.chat.id, text=Is_t_group(GroupId, 0), parse_mode="Markdown")
    elif(message.text == "Вторник"):
        bot.send_message(message.chat.id, text=Is_t_group(GroupId, 1), parse_mode="Markdown")
    elif (message.text == "Среда"):
        bot.send_message(message.chat.id, text=Is_t_group(GroupId, 2), parse_mode="Markdown")
    elif (message.text == "Четверг"):
        bot.send_message(message.chat.id, text=Is_t_group(GroupId, 3), parse_mode="Markdown")
    elif (message.text == "Пятница"):
        bot.send_message(message.chat.id, text=Is_t_group(GroupId, 4), parse_mode="Markdown")
    elif (message.text == "Суббота"):
        bot.send_message(message.chat.id, text=Is_t_group(GroupId, 5), parse_mode="Markdown")
    elif (message.text == "Вся неделя"):
        bot.send_message(message.chat.id, text=Is_t_group(GroupId, 6), parse_mode="Markdown")
    elif (message.text == "Сменить группу"):
      bot.send_message(message.chat.id, text="Уверен, что хочешь сменить группу? Нажми на кнопку ещё раз, если да")
      bot.register_next_step_handler(message, main);
    else:
      bot.send_message(message.chat.id, text="Либо ты накосячил, либо я. Давай начнём с начала, нажми на /start")
  except:
    bot.send_message(message.chat.id, text="Либо ты накосячил, либо я. Давай начнём с начала, нажми на /start")


bot.infinity_polling()