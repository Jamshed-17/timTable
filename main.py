import requests
import json

def Group_ID(group_name):
    Group_list = requests.get("https://urtk-journal.ru/api/groups/urtk")
    Group_data = Group_list.json()
    for i in range(0, len(Group_data)):
        for n in range(0, len(Group_data[i]["groups"])):
            if group_name == Group_data[i]["groups"][n]["name"]:
                #print(Group_data[i]["groups"][n]["name"], Group_data[i]["groups"][n]["id"])
                return Group_data[i]["groups"][n]["id"]

def GroupChekName(group_name):
    Group_list = requests.get("https://urtk-journal.ru/api/groups/urtk")
    Group_data = Group_list.json()
    for i in range(0, len(Group_data)):
        for n in range(0, len(Group_data[i]["groups"])):
            if group_name == Group_data[i]["groups"][n]["name"]:
                #print(Group_data[i]["groups"][n]["name"], Group_data[i]["groups"][n]["id"])
                return True
            else:
                pass
    return False

def Is_t_group(ID, ind):
    x = 0
    y = 0
    chekkk = True
    num = 0
    if ind == 6:
        strokes = ""
    else:
        strokes = []
    #Получаем доступ к объекту
    client = requests.get(f"https://urtk-journal.ru/api/schedule/group/{ID}")
    #Форматируем его под себя
    data = client.json()
    #Выводим [дату, день недели, предмет]
    for i in range(0, len(data["schedule"])):
        les = []
        num = 0
        '''if chekkk == True:
            for y in range(0, len(data["schedule"])):
                if data["schedule"][y]["day"] == "Понедельник":
                    i = y
                    chekkk = False
                    brakeFor = True
                    break'''
            #print(i, data["schedule"][i]["day"])

        for n in range(0, len(data["schedule"][i]["lessons"])-1):
            num = num + 1

            if x == 0:
                les.append(["*", data["schedule"][i]["date"][0:5], " - ", data["schedule"][i]["day"], "* ", "(", data["name"], ")"])
                x = 1

            if "name" in data["schedule"][i]["lessons"][n] and "/" in data["schedule"][i]["lessons"][n]["name"] and "ВПР" not in data["schedule"][i]["lessons"][n]["name"] and "9:20" not in data["schedule"][i]["lessons"][n]["name"]:
                nameInTwo = data["schedule"][i]["lessons"][n]["name"]
                nameInTwo = nameInTwo.split("/")
                nameOne = str(nameInTwo[0])
                nameOne = nameOne.split(" ")
                nameOneList = nameOne[0] + "|" + nameOne[1] #nameOneList - для конечного списка - первая подгруппа
                nameTwo = str(nameInTwo[1])
                nameTwo = nameTwo.split(" ")
                nameTwoList = nameTwo[0] + "|" + nameTwo[1] #nameTwoList - тоже для конечного списка - вторая подгуппа
                officeList = data["schedule"][i]["lessons"][n]["office"]
                officeList = officeList.split("/")
                officeOne = officeList[0]
                officeTwo = officeList[1]
                les.append(["\t"*5, "*", num, "* \n",nameOneList, "гр" , " - ", officeOne, nameTwoList,"гр" , " - ", officeTwo])
                '''elif "9:20" in data["schedule"][i]["lessons"][n]["name"]:
                les.append(["*", num, "* ", "Нач - 9:20", data["schedule"][i]["lessons"][n]["name"].split(" ")[0], " - ", data["schedule"][i]["lessons"][n]["office"]])'''
            else:
                if "name" in data["schedule"][i]["lessons"][n]:
                    for j in range(0, len(data["schedule"][i]["lessons"][n]["name"].split(" "))):
                        if j == 0:
                            pass
                    if x == 1 :
                        les.append(["*", num, "* ", data["schedule"][i]["lessons"][n]["name"].split(" ")[0], " - ", data["schedule"][i]["lessons"][n]["office"]])
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
        return strokes[ind+y]



'''Group_list = requests.get("https://urtk-journal.ru/api/groups/urtk")
Group_data = Group_list.json()

for i in range(0, len(Group_data)):
    for n in range(0, len(Group_data[i]["groups"])):
        for k in range(0, 7):
            print(Is_t_group(Group_data[i]["groups"][n]["id"], k))'''
#print(Is_t_group(16, 6))

def groupChoise(G_name: str, ID: str):
    with open("Data/DataBaseStudent.json", "r") as read_file:
        data = dict(json.load(read_file))
        studentGroupChoise = {"groupName":G_name}
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
    with open("Data/DataBaseStudent.json", "r") as read_file:
        data = dict(json.load(read_file))
        return Group_ID(data[id]["groupName"])
