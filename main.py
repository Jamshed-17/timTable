# main.py with modularization and fixes
import requests
import json
import datetime
from prepods import *
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Импорт из нового файла config.py
try:
    from config import SCHEDULE_BUDNI, SCHEDULE_SUBBOTA 
except ImportError:
    # Заглушки, если config.py не найден, для предотвращения ошибок
    logging.warning("ВНИМАНИЕ: Не найден файл config.py. Проверьте наличие файла и его содержимое.")
    SCHEDULE_BUDNI = {}
    SCHEDULE_SUBBOTA = {}

def Group_ID(group_name):
    #Выдаёт id группы, чтобы выдавать из API
    try:
        Group_list = requests.get("https://urtk-journal.ru/api/groups/urtk", timeout=10)
        Group_list.raise_for_status()
        Group_data = Group_list.json()
        for i in range(0, len(Group_data)):
            for n in range(0, len(Group_data[i]["groups"])):
                if group_name == Group_data[i]["groups"][n]["name"]:
                    return Group_data[i]["groups"][n]["id"]
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching group ID for {group_name}: {e}")
    return None
            
def groups_for_keyboard(course):
    list_of_groups = []
    try:
        Group_list = requests.get("https://urtk-journal.ru/api/groups/urtk", timeout=10)
        Group_list.raise_for_status()
        Group_data = Group_list.json()
        for i in range(len(Group_data[course]["groups"])):
            list_of_groups.append(Group_data[course]["groups"][i]["name"])
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching groups for keyboard: {e}")
    return list_of_groups

# ----------------- Функции для расписания звонков -----------------

def get_zvon_schedule(day_type="Будни"):
    """Возвращает расписание звонков для Будней или Субботы в красивом текстовом формате."""
    schedule = SCHEDULE_BUDNI if day_type == "Будни" else SCHEDULE_SUBBOTA
    
    output = []
    output.append(f"🔔 **РАСПИСАНИЕ ЗВОНКОВ ({day_type})** 🔔\n")
    
    for i, (key, times) in enumerate(schedule.items(), 1):
        
        # Используем эмодзи для номера пары
        number_emoji = {1: '1️⃣', 2: '2️⃣', 3: '3️⃣', 4: '4️⃣', 5: '5️⃣', 6: '6️⃣', 7: '7️⃣'}.get(i, f'*{i}*')
        
        start_time = times[0]
        # Конец второй половины пары (или конец первой, если второй нет)
        end_time = times[3] if len(times) > 3 and times[3] else times[1] 
        
        # Заголовок пары: Общий интервал времени
        output.append(f"{number_emoji} **Пара: {start_time} – {end_time}**")

        # 1-й урок
        output.append(f"   • 1-й урок: {times[0]} – {times[1]}")
        
        # 2-й урок (если есть)
        if len(times) > 3 and times[2]:
            output.append(f"   • 2-й урок: {times[2]} – {times[3]}")
        
        # Перерыв
        break_time = times[-1]
        if break_time and break_time != '—':
            output.append(f"   • Перерыв: *{break_time}*\n")
        else:
            output.append("\n") # Добавляем пустую строку для разделения

    return "\n".join(output).strip()

def get_zvon_time_range(lesson_number: int, day_of_week: str) -> str:
    """
    Возвращает интервал времени от начала первого занятия до конца второго
    для заданной пары и дня недели.
    """
    is_subbota = "суббота" in day_of_week.lower()
    schedule = SCHEDULE_SUBBOTA if is_subbota else SCHEDULE_BUDNI
    
    lesson_key = f"{lesson_number} пара"
    
    if lesson_key in schedule:
        times = schedule[lesson_key]
        # Возвращаем интервал от начала первого занятия (times[0]) до конца второго (times[3])
        return f"{times[0]} - {times[3]}" if len(times) > 3 and times[3] else f"{times[0]} - {times[1]}"
    
    return ""

def get_user_zvon_setting(user_id: str) -> bool:
    """Получает настройку show_zvon для пользователя."""
    try:
        with open("Data/DBS.json", "r", encoding="utf-8") as read_file:
            data = json.load(read_file)
            # По умолчанию False, если поле не найдено
            return data.get(user_id, {}).get("show_zvon", False) 
    except Exception as e:
        logging.error(f"Error getting user zvon setting: {e}")
        return False

