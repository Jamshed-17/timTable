import requests
import json
import datetime

def Group_ID(group_name):
    #Выдаёт id группы, чтобы выдавать из API
    Group_list = requests.get("https://urtk-journal.ru/api/groups/urtk")
    Group_data = Group_list.json()
    for i in range(0, len(Group_data)):
        for n in range(0, len(Group_data[i]["groups"])):
            if group_name == Group_data[i]["groups"][n]["name"]:
                return Group_data[i]["groups"][n]["id"]

def GroupChekName(group_name):
    #Проверяет наличие такой группы в API
    Group_list = requests.get("https://urtk-journal.ru/api/groups/urtk")
    Group_data = Group_list.json()
    for i in range(0, len(Group_data)):
        for n in range(0, len(Group_data[i]["groups"])):
            if group_name == Group_data[i]["groups"][n]["name"]:
                return True
            else:
                pass
    return False

def Is_t_group(ID, text):
    """
    Преобразовывает данные из API в строку для вывода расисания
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
                les.append(["*", data["schedule"][i]["date"][0:5], " - ", data["schedule"][i]["day"], "* ", "(", data["name"], ")"])
                x = 1
            try:
                if "Кл. час" in data["schedule"][i]["lessons"][n]["name"]:
                    if "name" in data["schedule"][i]["lessons"][n] and "office" in data["schedule"][i]["lessons"][n]:
                        les.append(["*", num, "*) ", data["schedule"][i]["lessons"][n]["name"], " - ", data["schedule"][i]["lessons"][n]["office"]])
           
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
                    les.append(["  "*9, "*", num, "* \n",nameOneList, "гр" , " - ", officeOne, nameTwoList,"гр" , " - ", officeTwo, "\n"])
            except:
                try:
                    if "name" in data["schedule"][i]["lessons"][n]:
                        for j in range(0, len(data["schedule"][i]["lessons"][n]["name"].split(" "))):
                            if j == 0:
                                pass
                        if x == 1 :
                            if data["schedule"][i]["lessons"][n]["name"].split(" ")[1] == "1" or data["schedule"][i]["lessons"][n]["name"].split(" ")[1] == "2":
                                les.append(["*", num, "*) ", data["schedule"][i]["lessons"][n]["name"].split(" ")[0]," ", data["schedule"][i]["lessons"][n]["name"].split(" ")[1], "гр" , " - ", data["schedule"][i]["lessons"][n]["office"]])
                            else:
                                les.append(["*", num, "*) ", data["schedule"][i]["lessons"][n]["name"].split(" ")[0], " - ", data["schedule"][i]["lessons"][n]["office"]])
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
    #Выводит всех пользователей с выранной гоуппой (Админ панель)
    cout = "Все пользователи:\n"
    with open("Data/DataBaseStudent.json", "r") as read_file:
        data = dict(json.load(read_file))
        IDs = list(data.keys())
        x = 0
        for i in IDs:
            x += 1
            cout += f"{x}. @{data[i]["username"]} - {data[i]["groupName"]}\n"
            
        cout = cout[0:-1]
    return cout
        

def groupChoise(G_name: str, ID: str, username:str):
    #Добавляет запись в базу данных
    with open("Data/DataBaseStudent.json", "r") as read_file:
        data = dict(json.load(read_file))
        studentGroupChoise = {"groupName":G_name, "username":username}
        if ID in data.keys():
            if G_name != data[ID]["groupName"]:
                data[ID] = studentGroupChoise
            else:
                pass
        else:
            data[ID] = studentGroupChoise
        with open('Data/DataBaseStudent.json', "w", encoding='utf-8') as write_file:
            json.dump(data, write_file, ensure_ascii=False)

def base_group_name(id):
    #Находит запись пользователя в БД и возвращает последнюю выбранную им группу
    with open("Data/DataBaseStudent.json", "r") as read_file:
        data = dict(json.load(read_file))
        return Group_ID(data[id]["groupName"])
    
def base_open_admin():
    #Выводит базу данных, для сохранения (Админ панель)
    with open("Data/DataBaseStudent.json", "r") as read_file:
        data = dict(json.load(read_file))
    return data