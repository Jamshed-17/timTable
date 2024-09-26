import requests

def Is_t_group(ID):
    x = 0
    #Получаем доступ к объекту
    client = requests.get(f"https://urtk-journal.ru/api/schedule/group/{ID}")
    #Форматируем его под себя
    data = client.json()
    #Выводим [дату, день недели, предмет]
    for i in range(0, len(data["schedule"])):
        for n in range(0, len(data["schedule"][i]["lessons"])):
            if "name" in data["schedule"][i]["lessons"][n]:
                prepod = ""
                enters = 13 - len(data["schedule"][i]["lessons"][n]["name"].split(" ")[0])
                for j in range(0, len(data["schedule"][i]["lessons"][n]["name"].split(" "))):
                    if j == 0:
                        pass
                    else:
                        prepod = prepod + data["schedule"][i]["lessons"][n]["name"].split(" ")[j] + " "

                lenPrepod = 18 - len(prepod)
                if x == 1 :
                    print(data["schedule"][i]["lessons"][n]["number"],
                          data["schedule"][i]["lessons"][n]["name"].split(" ")[0], " "*enters, prepod," "*lenPrepod, data["schedule"][i]["lessons"][n]["time"], " ", data["schedule"][i]["lessons"][n]["office"])
                else:
                    print("\n", "**", data["schedule"][i]["date"],"**", "\n", "**",data["schedule"][i]["day"],"**",
                          "\n",data["schedule"][i]["lessons"][n]["number"], " ",
                          data["schedule"][i]["lessons"][n]["name"].split(" ")[0],"  ", " "*enters, prepod, " "*lenPrepod, "   ", data["schedule"][i]["lessons"][n]["time"], "   " , data["schedule"][i]["lessons"][n]["office"] ,sep = "")
            else:
                break
            x = 1
        x = 0

Is_t_group(16) #16 - моя группа

