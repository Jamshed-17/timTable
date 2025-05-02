import requests
import json
import datetime
import re
from main import *

def prepod_ch(lastname):
    coincidence = []
    names = ['Кириевская О.Р.', 'Хрущевская Е.С.', 'Писцова А.С.', 'Орлов П.Е.', 'Бушмелева Е.А.', 'Антонов А.Г.', 'Комаровская А.В.', 
             'Бельтюков А.И.', 'Русинов Г.А.', 'Коломейцев И.И.', 'Бушмелева Т.В.', 'Брусницына Л.Н.', 'Кирякова П.В.', 'Захарова О.А.', 
             'Устьянцев А.А.', 'Зеркалий Н.Г.', 'Аристов Н.М.', 'Камиров С.М.', 'Гребенюк А.П.', ' С.В.', 'Тучков А.М.', 'Потапова Н.В.', 
             'Тукмачев В.Б.', 'Ворожцова Л.О.', 'Измайлова Е.В.', 'Олейников-Мендрух Е.Н.', 'Бакирова Н.В.', 'Евдокимова С.Н.', 'Грачева Е.П.', 
             'Захарова Н.Г.', 'Бушуева Е.Л.', 'Уварова М.Е.', 'Калмыкова Н.М.', 'Кочуров А.Л.', 'Сергеев М.И.', 'Токманцев Д.А.', 'Соловьева Н.С.']
    for i in names:
        if lastname in i:
            coincidence.append(i)
    if not coincidence:
        #Возвращает все возможные варианты ФИО (в API) по принятой фамилии. Возвращает список с однофамильцами
        lastname = lastname.lower()
        return_arr = []
        Group_list = requests.get("https://urtk-journal.ru/api/groups/urtk")
        Group_data = Group_list.json()
        for i in range(0, len(Group_data)):
            for n in range(0, len(Group_data[i]["groups"])):
                ID = Group_data[i]["groups"][n]["id"]
                client = requests.get(f"https://urtk-journal.ru/api/schedule/group/{ID}")
                data = client.json()
                for x in range(0, len(data["schedule"])):
                    for y in range(0, len(data["schedule"][x]["lessons"])-1):
                        if "name" in data["schedule"][x]["lessons"][y]:
                            check_name = str(data["schedule"][x]["lessons"][y]["name"]).lower()
                            if lastname in check_name:
                                name = ""
                                name += "".join(data["schedule"][x]["lessons"][y]["name"].split(" ")[-3])
                                name += "".join(" ")
                                name += "".join(data["schedule"][x]["lessons"][y]["name"].split(" ")[-2:])
                                return_arr.append(name)          
        
        return_arr = list(set(return_arr))
        check_arr = []
        for i in return_arr:
            if lastname in i.lower():
                pass
            else:
                check_arr.append(i)
        
        return list(set(return_arr) - set(check_arr))
    else:
        return coincidence

        
def prepod_to_bd(prepod_name: str, user_id: str):
    with open("Data/DBS.json", "r") as file:
        data = dict(json.load(file))
        if data[user_id]["prepod"] == False or data[user_id]["prepod"] != prepod_name:
            data[user_id]["prepod"] = prepod_name
        with open('Data/DBS.json', "w", encoding='utf-8') as write_file:
            json.dump(data, write_file, ensure_ascii=False)
            
def base_prepod_name(id):
    #Находит запись пользователя в БД и возвращает препода
    with open("Data/DBS.json", "r") as read_file:
        data = dict(json.load(read_file))
        return data[id]["prepod"]

# Функция для форматирования расписания преподавателя
def format_teacher_schedule(teacher_name, schedule_file="Data/teachers_schedule.json"):
    with open(schedule_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    if teacher_name not in data:
        return f"Для преподавателя {teacher_name} расписание не найдено."

    lessons = data[teacher_name]
    schedule_by_date = {}

    # Разбираем фамилию и инициалы
    surname = teacher_name.split()[0]
    initials_pattern = r"\s*[А-ЯЁ]\.\s*[А-ЯЁ]\.?"
    full_pattern = re.compile(rf"{surname}{initials_pattern}", re.UNICODE)

    for lesson in lessons:
        date = lesson["date"]
        day = lesson["day"]
        number = lesson["number"]
        group = lesson["group"]
        sub_group = lesson.get("sub_group", "None")

        name_parts = [part.strip() for part in lesson["name"].split("/")]
        office_raw = lesson["office"]
        office_parts = [part.strip() for part in office_raw.split("/")] if "/" in office_raw else [office_raw.strip()]

        matching_indices = [
            i for i, part in enumerate(name_parts) if surname in part
        ]

        for i in matching_indices:
            name_part = name_parts[i]
            office_part = office_parts[i] if i < len(office_parts) else (office_parts[0] if office_parts else "кабинет не указан")
            office = office_part or "кабинет не указан"

            # Удаляем фамилию и инициалы из названия
            subject_raw = full_pattern.sub("", name_part).strip()

            # Добавляем "гр" только если подгруппа указана и её нет в названии
            if sub_group and sub_group != "None":
                # Проверяем: есть ли подгруппа как отдельное слово уже в названии
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
                "office": office if office != "с" else "с/р"
            })

    # Сортировка по датам
    sorted_dates = sorted(schedule_by_date.keys(), key=lambda d: datetime.datetime.strptime(d, "%d.%m.%Y"))

    result_lines = []
    for date in sorted_dates:
        day = schedule_by_date[date]["day"]
        result_lines.append(f"{date} - {day} ({teacher_name})")

        sorted_lessons = sorted(schedule_by_date[date]["lessons"], key=lambda x: x["number"])
        last_number = None
        for lesson in sorted_lessons:
            prefix = f"{lesson['number']})" if lesson['number'] != last_number else "   "
            last_number = lesson['number']
            result_lines.append(f"{prefix} {lesson['name']} {lesson['group']} - {lesson['office']}")

        result_lines.append("")

    return "\n".join(result_lines)




def teach_shredule_cout_day(day: str, name:str):
    """Эта функция выводит расписание прерода по дню недели. day - день недели, name - имя препода"""
    #update_teacher_sh()
    string = ""
    returnet_str = ""
    text = format_teacher_schedule(name)
    # print(text)
    if "расписание не найдено" in text:
        return "Нет расписания на этот день"
    else:    
        for i in text:
            string += f"{i}\n"

        for x in string.split("\n\n"):
            for k in x.split("', '"):
                if day in x:
                    # Сортировка
                    ret = ""
                    for i in sorted(x.split("\n")[1:]):
                        ret += f"{i}\n"
                    for d in (str(x.split("\n")[0]) + "\n" + ret).split(","):
                        returnet_str += d.replace("'", "").replace("[", "").replace("]", "") + "\n"
                    
                    return returnet_str
   

'''Этот скрипт был для того, чтобы добавить в базу данных новый ключ
with open("Data/DBS.json", "r") as file:
    data = dict(json.load(file))
    for ID in data.keys():
        studentGroupChoise = {"groupName":data[ID]["groupName"], "username":data[ID]["username"], "time":data[ID]["time"], "prepod": False}
        data[ID] = studentGroupChoise
        with open('Data/DBS.json', "w", encoding='utf-8') as write_file:
            json.dump(data, write_file, ensure_ascii=False)
    print("Ok")
    
'''


