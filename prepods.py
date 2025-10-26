import requests
import json
import datetime
import re
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Импортируем нужные функции для работы с настройками звонков из main
try:
    # Замените 'main' на 'main', если это отдельный файл
    from main import get_user_zvon_setting, get_zvon_time_range 
except ImportError:
    # Заглушки, если import не удался
    logging.warning("ВНИМАНИЕ: Не удалось импортировать функции get_user_zvon_setting/get_zvon_time_range из main.py.")
    def get_user_zvon_setting(user_id): return False
    def get_zvon_time_range(lesson_number, day_of_week): return ""

try:
    from config import SCHEDULE_BUDNI, SCHEDULE_SUBBOTA
except ImportError:
    SCHEDULE_BUDNI = {}
    SCHEDULE_SUBBOTA = {}

def prepod_ch(lastname):
    #Возвращает все возможные варианты ФИО (в API) по принятой фамилии. Возвращает список с однофамильцами
    coincidence = []
    # Ваш фиксированный список преподавателей
    names = ['Кирякова П.В.', 'Комаровская А.В.', 'Брусницына Л.Н.', 'Кочуров А.Л.', 'Бакирова Н.В.',
            'Антонов А.Г.', 'Писцова А.С.', 'Бушмелева Е.А.', 'Аристов Н.М.', 'Бушуева Е.Л.',
            'Королева О.Н.', 'Захарова Н.Г.', 'Калмыкова Н.М.', 'Хлызова А.А.', 'Олейников-Мендрух Е.Н.',
            'Хрущевская Е.С.', 'Тукмачев В.Б.', 'Гребенюк А.П.', 'Русинов Г.А.', 'Захарова О.А.', 'Шестакова Е.Е.',
            'Тучков А.М.', 'Бельтюков А.И.', 'Измайлова Е.В.', 'Бушмелева Т.В.', 'Горецкая Е.А.', 'Соловьева Н.С.',
            'Орлов П.Е.', 'Сергеев М.И.', 'Зеркалий Н.Г.', 'Кириевская О.Р.', 'Потапова Н.В.', 'Кирин С.В.',
            'Устьянцев А.А.', 'Сергеева Е.А.', 'Уварова М.Е.', 'Орешкин М.В.']
            
    for i in names:
        if lastname in i:
            coincidence.append(i)
            
    if not coincidence:
        lastname = lastname.lower()
        return_arr = []
        try:
            Group_list = requests.get("https://urtk-journal.ru/api/groups/urtk", timeout=10)
            Group_list.raise_for_status()
            Group_data = Group_list.json()
            for i in range(0, len(Group_data)):
                for n in range(0, len(Group_data[i]["groups"])):
                    ID = Group_data[i]["groups"][n]["id"]
                    client = requests.get(f"https://urtk-journal.ru/api/schedule/group/{ID}", timeout=10)
                    client.raise_for_status()
                    data = client.json()
                    for x in range(0, len(data["schedule"])):
                        for y in range(0, len(data["schedule"][x]["lessons"])-1):
                            if "name" in data["schedule"][x]["lessons"][y]:
                                check_name = str(data["schedule"][x]["lessons"][y]["name"]).lower()
                                if lastname in check_name:
                                    # Логика извлечения ФИО преподавателя из строки расписания
                                    name_parts = data["schedule"][x]["lessons"][y]["name"].split(" ")
                                    if len(name_parts) >= 3:
                                        name = f"{name_parts[-3]} {name_parts[-2]} {name_parts[-1]}"
                                        return_arr.append(name.strip())          
        except requests.exceptions.RequestException as e:
            logging.error(f"Error in prepod_ch: {e}")
        
        return_arr = list(set(return_arr))
        check_arr = []
        # Фильтрация по совпадению с введенной фамилией
        for i in return_arr:
            if lastname not in i.lower():
                check_arr.append(i)
        
        return list(set(return_arr) - set(check_arr))
    else:
        return coincidence

        
def prepod_to_bd(prepod_name: str, user_id: str):
    #Сохраняет выбранного преподавателя в БД пользователя
    try:
        with open("Data/DBS.json", "r", encoding="utf-8") as file:
            data = dict(json.load(file))
    except Exception:
        data = {}

    if user_id in data:
        # Обновляем только имя препода, сохраняя остальные поля
        data[user_id]["prepod"] = prepod_name
    else:
        # Создаем минимальную запись, если пользователя нет
        data[user_id] = {
            "groupName": None, 
            "username": None, 
            "time": None, 
            "prepod": prepod_name, 
            "show_zvon": False
        }
    
    with open('Data/DBS.json', "w", encoding='utf-8') as write_file:
        json.dump(data, write_file, ensure_ascii=False, indent=4)
            
def base_prepod_name(id):
    #Находит запись пользователя в БД и возвращает имя препода
    try:
        with open("Data/DBS.json", "r", encoding="utf-8") as read_file:
            data = dict(json.load(read_file))
            return data.get(id, {}).get("prepod")
    except Exception as e:
        logging.error(f"Error in base_prepod_name: {e}")
        return None

