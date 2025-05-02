import requests
import json
import datetime
from prepods import *

def Group_ID(group_name):
    #Выдаёт id группы, чтобы выдавать из API
    Group_list = requests.get("https://urtk-journal.ru/api/groups/urtk")
    Group_data = Group_list.json()
    for i in range(0, len(Group_data)):
        for n in range(0, len(Group_data[i]["groups"])):
            if group_name == Group_data[i]["groups"][n]["name"]:
                return Group_data[i]["groups"][n]["id"]
            
def groups_for_keyboard(course):
    list_of_groups = []
    Group_list = requests.get("https://urtk-journal.ru/api/groups/urtk")
    Group_data = Group_list.json()
    for i in range(len(Group_data[course]["groups"])):
        list_of_groups.append(Group_data[course]["groups"][i]["name"])
        
    return list_of_groups

def Is_t_group(ID, text):
    """
    Преобразовывает данные из API в строку для вывода расписания
    """
    #Получаем доступ к объекту
    client = requests.get(f"https://urtk-journal.ru/api/schedule/group/{ID}")
    #Форматируем его под себя
    data = client.json()
       
    if text != "Вся неделя":
        for i in range(len(data["schedule"])):
            if data["schedule"][i]["day"] == text:
                ind = i 
                break
    else: 
        ind = 6
    x = 0
    num = 0
    if ind == 6:
        strokes = ""
    else:
        strokes = []
    #Выводим [дату, день недели, предмет]
    for i in range(0, len(data["schedule"])):
        les = []
        num = 0
        for n in range(0, len(data["schedule"][i]["lessons"])-1):
            num = num + 1

            if x == 0:
                les.append(["*", data["schedule"][i]["date"][0:5], " - ", data["schedule"][i]["day"],
                            "* ", "(", data["name"], ")"])
                x = 1
            try:
                if "Кл. час" in data["schedule"][i]["lessons"][n]["name"]:
                    if "name" in data["schedule"][i]["lessons"][n] and "office" in data["schedule"][i]["lessons"][n]:
                        les.append(["*", num, "*) ", data["schedule"][i]["lessons"][n]["name"], 
                                    " - ", data["schedule"][i]["lessons"][n]["office"]])
           
                else:
                    nameInTwo = data["schedule"][i]["lessons"][n]["name"]
                    nameInTwo = nameInTwo.split("/")
                    nameOne = str(nameInTwo[0])
                    nameOne = nameOne.split(" ")
                    nameOneList = nameOne[0] + " | " + nameOne[1] #nameOneList - для конечного списка - первая подгруппа
                    nameTwo = str(nameInTwo[1])
                    nameTwo = nameTwo.split(" ")
                    nameTwoList = nameTwo[0] + " | " + nameTwo[1] #nameTwoList - тоже для конечного списка - вторая подгуппа
                    officeList = data["schedule"][i]["lessons"][n]["office"]
                    officeList = officeList.split("/")
                    officeOne = officeList[0]
                    officeTwo = officeList[1]
                    les.append(["  "*9, "*", num, "* \n",nameOneList, "гр" ,
                                " - ", officeOne, nameTwoList,"гр" , " - ", officeTwo, "\n"])
            except:
                try:
                    if "name" in data["schedule"][i]["lessons"][n]:
                        for j in range(0, len(data["schedule"][i]["lessons"][n]["name"].split(" "))):
                            if j == 0:
                                pass
                        if x == 1 :
                            if data["schedule"][i]["lessons"][n]["name"].split(" ")[1] == "1" or data["schedule"][i]["lessons"][n]["name"].split(" ")[1] == "2":
                                les.append(["*", num, "*) ", data["schedule"][i]["lessons"][n]["name"].split(" ")[0],
                                            " ", data["schedule"][i]["lessons"][n]["name"].split(" ")[1], "гр" , " - ",
                                            data["schedule"][i]["lessons"][n]["office"]])
                            else:
                                les.append(["*", num, "*) ", data["schedule"][i]["lessons"][n]["name"].split(" ")[0], " - ",
                                            data["schedule"][i]["lessons"][n]["office"]])
                    else:
                        les.append(str(num))
                except:
                    if "name" in data["schedule"][i]["lessons"][n]:
                        les.append(["*", num, "*) ", data["schedule"][i]["lessons"][n]["name"].split(" ")[0]])
                    else:
                        les.append(str(num))
                    
        x = 0
        if ind != 6:
            stroke = ""
            for ik in range(0, len(les)):
                for j in range(0, len(les[ik])):
                    stroke = stroke + str(les[ik][j])
                stroke = stroke + "\n"
            strokes.append(stroke  + "\n")
        else:
            stroke = ""
            for il in range(0, len(les)):
                for j in range(0, len(les[il])):
                    stroke = stroke + str(les[il][j])
                stroke = stroke + "\n"
            strokes = strokes + stroke + "\n"

    if ind == 6:
        return strokes
    else:
        return strokes[ind]

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
    with open("Data/DBS.json", "r") as read_file:
        data = dict(json.load(read_file))
        studentGroupChoise = {"groupName":G_name, "username":username, "time":time, "prepod": False}
        if ID in data.keys():
            if G_name != data[ID]["groupName"]:
                data[ID] = studentGroupChoise
            else:
                pass
        else:
            data[ID] = studentGroupChoise
        with open('Data/DBS.json', "w", encoding='utf-8') as write_file:
            json.dump(data, write_file, ensure_ascii=False)
            
def time_check(time_of_user, ID):
    #Сравнивает время отправки сообщений пользователем
    with open("Data/DBS.json", "r") as read_file:
        data = dict(json.load(read_file))
        if ID in data.keys():
            last_time = datetime.datetime.strptime(data[ID]["time"], '(%Y-%m-%d)%H:%M:%S')
            data[ID]["time"] = time_of_user
            with open('Data/DBS.json', "w", encoding='utf-8') as write_file:
                json.dump(data, write_file, ensure_ascii=False)
            if last_time < datetime.datetime.strptime(time_of_user, '(%Y-%m-%d)%H:%M:%S'):
                return True
            else:
                return False

def base_group_name(id):
    #Находит запись пользователя в БД и возвращает последнюю выбранную им группу
    with open("Data/DBS.json", "r") as read_file:
        data = dict(json.load(read_file))
        return Group_ID(data[id]["groupName"])

def base_open_admin():
    #Выводит базу данных, для сохранения (Админ панель)
    with open("Data/DBS.json", "r") as read_file:
        data = dict(json.load(read_file))
    write_file = open("Data/DB_save.txt", "w")
    write_file.write(str(data).replace("'", '"'))
    write_file.close()
    return "Data/DB_save.txt"

def all_id():
    #Эта функция возвращает все  id пользователей бота, в виде списка
    with open("Data/DBS.json", "r") as read_file:
        data = dict(json.load(read_file))
        a = []
        for i in data.keys():
            a.append(i)
        return(a)