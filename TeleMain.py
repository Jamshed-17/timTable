import telebot
import time
import datetime
from telebot import types
from threading import Thread
from functools import wraps
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --------------------------------- Импорты и конфигурация ---------------------------------

try:
    from config import work_TOKEN, test_TOKEN, SCHEDULE_BUDNI, SCHEDULE_SUBBOTA, ADMIN_USERNAME
except ImportError:
    logging.warning("⚠ Не найден config.py. Используются заглушки.")
    work_TOKEN = "TEST_TOKEN"
    test_TOKEN = "TEST_TOKEN"
    ADMIN_USERNAME = "admin"
    SCHEDULE_BUDNI, SCHEDULE_SUBBOTA = {}, {}

from main import *
from prepods import *
from returned import multi_update

# --------------------------------- Инициализация ---------------------------------

bot = telebot.TeleBot(test_TOKEN, exception_handler=telebot.ExceptionHandler())
t = Thread(target=multi_update)
t.daemon = True
t.start()

# --------------------------------- Антиспам ---------------------------------

THROTTLE_TIME = 0.3  # Уменьшено для повышения отзывчивости
THROTTLE_DICT = {}

def rate_limit(func):
    @wraps(func)
    def wrapper(message, *args, **kwargs):
        uid = message.chat.id
        now = time.time()
        if now - THROTTLE_DICT.get(uid, 0) < THROTTLE_TIME:
            return
        THROTTLE_DICT[uid] = now
        return func(message, *args, **kwargs)
    return wrapper

# --------------------------------- Управление состояниями ---------------------------------

USER_STATES = {}

def set_user_state(chat_id, state):
    USER_STATES[chat_id] = state

def get_user_state(chat_id):
    return USER_STATES.get(chat_id, "main")

def clear_user_state(chat_id):
    USER_STATES.pop(chat_id, None)

# --------------------------------- Админ-функции ---------------------------------

def show_users_info(message):
        markup = telebot.types.InlineKeyboardMarkup(row_width=1)
        but1 = telebot.types.InlineKeyboardButton("Give BD", callback_data="BD_cout")
        markup.add(but1)
        for i in range(len(all_users_cout())):
          cout = ""
          for j in range(len(all_users_cout()[i])):
            cout += all_users_cout()[i][j]
            if j % 100 == 0 and j != 0:
              bot.send_message(message.chat.id, text=f"{cout}".format(message.from_user))
              cout = ""
          if cout:
              bot.send_message(message.chat.id, text=f"{cout}".format(message.from_user))
        bot.send_message(message.chat.id, " ", reply_markup=markup)
    
    

def handle_bd_download(message):
    base_open_admin()
    try:
        with open("Data/DB_save.txt", "rb") as file:
            bot.send_document(message.chat.id, file)
    except FileNotFoundError:
        bot.send_message(message.chat.id, "Файл базы данных не найден.")
    except Exception as e:
        logging.error(f"Error downloading BD: {e}")
    admin_menu(message)