def set_user_zvon_setting(user_id: str, value: bool):
    """Устанавливает настройку show_zvon для пользователя."""
    try:
        with open("Data/DBS.json", "r", encoding="utf-8") as read_file:
            data = json.load(read_file)
    except Exception:
        data = {} 
        
    # Обновляем или создаем запись, сохраняя остальные поля
    current_data = data.get(user_id, {})
    current_data["show_zvon"] = value
    data[user_id] = current_data
        
    with open('Data/DBS.json', "w", encoding='utf-8') as write_file:
        json.dump(data, write_file, ensure_ascii=False, indent=4)
                
# ----------------- Основная функция расписания -----------------

def Is_t_group(group_id: str, day_text: str, user_id: str, day_obj: dict | None = None):
    """
    Преобразовывает данные из API в строку расписания.
    day_obj – уже готовый объект дня (используется при рекурсивном вызове «Вся неделя»).
    """
    show_zvon = get_user_zvon_setting(user_id)

    # ------------------------------------------------- Получаем данные -------------------------------------------------
    try:
        client = requests.get(f"https://urtk-journal.ru/api/schedule/group/{group_id}", timeout=10)
        client.raise_for_status()
        data = client.json()
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching group schedule: {e}")
        return "Ошибка при получении расписания. Попробуйте позже."

    schedule_data = data.get("schedule", [])
    group_name = data.get("name", "Группа")

    # ------------------------------------------------- ВСЯ НЕДЕЛЯ -------------------------------------------------
    if day_text == "Вся неделя":
        # Берём только текущую учебную неделю (Пн → Сб)
        today = datetime.datetime.today()
        monday = today - datetime.timedelta(days=today.weekday())          # Понедельник текущей недели
        week_start = monday
        week_end   = monday + datetime.timedelta(days=10) 
        print(week_end)
        # Суббота включительно

        # Список дней, которые попадают в нужный диапазон и не воскресенье
        week_days = [
            d for d in schedule_data
            if d.get("day") != "Воскресенье"
            and (dt := d.get("date")) and (dt := datetime.datetime.strptime(dt, "%d.%m.%Y"))
            and week_start <= dt <= week_end
        ]

        # Формируем расписание, передавая каждый объект дня в рекурсию
        parts = [
            Is_t_group(group_id, d["day"], user_id, day_obj=d)
            for d in week_days
        ]
        return "\n\n".join(filter(None, parts)) or "Расписание на неделю отсутствует."

    # ------------------------------------------------- ОДИН ДЕНЬ -------------------------------------------------
    # Если day_obj передан – используем его, иначе ищем в schedule_data
    target = day_obj or next(
        (d for d in schedule_data if d.get("day") == day_text), None
    )

    if not target:
        return f"Расписание на *{day_text}* отсутствует."

    lessons = target.get("lessons", [])
    lines = []
    
    date_str = target.get("date", "")[:5]
    
    # Заголовок
          
    lines.append(f"*{date_str} - {target['day']} ({group_name})*")

    # Пары
    for lesson in lessons:
        num = lesson.get("number")
        if num is None:
            continue

        zvon = get_zvon_time_range(num, target["day"]) if show_zvon else ""
        zvon_sep = f" | {zvon}" if zvon else ""

        name_raw  = lesson.get("name", "") or ""
        office_raw = lesson.get("office", "") or ""

        try:
            # ---------- подгруппы ----------
            if "/" in name_raw and "/" in office_raw:
                name_parts   = [p.strip() for p in name_raw.split("/")]
                office_parts = [o.strip() for o in office_raw.split("/")]

                def clean(n):
                    n = n.split(" | ")[0]
                    p = n.split()
                    if len(p) >= 2 and p[-1].isupper() and p[-2].isupper():
                        return " ".join(p[:-2])
                    if len(p) >= 2 and len(p[-2]) == 2 and p[-2].endswith('.') \
                       and len(p[-1]) == 2 and p[-1].endswith('.'):
                        return " ".join(p[:-2])
                    return n

                n1 = clean(name_parts[0])
                n2 = clean(name_parts[1]) if len(name_parts) > 1 else ""

                lines.append(
                    f"*{num}*)\n"
                    f"  {n1} - {office_parts[0]}{zvon_sep}\n"
                    f"  {n2} - {office_parts[1]}{zvon_sep}"
                )
                continue

            # ---------- обычная пара ----------
            name_disp = name_raw.split(" | ")[0].split(" / ")[0].strip()
            if "Кл. час" in name_disp:
                lines.append(f"*{num}*) {name_disp} - {office_raw}{zvon_sep}")
            else:
                p = name_disp.split()
                if len(p) > 3:
                    name_disp = " ".join(p[:-3])
                elif len(p) > 2:
                    name_disp = " ".join(p[:-2])
                lines.append(f"*{num}*) {name_disp} - {office_raw}{zvon_sep}")

        except Exception as e:
            logging.error(f"Error processing lesson {target.get('date')} #{num}: {e}")
            lines.append(f"*{num}*){zvon_sep}")

    return "\n".join(lines)

