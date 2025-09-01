import json
from collections import defaultdict
import requests
import time
import re


def groups_id():
    list_of_groups = []
    Group_list = requests.get("https://urtk-journal.ru/api/groups/urtk")
    Group_data = Group_list.json()
    for i in range(0, len(Group_data)):
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
                if not lesson.get("name"):  # Пропускаем пустые уроки
                    continue

                # Обрабатываем поле "name": удаляем переносы строк и лишние пробелы
                name_raw = lesson["name"].replace("\n", " ").strip()
                
                # Разделяем на части, если есть "/"
                name_parts = [part.strip() for part in name_raw.split("/") if part.strip()]

                # Обрабатываем каждую часть отдельно
                for part in name_parts:
                    # Извлекаем ФИО преподавателя (последние 2-3 слова)
                    words = part.split()
                    if len(words) < 2:
                        continue  # Пропускаем, если нет ФИО

                    # Ищем фамилию и инициалы (формат "Фамилия И.О." или "Фамилия И. О.")
                    fio_match = re.search(r"([А-ЯЁ][а-яё]+)\s+([А-ЯЁ]\.\s*[А-ЯЁ]\.?)", part)
                    if not fio_match:
                        continue  # Пропускаем, если не нашли ФИО

                    fio = fio_match.group(0).strip()
                    # Приводим к единому формату (убираем лишние пробелы между инициалами)
                    fio = re.sub(r"([А-ЯЁ]\.)\s+([А-ЯЁ]\.)", r"\1\2", fio)

                    # Добавляем запись в расписание преподавателя
                    all_teachers_schedule[fio].append({
                        "group": group_name,
                        "date": date,
                        "day": day,
                        "name": part,  # Сохраняем только часть с текущим преподавателем
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
        time.sleep(600)
        

for i in extract_schedule()["Шестакова Е.Е."]:
    print(i)