def format_teacher_schedule(teacher_name, user_id, schedule_file="Data/teachers_schedule.json"):
    """
    Форматирует расписание преподавателя из teachers_schedule.json в читаемый вид.
    Добавлена поддержка настройки show_zvon.
    """
    
    show_zvon = get_user_zvon_setting(user_id) # Получаем настройку
    
    try:
        with open(schedule_file, "r", encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        return f"Файл расписания преподавателей не найден."
    except json.JSONDecodeError:
        return f"Ошибка декодирования файла расписания преподавателей."
    except Exception as e:
        logging.error(f"Error loading teacher schedule: {e}")
        return "Ошибка при загрузке расписания."

    if teacher_name not in data:
        return f"Для преподавателя {teacher_name} расписание не найдено."

    lessons = data[teacher_name]
    schedule_by_date = {}

    # Разбираем фамилию и инициалы для очистки названия предмета
    surname = teacher_name.split()[0]
    # Шаблон для поиска ФИО в формате "Фамилия И.О." или "Фамилия И. О."
    initials_pattern = r"\s*[А-ЯЁ]\.\s*[А-ЯЁ]\.?\s*"
    full_pattern = re.compile(rf"{surname}{initials_pattern}", re.UNICODE | re.IGNORECASE)

    for lesson in lessons:
        date = lesson["date"]
        day = lesson["day"]
        number = lesson["number"]
        group = lesson["group"]
        sub_group = lesson.get("sub_group", "None")

        # Обрабатываем name: убираем переносы строк и лишние пробелы, разбиваем по /
        name_raw = lesson["name"].replace("\n", " ").strip()
        name_parts = [part.strip() for part in name_raw.split("/") if part.strip()]
        
        office_raw = lesson["office"]
        office_parts = []
        # Логика разбиения кабинета
        if "/" in office_raw and "с/р" not in office_raw and "с/з" not in office_raw:
            office_parts = [part.strip() for part in office_raw.split("/")]
        else:
            office_parts.append(office_raw.strip())
                
        # Определяем, какая часть названия относится к текущему преподавателю
        matching_indices = [
            i for i, part in enumerate(name_parts) 
            if full_pattern.search(part)
        ]

        for i in matching_indices:
            name_part = name_parts[i]
            office_part = office_parts[i] if i < len(office_parts) else (office_parts[0] if office_parts else "кабинет не указан")
            office = office_part or "кабинет не указан"

            # Удаляем ФИО преподавателя из названия предмета
            subject_raw = full_pattern.sub("", name_part).strip()

            # Добавляем подгруппу, если она указана
            if sub_group and sub_group != "None":
                # Добавляем "гр", если подгруппа указана и это не просто ее название в строке
                if re.search(rf"\b{sub_group}\b", subject_raw):
                    subject = re.sub(rf"\b{sub_group}\b", f"{sub_group} гр", subject_raw)
                else:
                    subject = f"{subject_raw} {sub_group} гр"
            else:
                subject = subject_raw

            if date not in schedule_by_date:
                schedule_by_date[date] = {"day": day, "lessons": []}

            schedule_by_date[date]["lessons"].append({
                "number": number,
                "name": subject.strip(),
                "group": group,
                "office": office
            })

    # Сортировка по датам
    try:
        sorted_dates = sorted(schedule_by_date.keys(), key=lambda d: datetime.datetime.strptime(d, "%d.%m.%Y"))
    except ValueError:
        # Если формат даты не соответствует "%d.%m.%Y", сортируем по строке
        sorted_dates = sorted(schedule_by_date.keys())


    result_lines = []
    for date in sorted_dates:
        day = schedule_by_date[date]["day"]
        result_lines.append(f"*{date} - {day} ({teacher_name})*")

        sorted_lessons = sorted(schedule_by_date[date]["lessons"], key=lambda x: x["number"])
        last_number = None
        for lesson in sorted_lessons:
            # Добавляем время звонка, если включено
            zvon_time = get_zvon_time_range(lesson['number'], day) if show_zvon else ""
            zvon_separator = f" | {zvon_time}" if zvon_time else ""
            
            prefix = f"*{lesson['number']})*" if lesson['number'] != last_number else "    "
            last_number = lesson['number']
            
            # Форматирование: [№)] [Название предмета] [Группа] - [Кабинет] | [Время звонка]
            result_lines.append(f"{prefix} {lesson['name']} {lesson['group']} - {lesson['office']}{zvon_separator}")

        result_lines.append("")

    return "\n".join(result_lines)


def teach_shredule_cout_day(day: str, name:str, user_id):
    """Эта функция выводит расписание преподавателя по дню недели. day - день недели, name - имя препода"""
    # Теперь вызываем format_teacher_schedule с user_id
    text = format_teacher_schedule(name, user_id) 
    
    if "расписание не найдено" in text or "Файл расписания преподавателей не найден" in text:
        return "Нет расписания для этого преподавателя или расписание отсутствует."
    
    # Фильтрация по дню недели
    if day != "Вся неделя":
        
        daily_schedule_lines = [] 
        in_target_day = False
        
        # Переводим day в формат для поиска в заголовке (например, "Понедельник" или "Пятница")
        day_for_search = day
        
        for line in text.split("\n"):
            # Заголовок дня/даты: "*[Дата] - [День недели] ([Имя преподавателя])*"
            if day_for_search in line and name in line:
                in_target_day = True
                daily_schedule_lines.append(line)
            # Пустая строка после дня - конец текущего дня расписания
            elif in_target_day and not line.strip():
                break
            # Строки расписания
            elif in_target_day:
                daily_schedule_lines.append(line)
        
        if daily_schedule_lines:
            return "\n".join(daily_schedule_lines)
        else:
            return f"Нет расписания для {name} на {day}."
    else:
        # Для "Вся неделя" возвращаем весь текст, который уже отформатирован
        return text