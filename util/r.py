from database import *
import datetime
import time
l=[]
i=100
def add_date():
    global i
    d = {'u':str(100-2*i + 1)}
    i+=1
    da = datetime.datetime.now()
    d['date']=da
    l.append(d)

add_date()
time.sleep(5)
add_date()
time.sleep(5)
add_date()
time.sleep(5)
add_date()
time.sleep(5)
add_date()
time.sleep(5)
l.reverse()
print(l)
l=sorted(l, key=lambda x: x['date'])
print(l)

    