# ----------------- Функции для работы с БД -----------------

def get_user_setting_string(user_id: str) -> str:
    """Возвращает выбранную группу, или преподавателя, или 'None'."""
    try:
        with open("Data/DBS.json", "r", encoding="utf-8") as read_file:
            data = json.load(read_file)
            user_data = data.get(user_id, {})
            
            group = user_data.get("groupName")
            prepod = user_data.get("prepod")
            
            if group:
                return group
            elif prepod:
                return prepod
            else:
                return "None"
    except Exception as e:
        logging.error(f"Error getting user setting: {e}")
        return "None"


def all_users_cout():
    #Выводит всех пользователей с выбранной гоуппой (Админ панель)
    cout = ["Все пользователи:\n"]
    with open("Data/DBS.json", "r") as read_file:
        data = dict(json.load(read_file))
        IDs = list(data.keys())
        x = 0
        i = 0
        return_list = []
        for i in IDs:
            x += 1
            cout.append(f"{x}. @{data[i]["username"]} - {data[i]["groupName"]}\n")
        return_list.append(cout)
    return return_list


def groupChoise(G_name: str, ID: str, username:str, time):
    #Добавляет запись в базу данных
    try:
        with open("Data/DBS.json", "r", encoding="utf-8") as read_file:
            data = json.load(read_file)
    except Exception:
        data = {}

    # Получаем текущие настройки, если пользователь уже есть
    current_data = data.get(ID, {})
    current_show_zvon = current_data.get("show_zvon", False)
    current_prepod = current_data.get("prepod", None)
    
    # Обновляем данные пользователя
    studentGroupChoise = {
        "groupName": G_name, 
        "username": username if username else f"id_{ID}", 
        "time": time, 
        "prepod": current_prepod, 
        "show_zvon": current_show_zvon 
    }
    
    data[ID] = studentGroupChoise
    
    with open('Data/DBS.json', "w", encoding='utf-8') as write_file:
        json.dump(data, write_file, ensure_ascii=False, indent=4)

def base_group_name(id):
    #Находит запись пользователя в БД и возвращает ID последней выбранной им группы
    try:
        with open("Data/DBS.json", "r", encoding="utf-8") as read_file:
            data = dict(json.load(read_file))
            group_name = data.get(id, {}).get("groupName")
            return Group_ID(group_name) if group_name else None
    except Exception as e:
        logging.error(f"Error in base_group_name: {e}")
        return None
    
def base_group_name_string(id):
    #Находит запись пользователя в БД и возвращает название группы
    try:
        with open("Data/DBS.json", "r", encoding="utf-8") as read_file:
            data = dict(json.load(read_file))
            return data.get(id, {}).get("groupName")
    except Exception as e:
        logging.error(f"Error in base_group_name_string: {e}")
        return None

def base_group_name_or_none(user_id):
    """Вспомогательная функция для получения текущей группы или None (используется в TeleMain.py)."""
    try:
        with open("Data/DBS.json", "r") as read_file:
            data = dict(json.load(read_file))
            return data.get(user_id, {}).get("groupName")
    except Exception as e:
        logging.error(f"Error in base_group_name_or_none: {e}")
        return None

def all_id():
    #Выводит все ID пользователей (Админ панель)
    list_of_ID = []
    try:
        with open("Data/DBS.json", "r") as read_file:
            data = dict(json.load(read_file))
            for key in data.keys():
                list_of_ID.append(key)
    except Exception as e:
        logging.error(f"Error in all_id: {e}")
    return list_of_ID

def base_open_admin():
    #Выводит базу данных, для сохранения (Админ панель)
    try:
        with open("Data/DBS.json", "r") as read_file:
            data = json.dumps(dict(json.load(read_file)))
        with open("Data/DB_save.txt", "w") as write_file:
            write_file.write(str(data))
    except Exception as e:
        logging.error(f"Ошибка при сохранении БД: {e}")