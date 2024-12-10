from datetime import datetime
import time
a = 9

#Шифровка в str
noww = datetime.now().strftime('(%Y-%m-%d)%H:%M:%S')
time.sleep(0.3)
noww2 = datetime.now().strftime('(%Y-%m-%d)%H:%M:%S')

#Расшифровка из str
x1 = datetime.strptime(noww, '(%Y-%m-%d)%H:%M:%S')
x2 = datetime.strptime(noww2, '(%Y-%m-%d)%H:%M:%S')


if x2 > x1:
    print("Э")
else:
    print("dcbh")
