import telebot
import time
from telebot import types
import datetime
from returned import multi_update
from main import *
from threading import Thread
from config import work_TOKEN, test_TOKEN

bot = telebot.TeleBot(work_TOKEN)
# t=Thread(target=multi_update)
# t.start()

@bot.message_handler(commands=['prepod'])
def prepod_tim_table(message):
  try:
    last_prepod = base_prepod_name(str(message.chat.id)).split(" ")[0]
  except: last_prepod = False
  if last_prepod:
    del_keyboard = types.ReplyKeyboardMarkup(True, True)
    btn1 = last_prepod
    del_keyboard.add(btn1)
  else:
    del_keyboard = types.ReplyKeyboardRemove()
  bot.send_message(message.chat.id, text="Давайте авторизуемся. Введите фамилию преподавателя (или часть фамилии)", reply_markup = del_keyboard)
  bot.register_next_step_handler(message, prepod_use)
  
def prepod_use(message):
  name = ''
  bot.send_message(message.chat.id, text=f"Загрузка. Одну секунду")
  keyboard = types.ReplyKeyboardMarkup(True, True)
  list = prepod_ch(message.text)
  for i in list:
    keyboard.add(i)
    name += i
  bot.send_message(message.chat.id, 
                   text="""Выберите своё ФИО из этого списка:\nЕсли список пуст - фамилия введена неправильно или такой фамилии в текущем расписании нет""", 
                   reply_markup=keyboard, parse_mode="Markdown")
  bot.register_next_step_handler(message, prepod_to_DB)
   
def prepod_to_DB(message):
  prepod_to_bd(str(message.text), str(message.chat.id))
  markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
  btn1 = types.KeyboardButton("Понедельник")
  btn2 = types.KeyboardButton("Вторник")
  btn3 = types.KeyboardButton("Среда")
  btn4 = types.KeyboardButton("Четверг")
  btn5 = types.KeyboardButton("Пятница")
  btn6 = types.KeyboardButton("Суббота")
  btn7 = types.KeyboardButton("Вся неделя")
  btn8 = types.KeyboardButton("Главное меню")
  markup.add(btn1, btn2, btn3, btn4, btn5, btn6, btn7, btn8)
  bot.send_message(message.chat.id, text="На какой день недели выдать расписание?"
                   .format(message.from_user), reply_markup=markup)
  bot.register_next_step_handler(message, prepod_day)
  
def prepod_day(message):
  if message.text == "Главное меню":
    start(message)
  elif message.text == "Вся неделя":
    cout_schedule_prepod_week = ""               
    for i in format_teacher_schedule("".join(base_prepod_name(str(message.chat.id)))):
        cout_schedule_prepod_week += f"{i}\n"
    bot.send_message(message.chat.id, 
                     text=cout_schedule_prepod_week, 
                     parse_mode="Markdown")
    bot.register_next_step_handler(message, prepod_day)
  else:
    try:
      bot.send_message(message.chat.id, 
                      text=teach_shredule_cout_day(day=str(message.text), name=base_prepod_name(str(message.chat.id))), 
                      parse_mode="Markdown")
      bot.register_next_step_handler(message, prepod_day)
    except:
      bot.send_message(message.chat.id, 
                     text="Преподаватель в этот день отдыхает, расписания нет. Нажмите на кнопки чтобы продолжить", 
                     parse_mode="Markdown")
      bot.register_next_step_handler(message, prepod_day)

    

@bot.message_handler(commands=['start'])
def start(message):
  if message.chat.username == "Jamshed17":
    bot.send_message(message.chat.id, text="Админка есть".format(message.from_user))
    admin_menu(message)
  else:
    groupChoise(None, str(message.chat.id), str(message.chat.username), None)
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    butn1 = types.KeyboardButton("1 курс")
    butn2 = types.KeyboardButton("2 курс")
    butn3 = types.KeyboardButton("3 курс")
    butn4 = types.KeyboardButton("4 курс")
    markup.add(butn1, butn2, butn3, butn4,)
    bot.send_message(message.chat.id, text="Выбери свой курс".format(message.from_user), reply_markup=markup)
    bot.register_next_step_handler(message, groups)


def admin_menu(message):
  # Меню для админа, в котором можно посомтреть расписание, пользователей и опубликовать что-то
  markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
  gr1 = types.KeyboardButton("🗓️")
  gr2 = types.KeyboardButton("👥")
  gr3 = types.KeyboardButton("🗞️")
  markup.add(gr1, gr2, gr3)
  bot.send_message(message.chat.id, text="Выбери действие".format(message.from_user), reply_markup=markup)
  bot.register_next_step_handler(message, admin_urls)
  
