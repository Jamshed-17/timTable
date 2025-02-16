import telebot
import time
from telebot import types
import datetime
from main import *
import main as main
from config import work_TOKEN, test_TOKEN

bot = telebot.TeleBot(test_TOKEN)

@bot.message_handler(commands=['hey'])
def valentin_day(message):
  text = """Привет, Кать.
Знаешь, иногда программирование приносит очень необычные бонусы.
Например, возможность создать вот такую валентинку.
Так получилось, что я знаю, что тебе подарили несколько валентинок.
Но надеюсь эта станет самой запоминающейся.

Просто хочу сказать тебе, что ты — удивительная.
Ты не просто милая — ты очаровательная.
Не просто красивая — а по-настоящему особенная.
Но самое главное — ты человек с невероятным умом и остроумием.
И это очень восхищает.

В День святого Валентина я хочу пожелать тебе самого настоящего счастья.
Не того, которое идеально выглядит на фотографиях.
А того, которое теплое, искреннее, настоящее.
Счастья в уютных вечерах, в неожиданных приятных мелочах, в улыбках родных людей.
Чтобы каждый день у тебя был повод улыбнуться.

Ты заслуживаешь всего самого лучшего.
И я верю, что у тебя всё получится.
Будь собой — и мир сам раскроет перед тобой все двери.

Эта валентинка строго анонимная.
Ты никогда не догадаешься, кто её отправил. наверное.

Если захочешь перечитать всё заново — просто нажми /hey ещё раз.
А пока — просто наслаждайся моментом и прекрасной музыкой.

С Днём всех влюблённых, Боевой гном)""".split(".")

  for ches in text:
    bot.send_message(message.chat.id, text=ches)
    time.sleep(2)
  audio = open("Data/audio.mp3", "rb")
  bot.send_audio(message.chat.id, audio=audio)
  audio.close
  time.sleep(20)
  bot.send_message(message.chat.id, text="И кстати...\nБУ\n```pyton\nprint('kampfzwerg')\n```", parse_mode="Markdown")
  start(message)
  

@bot.message_handler(commands=['prepod'])
def prepod_tim_table(message):
  del_keyboard = types.ReplyKeyboardRemove()
  bot.send_message(message.chat.id, text="Давайте авторизуемся. Введите фамилию преподавателя", reply_markup = del_keyboard)
  bot.register_next_step_handler(message, prepod_use)
  
def prepod_use(message):
  name = ''
  bot.send_message(message.chat.id, text=f"Загрузка. Одну секунду")
  keyboard = types.ReplyKeyboardMarkup(True, True)
  list = main.prepod_ch(message.text)
  for i in list:
    keyboard.add(i)
    name += i
  bot.send_message(message.chat.id, text="""Выберите своё ФИО из этого списка:\nЕсли список пуст - 
                   фамилия введена неправильно или такой фамилии в текущем расписании нет""", reply_markup=keyboard, parse_mode="Markdown")
  bot.register_next_step_handler(message, prepod_to_DB)
  
def prepod_to_DB(message):
  prepod_to_bd(str(message.text), str(message.chat.id))
  bot.send_message(message.chat.id, text="()JSJSJSJS", parse_mode="Markdown")

  

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
        if j % 120 == 0:
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
    for index in range(0, len(main.groups_for_keyboard(0)), 3):
      row_buttons = main.groups_for_keyboard(0)[index:index + 3] 
      markup.add(*row_buttons)
  elif message.text == "2 курс":
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for index in range(0, len(main.groups_for_keyboard(1)), 3):
      row_buttons = main.groups_for_keyboard(1)[index:index + 3] 
      markup.add(*row_buttons)
  elif message.text == "3 курс":
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for index in range(0, len(main.groups_for_keyboard(2)), 3):
      row_buttons = main.groups_for_keyboard(2)[index:index + 3] 
      markup.add(*row_buttons)
  elif message.text == "4 курс":
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for index in range(0, len(main.groups_for_keyboard(3)), 3):
      row_buttons = main.groups_for_keyboard(3)[index:index + 3] 
      markup.add(*row_buttons)
  elif message.text == "/prepod":
    prepod_tim_table(message)
  elif message.text == "/hey":
    valentin_day(message)
    

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

@bot.message_handler(content_types=['text'])
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
        else:
          bot.send_message(message.chat.id, text="Слишком много запросов за эту секунду. Давай чуть помедленнее")
          start(message)
      elif (message.text == "Сменить группу"):
        start(message)
    except:
      bot.send_message(message.chat.id, text="Либо твой косяк, либо мой. Давай начнём с начала, нажми на /start")
 
  
@bot.callback_query_handler(func=lambda call: call.data == "BD_cout")
def BD_cout_func(call: types.CallbackQuery):
  #Ответ для кнопки, чтобы вывести расписание 
    bot.send_document(call.message.chat.id, open(f'{base_open_admin()}', 'rb'))
   
bot.infinity_polling()