def ask_for_news(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    cancel_btn = types.KeyboardButton("Отмена")
    markup.add(cancel_btn)
    bot.send_message(message.chat.id, "Введите текст новости для рассылки или *отправьте медиа (фото/видео) с подписью*:", reply_markup=markup, parse_mode="Markdown")
    set_user_state(message.chat.id, "admin_news")

@bot.message_handler(commands=['admin'])
@rate_limit
def admin_menu(message):
    if message.chat.username and message.chat.username.lower() == ADMIN_USERNAME.lower():
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn_users = types.KeyboardButton("Пользователи")
        btn_bd = types.KeyboardButton("Скачать БД")
        btn_news = types.KeyboardButton("Рассылка")
        btn_update = types.KeyboardButton("Обновить расписание преподов")
        btn_main = types.KeyboardButton("Главное меню")
        markup.add(btn_users, btn_bd)
        markup.add(btn_news, btn_update)
        markup.add(btn_main)
        bot.send_message(message.chat.id, "Добро пожаловать в админ-панель", reply_markup=markup)
        set_user_state(message.chat.id, "admin_menu")
    else:
        bot.send_message(message.chat.id, "У вас нет доступа к этой команде.")

@bot.message_handler(func=lambda message: get_user_state(message.chat.id) == "admin_menu")
@rate_limit
def handle_admin_menu(message):
    if not (message.chat.username and message.chat.username.lower() == ADMIN_USERNAME.lower()):
        clear_user_state(message.chat.id)
        return

    if message.text == "Пользователи":
        show_users_info(message)
    elif message.text == "Скачать БД":
        handle_bd_download(message)
    elif message.text == "Рассылка":
        ask_for_news(message)
    elif message.text == "Обновить расписание преподов":
        bot.send_message(message.chat.id, "Начато принудительное обновление расписания преподавателей...")
        try:
            update_teacher_sh()  # Call single update instead of multi
            bot.send_message(message.chat.id, "✔ Расписание преподавателей успешно обновлено.")
        except Exception as e:
            logging.error(f"Error updating teachers schedule: {e}")
        admin_menu(message)
    elif message.text == "Главное меню":
        clear_user_state(message.chat.id)
        show_main_menu(message)
    else:
        bot.send_message(message.chat.id, "Неизвестная команда в админ-панели.")

@bot.message_handler(content_types=['text', 'photo', 'video'], func=lambda message: get_user_state(message.chat.id) == "admin_news")
@rate_limit
def handle_news_input(message):
    if not (message.chat.username and message.chat.username.lower() == ADMIN_USERNAME.lower()):
        clear_user_state(message.chat.id)
        return

    if message.text == "Отмена":
        bot.send_message(message.chat.id, "Рассылка отменена")
        admin_menu(message)
        return
    
    content_type = 'text'
    file_id = None
    text_content = ""
    caption = ""
    
    if message.photo:
        content_type = 'photo'
        file_id = message.photo[-1].file_id 
        caption = message.caption if message.caption else ""
    elif message.video:
        content_type = 'video'
        file_id = message.video.file_id
        caption = message.caption if message.caption else ""
    elif message.text:
        content_type = 'text'
        text_content = message.text
    else:
        bot.send_message(message.chat.id, "Неподдерживаемый тип контента. Пожалуйста, введите текст, фото или видео.")
        return
        
    try:
        user_ids = all_id()
        success_count = 0
        
        bot.send_message(message.chat.id, f"Начинаю рассылку *{content_type}* для {len(user_ids)} пользователей...", parse_mode="Markdown")
        
        for user_id in user_ids:
            if str(user_id) == str(message.chat.id):
                continue
                
            try:
                prefix = "📢 Новость:\n\n"
                
                if content_type == 'text':
                    message_text = f"{prefix}{text_content}"
                    bot.send_message(user_id, message_text)
                else:
                    message_caption = f"{prefix}{caption}"
                    if content_type == 'photo':
                        bot.send_photo(user_id, file_id, caption=message_caption)
                    elif content_type == 'video':
                        bot.send_video(user_id, file_id, caption=message_caption, supports_streaming=True)
                
                success_count += 1
            except telebot.apihelper.ApiTelegramException as e:
                if e.error_code == 403:
                    logging.info(f"Пользователь {user_id} заблокировал бота.")
                else:
                    logging.error(f"Error sending news to {user_id}: {e}")
                continue  
            
            time.sleep(0.05)  # Уменьшено для повышения скорости, но осторожно с флудом
        
        bot.send_message(message.chat.id, f"Новость ({content_type}) отправлена *{success_count}* пользователям", parse_mode="Markdown")
    except Exception as e:
        logging.error(f"Critical error in news broadcast: {e}")
    
    admin_menu(message)

# --------------------------------- Основное меню ---------------------------------

@bot.message_handler(commands=["start"])
@rate_limit
def start(message):
    clear_user_state(message.chat.id)
    group = base_group_name_string(str(message.chat.id))
    groupChoise(group, str(message.chat.id),
                message.chat.username or None,
                datetime.datetime.now().strftime("(%Y-%m-%d)%H:%M:%S"))
    show_main_menu(message)

def show_main_menu(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("1 курс", "2 курс", "3 курс")
    markup.add("Преподаватели", "Звонки", "4 курс")
    bot.send_message(message.chat.id, "Выбери свой курс или действие:", reply_markup=markup)
    set_user_state(message.chat.id, "main")

# --------------------------------- Расписание звонков ---------------------------------

@bot.message_handler(commands=['zvon'], func=lambda message: get_user_state(message.chat.id) != "admin_news")
@bot.message_handler(func=lambda message: message.text == "Звонки" and get_user_state(message.chat.id) == "main")
@rate_limit
def handle_zvon(message):
    group_name = base_group_name_string(str(message.chat.id))
    groupChoise(group_name, 
                str(message.chat.id), 
                message.chat.username if message.chat.username else None, 
                datetime.datetime.now().strftime('(%Y-%m-%d)%H:%M:%S'))
    show_zvon_schedule(message.chat.id, "Будни")

def show_zvon_schedule(chat_id, day_type):
    schedule = get_zvon_schedule(day_type)
    markup = types.InlineKeyboardMarkup()
    btn_text = "Расписание на Субботу" if day_type == "Будни" else "Расписание на Будни"
    btn_callback = "zvon_subbota" if day_type == "Будни" else "zvon_budni"
    markup.add(types.InlineKeyboardButton(btn_text, callback_data=btn_callback))
    bot.send_message(chat_id, schedule + "\n\nЗвонки в расписании:\n Вкл 👉 /zvonON\n Выкл 👉 /zvonOFF", parse_mode="Markdown", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("zvon_"))
def change_zvon(call):
    chat_id = call.message.chat.id
    if call.data in ["zvon_subbota", "zvon_budni"]:
        new_day = "Суббота" if call.data == "zvon_subbota" else "Будни"
        try:
            bot.delete_message(chat_id, call.message.message_id)
        except Exception as e:
            logging.error(f"Error deleting message: {e}")
        show_zvon_schedule(chat_id, new_day)
    bot.answer_callback_query(call.id)

@bot.message_handler(commands=["zvonON"], func=lambda message: get_user_state(message.chat.id) != "admin_news")
@rate_limit
def zvon_on(message):
    set_user_zvon_setting(str(message.chat.id), True)
    bot.send_message(message.chat.id, "✔ Расписание звонков *включено* и будет отображаться рядом с парами.", parse_mode="Markdown")
    if get_user_state(message.chat.id) == "main":
        show_main_menu(message)

@bot.message_handler(commands=["zvonOFF"], func=lambda message: get_user_state(message.chat.id) != "admin_news")
@rate_limit
def zvon_off(message):
    set_user_zvon_setting(str(message.chat.id), False)
    bot.send_message(message.chat.id, "✗ Расписание звонков *отключено*.", parse_mode="Markdown")
    if get_user_state(message.chat.id) == "main":
        show_main_menu(message)

# --------------------------------- Выбор курса и группы ---------------------------------

@bot.message_handler(func=lambda message: message.text in ["1 курс", "2 курс", "3 курс", "4 курс"] and get_user_state(message.chat.id) == "main")
@rate_limit
def select_course(message):
    num = int(message.text.split()[0])
    groups = groups_for_keyboard(num - 1)
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for i in range(0, len(groups), 3):
        markup.row(*groups[i:i+3])
    markup.add("Главное меню")
    bot.send_message(message.chat.id, f"Выберите группу для {num} курса:", reply_markup=markup)
    set_user_state(message.chat.id, "group_select")

@bot.message_handler(func=lambda message: get_user_state(message.chat.id) == "group_select")
@rate_limit
def select_group(message):
    if message.text == "Главное меню":
        clear_user_state(message.chat.id)
        show_main_menu(message)
        return

    group = message.text
    if not Group_ID(group):
        bot.send_message(message.chat.id, "Такой группы нет. Выберите из списка.")
        return

    groupChoise(group, str(message.chat.id), message.chat.username or None,
                datetime.datetime.now().strftime("(%Y-%m-%d)%H:%M:%S"))
    bot.send_message(message.chat.id, f"Вы выбрали группу *{group}*.", parse_mode="Markdown")
    show_days_menu(message)

def show_days_menu(message):
    days = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота",
            "Сегодня", "Завтра", "Вся неделя"]
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for i in range(0, len(days), 3):
        markup.row(*days[i:i+3])
    markup.add("Сменить группу")
    bot.send_message(message.chat.id, "Выберите день недели:", reply_markup=markup)
    set_user_state(message.chat.id, "day_select")

@bot.message_handler(func=lambda message: get_user_state(message.chat.id) == "day_select")
@rate_limit
def handle_day(message):
    txt = message.text
    if txt == "Сменить группу":
        clear_user_state(message.chat.id)
        show_main_menu(message)
        return

    valid = ["Сегодня", "Завтра", "Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота", "Вся неделя"]
    if txt not in valid:
        bot.send_message(message.chat.id, "Пожалуйста, выберите день из меню.")
        return

    day = txt
    if txt == "Сегодня":
        day = datetime.datetime.now().strftime("%A")
    elif txt == "Завтра":
        day = (datetime.datetime.now() + datetime.timedelta(days=1)).strftime("%A")

    day = (day.replace("Monday", "Понедельник").replace("Tuesday", "Вторник")
               .replace("Wednesday", "Среда").replace("Thursday", "Четверг")
               .replace("Friday", "Пятница").replace("Saturday", "Суббота")
               .replace("Sunday", "Воскресенье"))

    try:
        gid = base_group_name(str(message.chat.id))
        if not gid:
            bot.send_message(message.chat.id, "Сначала выберите группу.")
            clear_user_state(message.chat.id)
            show_main_menu(message)
            return

        schedule = Is_t_group(gid, day, str(message.chat.id))
        bot.send_message(message.chat.id, schedule, parse_mode="Markdown")
    except Exception as e:
        logging.error(f"Error handling day: {e}")
        

# --------------------------------- Преподаватели ---------------------------------

@bot.message_handler(func=lambda message: message.text == "Преподаватели" and get_user_state(message.chat.id) == "main")
@rate_limit
def handle_prepods(message):
    prepod = base_prepod_name(str(message.chat.id))
    if prepod:
        bot.send_message(message.chat.id, f"Ваш преподаватель: *{prepod}*", parse_mode="Markdown")
        show_prepod_menu(message)
    else:
        ask_for_prepod(message)

def ask_for_prepod(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("Главное меню")
    bot.send_message(message.chat.id, "Введите фамилию преподавателя:", reply_markup=markup)
    set_user_state(message.chat.id, "prepod_input")

@bot.message_handler(func=lambda message: get_user_state(message.chat.id) == "prepod_input")
@rate_limit
def input_prepod(message):
    if message.text == "Главное меню":
        clear_user_state(message.chat.id)
        show_main_menu(message)
        return

    lastname = message.text
    matches = prepod_ch(lastname)
    if not matches:
        bot.send_message(message.chat.id, f"Преподаватель '{lastname}' не найден.")
        ask_for_prepod(message)
        return

    if len(matches) == 1:
        prepod_to_bd(matches[0], str(message.chat.id))
        bot.send_message(message.chat.id, f"Выбран преподаватель: *{matches[0]}*", parse_mode="Markdown")
        show_prepod_menu(message)
    else:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        for m in matches:
            markup.add(m)
        markup.add("Главное меню")
        bot.send_message(message.chat.id, "Найдено несколько совпадений. Выберите нужного:", reply_markup=markup)
        set_user_state(message.chat.id, "prepod_select")

@bot.message_handler(func=lambda message: get_user_state(message.chat.id) == "prepod_select")
@rate_limit
def select_prepod(message):
    if message.text == "Главное меню":
        clear_user_state(message.chat.id)
        show_main_menu(message)
        return

    prepod_to_bd(message.text, str(message.chat.id))
    bot.send_message(message.chat.id, f"Выбран преподаватель: *{message.text}*", parse_mode="Markdown")
    show_prepod_menu(message)

def show_prepod_menu(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("Сегодня", "Завтра", "Вся неделя")
    markup.add("Сменить преподавателя", "Главное меню")
    bot.send_message(message.chat.id, "Выберите день или действие:", reply_markup=markup)
    set_user_state(message.chat.id, "prepod_menu")

@bot.message_handler(func=lambda message: get_user_state(message.chat.id) == "prepod_menu")
@rate_limit
def prepod_menu(message):
    if message.text == "Главное меню":
        clear_user_state(message.chat.id)
        show_main_menu(message)
        return
    if message.text == "Сменить преподавателя":
        ask_for_prepod(message)
        return

    if message.text not in ["Сегодня", "Завтра", "Вся неделя"]:
        bot.send_message(message.chat.id, "Выберите действие из меню.")
        return

    prepod = base_prepod_name(str(message.chat.id))
    user_id = str(message.chat.id)
    day = message.text
    if day == "Сегодня":
        day = datetime.datetime.now().strftime("%A")
    elif day == "Завтра":
        day = (datetime.datetime.now() + datetime.timedelta(days=1)).strftime("%A")

    day = (day.replace("Monday", "Понедельник").replace("Tuesday", "Вторник")
               .replace("Wednesday", "Среда").replace("Thursday", "Четверг")
               .replace("Friday", "Пятница").replace("Saturday", "Суббота")
               .replace("Sunday", "Воскресенье"))

    try:
        if message.text == "Вся неделя":
            schedule = format_teacher_schedule(prepod, user_id)
        else:
            schedule = teach_shredule_cout_day(day, prepod, user_id)
        bot.send_message(message.chat.id, schedule, parse_mode="Markdown")
    except Exception as e:
        logging.error(f"Error in prepod menu: {e}")

# --------------------------------- Обработка прочего ---------------------------------

@bot.message_handler(func=lambda message: get_user_state(message.chat.id) == "main")
@rate_limit
def fallback(message):
    bot.send_message(message.chat.id, "Пожалуйста, пользуйтесь кнопками меню 🙂")
    show_main_menu(message)

# --------------------------------- Запуск ---------------------------------

if __name__ == "__main__":
    logging.info("✅ Бот запущен и готов к работе.")
    while True:
        try:
            bot.infinity_polling(skip_pending=True, timeout=30)  # Уменьшен timeout для лучшей отзывчивости
        except Exception as e:
            logging.error(f"Polling error: {e}")
            time.sleep(5)  # Уменьшено время перезапуска для быстрого восстановления