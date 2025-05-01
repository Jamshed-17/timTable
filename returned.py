import json
from collections import defaultdict
import requests
import time


def groups_id():
    list_of_groups = []
    Group_list = requests.get("https://urtk-journal.ru/api/groups/urtk")
    Group_data = Group_list.json()
    for i in range(0, 3):
        for n in range(len(Group_data[i]["groups"])):
            list_of_groups.append(Group_data[i]["groups"][n]["id"])
        
    return list_of_groups

def extract_schedule():
    # Словарь для хранения расписания всех преподавателей
    all_teachers_schedule = defaultdict(list)

    # Получение ID всех групп
    index = groups_id()

    for i in index:
        # Получение данных API для группы
        api_data = f"https://urtk-journal.ru/api/schedule/group/{i}"
        api_data = requests.get(api_data).json()

        group_name = api_data["name"]  # Название группы
        schedule = api_data["schedule"]

        for day_schedule in schedule:
            date = day_schedule["date"]
            day = day_schedule["day"]
            lessons = day_schedule["lessons"]

            for lesson in lessons:
                if lesson.get("name"):  # Проверка, что у урока есть название
                    # Извлечение ФИО преподавателя
                    fio = " ".join(lesson["name"].split()[-3:])
                    try:
                        print(fio)
                        to_fio = fio.split(" ")
                        fio = f"{to_fio[0]} {to_fio[1]}{to_fio[2]}"
                        # fio = fio.replace(fio[fio.index(".")+1], "", 2)
                        print(fio)
                    except: pass
                    
                    # Добавление расписания в словарь для преподавателя
                    all_teachers_schedule[fio].append({
                        "group": group_name,
                        "date": date,
                        "day": day,
                        "name": lesson["name"],
                        "number": lesson["number"],
                        "office": lesson["office"],
                        "sub_group": lesson["sub_group"],
                        "time": lesson["time"]
                    })

    return all_teachers_schedule

def update_teacher_sh():
    """Функция для обновления словаря расписания"""
    # Извлечение расписания
    schedule = extract_schedule()

    # Сохранение расписания всех преподавателей в файл
    with open("Data/teachers_schedule.json", "w", encoding="utf-8") as f:
        json.dump(schedule, f, ensure_ascii=False, indent=4)
        
def multi_update():
    while True:
        update_teacher_sh()
        print("-------------------------------------------------")
        time.sleep(600)