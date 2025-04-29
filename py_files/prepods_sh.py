import json
from collections import defaultdict
import requests

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

# Функция для форматирования расписания преподавателя
def format_teacher_schedule(teacher_name, schedule_file = "Data/teachers_schedule.json"):
    # Читаем расписание из JSON-файла
    with open(schedule_file, "r", encoding="utf-8") as f:
        teacher_schedule = json.load(f)
    
    # Проверяем, есть ли расписание для указанного преподавателя
    if teacher_name not in teacher_schedule:
        return f"Для преподавателя {teacher_name} расписание не найдено."

    # Получаем расписание для указанного преподавателя
    lessons = teacher_schedule[teacher_name]

    # Группируем уроки по дате
    grouped_schedule = {}
    for lesson in lessons:
        date = lesson["date"]
        day = lesson["day"]
        num = lesson["number"]

        # Проверяем, относится ли урок к указанному преподавателю
        if teacher_name not in lesson["name"]:
            continue

        if date not in grouped_schedule:
            grouped_schedule[date] = {"day": day, "lessons": []}

        # Извлекаем только часть расписания, относящуюся к указанному преподавателю
        subject_parts = lesson["name"].split("/")
        office_parts = lesson["office"].split("/")

        for subject, office in zip(subject_parts, office_parts):
            if teacher_name in subject:
                grouped_schedule[date]["lessons"].append({
                    "number": num,
                    "name": subject.strip(),
                    "group": lesson["group"],
                    "office": office.strip(),
                })

    # Формируем строку с расписанием
    formatted_schedule = []
    for date, data in grouped_schedule.items():
        formatted_schedule.append(f"{date} - {data['day']} ({teacher_name})")
        for i, lesson in enumerate(data["lessons"], start=1):
            idx = lesson["number"]
            subject = lesson["name"]
            group = lesson["group"]
            office = lesson["office"] if lesson["office"].strip() else "кабинет не указан"
            formatted_schedule.append(f"{idx}) {subject} {group} - {office}")
        formatted_schedule.append("")  # Пустая строка для разделения дней

    return formatted_schedule


#update_teacher_sh()

for i in range(len(format_teacher_schedule("Коломейцев И. И."))):
    print(i, format_teacher_schedule("Коломейцев И. И.")[i])