def admin_urls(message):
  # Здесь маршрутизация для админ меню
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
    for i in range (len(all_users_cout())):
      cout = ""
      for j in range(len(all_users_cout()[i])):
        cout += all_users_cout()[i][j]
        if j % 100 == 0:
          bot.send_message(message.chat.id, text=f"{cout}".format(message.from_user))
          cout = ""
          cout += all_users_cout()[i][j]
      bot.send_message(message.chat.id, text=f"{cout}".format(message.from_user))
    else:
      bot.send_message(message.chat.id, text=f"Чтобы вывести список всех пользователей в формате бд - нажмите"
                       .format(message.from_user), reply_markup = markup)

    start(message)
  elif message.text == "🗞️":
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    butn1 = types.KeyboardButton("Отмена")
    markup.add(butn1)
    bot.send_message(message.chat.id, text="Публикуем новость. Отправь текст, который нужно разослать всем пользователям"
                     .format(message.from_user), reply_markup=markup)
    bot.register_next_step_handler(message, news_for_all_users)

def news_for_all_users(message):
  if message.text == "Отмена":
    bot.send_message(message.chat.id, text="Нет так нет".format(message.from_user))
    start(message)
  else:
    list = all_id()
    for i in list:
      bot.send_message(i, text=f"Новость:\n{message.text}".format(message.from_user))
    start(message)


def groups(message):
  # Здесь генерируются кнопки для выбора группы. 
  if message.text == "1 курс":
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for index in range(0, len(groups_for_keyboard(0)), 3):
      row_buttons = groups_for_keyboard(0)[index:index + 3] 
      markup.add(*row_buttons)
  elif message.text == "2 курс":
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for index in range(0, len(groups_for_keyboard(1)), 3):
      row_buttons = groups_for_keyboard(1)[index:index + 3] 
      markup.add(*row_buttons)
  elif message.text == "3 курс":
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for index in range(0, len(groups_for_keyboard(2)), 3):
      row_buttons = groups_for_keyboard(2)[index:index + 3] 
      markup.add(*row_buttons)
  elif message.text == "4 курс":
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for index in range(0, len(groups_for_keyboard(3)), 3):
      row_buttons = groups_for_keyboard(3)[index:index + 3] 
      markup.add(*row_buttons)
  elif message.text == "/prepod":
    prepod_tim_table(message)
    

  bot.send_message(message.chat.id, text="Выбери группу".format(message.from_user),reply_markup=markup)
  bot.register_next_step_handler(message, getIdGroup);

def getIdGroup(message):
  # Здесь можно выбрать день недели
  global GroupId
  GroupId = Group_ID(message.text)
  groupChoise(message.text, str(message.chat.id), str(message.chat.username),
              datetime.datetime.now().strftime('(%Y-%m-%d)%H:%M:%S'))
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
  bot.send_message(message.chat.id, text="На какой день недели тебе выдать расписание?"
                   .format(message.from_user), reply_markup=markup)
  bot.register_next_step_handler(message, func)

def func(message):
  # А это вывод расписания
    time.sleep(0.5)
    week_days = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота", "Вся неделя"]
    try:
      if message.text in week_days:
        now = datetime.datetime.now().strftime('(%Y-%m-%d)%H:%M:%S')
        if time_check(now, str(message.chat.id)) == True:
          bot.send_message(message.chat.id, text=Is_t_group(base_group_name(str(message.chat.id)),
                                                            str(message.text)), parse_mode="Markdown")
          bot.register_next_step_handler(message, func)
        else:
          bot.send_message(message.chat.id, text="Слишком много запросов за эту секунду. Давай чуть помедленнее")
          start(message)
          bot.register_next_step_handler(message, func)
      elif (message.text == "Сменить группу"):
        start(message)
    except:
      bot.send_message(message.chat.id, text="Либо твой косяк, либо мой. Давай начнём с начала, нажми на /start")
 
  
@bot.callback_query_handler(func=lambda call: call.data == "BD_cout")
def BD_cout_func(call: types.CallbackQuery):
  #Ответ для кнопки, чтобы вывести расписание 
    bot.send_document(call.message.chat.id, open(f'{base_open_admin()}', 'rb'))
   
bot.infinity_polling()
