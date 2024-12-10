import telebot
from telebot import types
import datetime
from main import Is_t_group, Group_ID, groupChoise, base_group_name, all_users_cout, base_open_admin

bot = telebot.TeleBot("7136769737:AAEZhLglJIQtGr88HEjqUW8sfx2lYglVHAo")
                     # 7136769737:AAEZhLglJIQtGr88HEjqUW8sfx2lYglVHAo -- Тестовый, 
                     # 7931500372:AAF28kr9FZgftLFkBKHXmW7J3VqnGYKseEQ -- рабочий

@bot.message_handler(commands=['start'])
def start(message):
  if message.chat.username == "Jamshed17":
    bot.send_message(message.chat.id, text="Админка есть".format(message.from_user))
    admin_menu(message)
  else:
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    butn1 = types.KeyboardButton("1 курс")
    butn2 = types.KeyboardButton("2 курс")
    butn3 = types.KeyboardButton("3 курс")
    butn4 = types.KeyboardButton("4 курс")
    markup.add(butn1, butn2, butn3, butn4,)
    bot.send_message(message.chat.id, text="Выбери свой курс".format(message.from_user), reply_markup=markup)
    bot.register_next_step_handler(message, groups)

def admin_menu(message):
  #Меню для админа, в котором можно посомтреть расписание, пользователей и опубликовать что-то
  markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
  gr1 = types.KeyboardButton("🗓️")
  gr2 = types.KeyboardButton("👥")
  gr3 = types.KeyboardButton("🗞️")
  markup.add(gr1, gr2, gr3)
  bot.send_message(message.chat.id, text="Выбери действие".format(message.from_user), reply_markup=markup)
  bot.register_next_step_handler(message, admin_urls)
  
def admin_urls(message):
  #Здесь маршрутизация для админ меню
  if message.text == "🗓️":
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    butn1 = types.KeyboardButton("1 курс")
    butn2 = types.KeyboardButton("2 курс")
    butn3 = types.KeyboardButton("3 курс")
    butn4 = types.KeyboardButton("4 курс")
    markup.add(butn1, butn2, butn3, butn4,)
    bot.send_message(message.chat.id, text="Выбери свой курс".format(message.from_user), reply_markup=markup)
    bot.register_next_step_handler(message, groups)
  elif message.text == "👥":
      markup = telebot.types.InlineKeyboardMarkup(row_width=1)
      but1 = telebot.types.InlineKeyboardButton("Give BD", callback_data="BD_cout")
      markup.add(but1)      
      bot.send_message(message.chat.id, text=f"{all_users_cout()}".format(message.from_user), reply_markup = markup)
      start(message)
  else:
    bot.send_message(message.chat.id, text="Неизвестная команда. Посмотри лучше расписание".format(message.from_user))
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    butn1 = types.KeyboardButton("1 курс")
    butn2 = types.KeyboardButton("2 курс")
    butn3 = types.KeyboardButton("3 курс")
    butn4 = types.KeyboardButton("4 курс")
    markup.add(butn1, butn2, butn3, butn4,)
    bot.send_message(message.chat.id, text="Выбери свой курс".format(message.from_user), reply_markup=markup)
    bot.register_next_step_handler(message, groups)

def groups(message):
  if message.text == "1 курс":
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    gr1 = types.KeyboardButton("1АС1")
    gr2 = types.KeyboardButton("1ИС1")
    gr3 = types.KeyboardButton("1С1")
    gr4 = types.KeyboardButton("1ТО1")
    gr5 = types.KeyboardButton("1ТО2")
    markup.add(gr1, gr2, gr3, gr4, gr5)
  elif message.text == "2 курс":
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    gr1 = types.KeyboardButton("2АС1")
    gr2 = types.KeyboardButton("2ИС1")
    gr3 = types.KeyboardButton("2ИС2")
    gr4 = types.KeyboardButton("2ОС1")
    gr5 = types.KeyboardButton("2С1")
    markup.add(gr1, gr2, gr3, gr4, gr5)
  elif message.text == "3 курс":
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    gr1 = types.KeyboardButton("3АС1")
    gr2 = types.KeyboardButton("3ИС1")
    gr3 = types.KeyboardButton("3ИС2")
    gr4 = types.KeyboardButton("3ОС1")
    gr5 = types.KeyboardButton("3С1")
    gr6 = types.KeyboardButton("3Э1")
    markup.add(gr1, gr2, gr3, gr4, gr5, gr6)
  elif message.text == "4 курс":
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    gr1 = types.KeyboardButton("4АС1")
    gr2 = types.KeyboardButton("4ИС1")
    gr3 = types.KeyboardButton("4ИС2")
    gr4 = types.KeyboardButton("4ОС1")
    gr5 = types.KeyboardButton("4С1")
    markup.add(gr1, gr2, gr3, gr4, gr5)

  bot.send_message(message.chat.id, text="Выбери группу".format(message.from_user),reply_markup=markup)
  bot.register_next_step_handler(message, getIdGroup);

def getIdGroup(message):
  global GroupId
  GroupId = Group_ID(message.text)
  groupChoise(message.text, str(message.chat.id), str(message.chat.username))
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
  week_days = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота", "Вся неделя"]
  try:
    if message.text in week_days:
        bot.send_message(message.chat.id, text=Is_t_group(base_group_name(str(message.chat.id)), str(message.text)), parse_mode="Markdown")
    elif (message.text == "Сменить группу"):
      start(message)
  except:
    bot.send_message(message.chat.id, text="Либо твой косяк, либо мой. Давай начнём с начала, нажми на /start")

@bot.callback_query_handler(func=lambda call: call.data == "BD_cout")
def BD_cout_func(call: types.CallbackQuery):
    bot.send_message(call.message.chat.id, text=f"{str(base_open_admin()).replace("'", '"')}")
   
bot.infinity_polling()