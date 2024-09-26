import requests


def Is_t_group(ID):
    x = 0
    strokes = ""
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
                enters = 25 - len(data["schedule"][i]["lessons"][n]["name"].split(" ")[0])
                for j in range(0, len(data["schedule"][i]["lessons"][n]["name"].split(" "))):
                    if j == 0:
                        pass
                    else:
                        prepod = prepod + data["schedule"][i]["lessons"][n]["name"].split(" ")[j] + " "

                lenPrepod = 30 - len(prepod)
                if x == 1 :
                    les.append([data["schedule"][i]["lessons"][n]["number"], ". ",
                                data["schedule"][i]["lessons"][n]["name"].split(" ")[0], " " * enters, prepod,
                                " " * lenPrepod, data["schedule"][i]["lessons"][n]["time"], " ",
                                data["schedule"][i]["lessons"][n]["office"]])
                else:
                    les.append(["*", data["schedule"][i]["date"], " ==> ", data["schedule"][i]["day"],"*"])
                    les.append([data["schedule"][i]["lessons"][n]["number"], ". ",
                                data["schedule"][i]["lessons"][n]["name"].split(" ")[0], " " * enters, prepod,
                                " " * lenPrepod, data["schedule"][i]["lessons"][n]["time"], " ",
                                data["schedule"][i]["lessons"][n]["office"]])
                    x = 1
            else:
                print("\n")
                break
        x = 0
        stroke = ""
        for i in range(0, len(les)):
            for j in range(0, len(les[i])):
                stroke = stroke + str(les[i][j])
            stroke = stroke + "\n"
        strokes = strokes + stroke  + "\n"
    return strokes

Is_t_group(16) #16 - моя группа

