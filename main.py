import requests

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
        for n in range(0, len(data["schedule"][i]["lessons"])):
            if "name" in data["schedule"][i]["lessons"][n]:
                prepod = ""
                #enters = 15 - len(data["schedule"][i]["lessons"][n]["name"].split(" ")[0])
                for j in range(0, len(data["schedule"][i]["lessons"][n]["name"].split(" "))):
                    if j == 0:
                        pass
                    else:
                        prepod = prepod + data["schedule"][i]["lessons"][n]["name"].split(" ")[j] + " "

                lenPrepod = 20 - len(prepod)
                if x == 1 :
                    les.append(["*", data["schedule"][i]["lessons"][n]["number"], ".", "* ",
                                data["schedule"][i]["lessons"][n]["name"].split(" ")[0],"\n", " " * 6, prepod,
                                " " * lenPrepod, data["schedule"][i]["lessons"][n]["time"], "     ",
                                data["schedule"][i]["lessons"][n]["office"], "\n"])
                else:
                    les.append(["*", data["schedule"][i]["date"], " ==> ", data["schedule"][i]["day"],"*"])
                    les.append(["*", data["schedule"][i]["lessons"][n]["number"], ".", "* ",
                                data["schedule"][i]["lessons"][n]["name"].split(" ")[0],"\n", " " * 6, prepod,
                                " " * lenPrepod, data["schedule"][i]["lessons"][n]["time"], "     ",
                                data["schedule"][i]["lessons"][n]["office"], "\n"])
                    x = 1
            else:
                les.append("")

        x = 0
        if ind != 6:
            stroke = ""
            for i in range(0, len(les)):
                for j in range(0, len(les[i])):
                    stroke = stroke + str(les[i][j])
                stroke = stroke + "\n"
            strokes.append(stroke  + "\n")
        else:
            stroke = ""

            for i in range(0, len(les)):
                for j in range(0, len(les[i])):
                    stroke = stroke + str(les[i][j])
                stroke = stroke + "\n"
            strokes = strokes + stroke + "\n"

    if ind == 6:
        return strokes
    else:
        return strokes[ind]


