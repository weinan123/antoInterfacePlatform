from untils import configerData
import threading
def runcase(i):
    print "weinannanstart"+str(i)
import schedule,time
def theadungsa():
    lists = configerData.configerData().getItemData("ischange", "changed").split(",")
    print lists
    for i in range(0,len(lists)):
        threading.Thread(target=runcase,args=(lists[i],)).start()
def job1_task():
    schedule.every(10).seconds.do(theadungsa)
job1_task()
while True:
    flag = configerData.configerData().getItemData("ischange", "flag")
    #print flag
    if flag=="true":
        for j in schedule.jobs:
            schedule.cancel_job(j)
        job1_task()
        configerData.configerData().setData("ischange", "flag","flase")
    else:
        pass
    schedule.run_pending()



