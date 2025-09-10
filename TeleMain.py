import telebot
import time
from telebot import types
import datetime
from returned import multi_update
from main import *
from prepods import *
from threading import Thread
from config import work_TOKEN, test_TOKEN

bot = telebot.TeleBot(test_TOKEN)
t = Thread(target=multi_update)
t.start()

# Состояния для обработки разных сценариев
USER_STATES = {}

def set_user_state(chat_id, state):
    USER_STATES[chat_id] = state

def get_user_state(chat_id):
    return USER_STATES.get(chat_id, "main")

def clear_user_state(chat_id):
    if chat_id in USER_STATES:
        del USER_STATES[chat_id]

@bot.message_handler(commands=['start'])
def start(message):
    clear_user_state(message.chat.id)
    groupChoise(None, str(message.chat.id), str(message.chat.username), None)
    show_main_menu(message)

def show_main_menu(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    butn1 = types.KeyboardButton("1 курс")
    butn2 = types.KeyboardButton("2 курс")
    butn3 = types.KeyboardButton("3 курс")
    butn4 = types.KeyboardButton("4 курс")
    butn5 = types.KeyboardButton("Преподаватели")
    markup.add(butn1, butn2, butn3, butn4, butn5)
    bot.send_message(message.chat.id, "Выбери свой курс", reply_markup=markup)

@bot.message_handler(commands=['prepod'])
def prepod_command(message):
    prepod_tim_table(message)

@bot.message_handler(commands=['admin'])
def admin_command(message):
    admin_menu_inter(message)

@bot.message_handler(func=lambda message: message.text == "Преподаватели")
def handle_prepods_button(message):
    prepod_tim_table(message)

@bot.message_handler(func=lambda message: message.text in ["1 курс", "2 курс", "3 курс", "4 курс"])
def handle_course_selection(message):
    show_groups_menu(message)

def show_groups_menu(message):
    course_map = {
        "1 курс": 0,
        "2 курс": 1, 
        "3 курс": 2,
        "4 курс": 3
    }
    
    course_index = course_map[message.text]
    groups_list = groups_for_keyboard(course_index)
    
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    
    # Добавляем группы по 3 в ряд
    for i in range(0, len(groups_list), 3):
        row = groups_list[i:i+3]
        markup.add(*row)
    
    # Добавляем кнопку возврата
    back_btn = types.KeyboardButton("Назад")
    markup.add(back_btn)
    
    bot.send_message(message.chat.id, "Выбери группу", reply_markup=markup)
    set_user_state(message.chat.id, "group_selection")

@bot.message_handler(func=lambda message: get_user_state(message.chat.id) == "group_selection")
def handle_group_selection(message):
    if message.text == "Назад":
        clear_user_state(message.chat.id)
        show_main_menu(message)
        return
    
    # Проверяем, существует ли такая группа
    try:
        group_id = Group_ID(message.text)
        if group_id:
            GroupId = group_id
            groupChoise(message.text, str(message.chat.id), str(message.chat.username),
                       datetime.datetime.now().strftime('(%Y-%m-%d)%H:%M:%S'))
            show_days_menu(message)
        else:
            bot.send_message(message.chat.id, "Группа не найдена. Попробуйте еще раз.")
    except Exception as e:
        bot.send_message(message.chat.id, "Произошла ошибка при выборе группы. Попробуйте еще раз.")

def show_days_menu(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    days = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота", "Вся неделя", "Сменить группу"]
    
    # Добавляем дни по 2 в ряд
    for i in range(0, len(days), 3):
        row = days[i:i+3]
        markup.add(*row)
    
    bot.send_message(message.chat.id, "На какой день недели тебе выдать расписание?", reply_markup=markup)
    set_user_state(message.chat.id, "day_selection")

@bot.message_handler(func=lambda message: get_user_state(message.chat.id) == "day_selection")
def handle_day_selection(message):
    week_days = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота", "Вся неделя"]
    
    if message.text == "Сменить группу":
        clear_user_state(message.chat.id)
        show_main_menu(message)
        return
    
    if message.text in week_days:
        now = datetime.datetime.now().strftime('(%Y-%m-%d)%H:%M:%S')
        if time_check(now, str(message.chat.id)):
            try:
                schedule = Is_t_group(base_group_name(str(message.chat.id)), message.text)
                bot.send_message(message.chat.id, schedule, parse_mode="Markdown")
            except Exception as e:
                bot.send_message(message.chat.id, "Произошла ошибка при получении расписания.")
        else:
            bot.send_message(message.chat.id, "Слишком много запросов. Подождите немного.")
    else:
        bot.send_message(message.chat.id, "Пожалуйста, выберите день из предложенных вариантов.")

# ---------------------------------admin-------------------------------------------
def admin_menu(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    gr1 = types.KeyboardButton("🗓️ Расписание")
    gr2 = types.KeyboardButton("👥 Пользователи")
    gr3 = types.KeyboardButton("🗞️ Новости")
    back_btn = types.KeyboardButton("Главное меню")
    markup.add(gr1, gr2, gr3, back_btn)
    bot.send_message(message.chat.id, "Выбери действие", reply_markup=markup)
    set_user_state(message.chat.id, "admin_menu")

@bot.message_handler(func=lambda message: get_user_state(message.chat.id) == "admin_menu")
def handle_admin_menu(message):
    if message.text == "Главное меню":
        clear_user_state(message.chat.id)
        start(message)
    elif message.text == "🗓️ Расписание":
        show_main_menu(message)
    elif message.text == "👥 Пользователи":
        show_users_info(message)
    elif message.text == "🗞️ Новости":
        ask_for_news(message)
    else:
        bot.send_message(message.chat.id, "Пожалуйста, выберите действие из меню")

def show_users_info(message):
    try:
        markup = telebot.types.InlineKeyboardMarkup(row_width=1)
        but1 = telebot.types.InlineKeyboardButton("Give BD", callback_data="BD_cout")
        markup.add(but1)
        for i in range(len(all_users_cout())):
          cout = ""
          for j in range(len(all_users_cout()[i])):
            cout += all_users_cout()[i][j]
            if j % 100 == 0:
              bot.send_message(message.chat.id, text=f"{cout}".format(message.from_user))
              cout = ""
              cout += all_users_cout()[i][j]
          bot.send_message(message.chat.id, text=f"{cout}".format(message.from_user))
    except Exception as e:
        bot.send_message(message.chat.id, f"Ошибка при получении информации о пользователях: {e}")
    
    markup = types.InlineKeyboardMarkup()
    bd_btn = types.InlineKeyboardButton("📊 Получить базу данных", callback_data="BD_cout")
    markup.add(bd_btn)
    bot.send_message(message.chat.id, "Дополнительные действия:", reply_markup=markup)

def ask_for_news(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    cancel_btn = types.KeyboardButton("Отмена")
    markup.add(cancel_btn)
    bot.send_message(message.chat.id, "Введите текст новости для рассылки:", reply_markup=markup)
    set_user_state(message.chat.id, "news_input")

@bot.message_handler(func=lambda message: get_user_state(message.chat.id) == "news_input")
def handle_news_input(message):
    if message.text == "Отмена":
        bot.send_message(message.chat.id, "Рассылка отменена")
        admin_menu(message)
    else:
        try:
            user_ids = all_id()
            success_count = 0
            for user_id in user_ids:
                try:
                    bot.send_message(user_id, f"📢 Новость:\n\n{message.text}")
                    success_count += 1
                except Exception as e:
                    continue  # Пропускаем неактивных пользователей
            
            bot.send_message(message.chat.id, f"Новость отправлена {success_count} пользователям")
        except Exception as e:
            bot.send_message(message.chat.id, f"Ошибка при рассылке: {e}")
        
        admin_menu(message)

@bot.callback_query_handler(func=lambda call: call.data == "BD_cout")
def handle_bd_download(call):
    try:
        file_path = base_open_admin()
        with open(file_path, 'rb') as file:
            bot.send_document(call.message.chat.id, file)
    except Exception as e:
        bot.send_message(call.message.chat.id, f"Ошибка при загрузке файла: {e}")

@bot.message_handler(commands=["admin"])
def admin_menu_inter(message):
    if message.chat.username == "Jamshed17":
        admin_menu(message)
    else:
        bot.send_message(message.chat.id, "У вас недостаточно прав")
        start(message)

# ---------------------------------prepods-----------------------------------------
def prepod_tim_table(message):
    try:
        last_prepod = base_prepod_name(str(message.chat.id)).split(" ")[0]
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(last_prepod)
    except:
        markup = types.ReplyKeyboardRemove()
    
    bot.send_message(message.chat.id, "Введите фамилию преподавателя (первые 3 буквы):", reply_markup=markup)
    set_user_state(message.chat.id, "prepod_input")

@bot.message_handler(func=lambda message: get_user_state(message.chat.id) == "prepod_input")
def handle_prepod_input(message):
    prepod_list = prepod_ch(message.text)
    
    if not prepod_list:
        bot.send_message(message.chat.id, "Преподаватель не найден. Попробуйте еще раз.")
        return
    
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for prepod in prepod_list:
        markup.add(prepod)
    
    back_btn = types.KeyboardButton("Назад")
    markup.add(back_btn)
    
    bot.send_message(message.chat.id, "Выберите преподавателя:", reply_markup=markup)
    set_user_state(message.chat.id, "prepod_selection")

@bot.message_handler(func=lambda message: get_user_state(message.chat.id) == "prepod_selection")
def handle_prepod_selection(message):
    if message.text == "Назад":
        clear_user_state(message.chat.id)
        show_main_menu(message)
        return
    
    try:
        prepod_to_bd(message.text, str(message.chat.id))
        show_prepod_menu(message)
    except Exception as e:
        bot.send_message(message.chat.id, "Ошибка при выборе преподавателя")
        prepod_tim_table(message)

def show_prepod_menu(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    schedule_btn = types.KeyboardButton("Вывести расписание")
    main_menu_btn = types.KeyboardButton("Главное меню")
    markup.add(schedule_btn, main_menu_btn)
    
    bot.send_message(message.chat.id, "Выберите действие:", reply_markup=markup)
    set_user_state(message.chat.id, "prepod_menu")

@bot.message_handler(func=lambda message: get_user_state(message.chat.id) == "prepod_menu")
def handle_prepod_menu(message):
    if message.text == "Главное меню":
        clear_user_state(message.chat.id)
        start(message)
    elif message.text == "Вывести расписание":
        try:
            prepod_name = base_prepod_name(str(message.chat.id))
            schedule = format_teacher_schedule(prepod_name)
            bot.send_message(message.chat.id, schedule, parse_mode="Markdown")
        except Exception as e:
            bot.send_message(message.chat.id, "Ошибка при получении расписания")
    else:
        bot.send_message(message.chat.id, "Пожалуйста, выберите действие из меню")

# Обработчик для любых других сообщений
@bot.message_handler(func=lambda message: True)
def handle_other_messages(message):
    current_state = get_user_state(message.chat.id)
    
    if current_state == "main":
        # Если пользователь в главном меню, но отправил непонятное сообщение
        bot.send_message(message.chat.id, "Пожалуйста, используйте кнопки для навигации")
        show_main_menu(message)
    else:
        # Для других состояний просто просим использовать кнопки
        bot.send_message(message.chat.id, "Пожалуйста, используйте предложенные варианты")

if __name__ == "__main__":
    bot.infinity_polling()