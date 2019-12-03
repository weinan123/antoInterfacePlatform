from untils import configerData
def runcase(i):
    print "weinannanstart"+str(i)
import schedule,time
def theadungsa():
    lists = configerData.configerData().getItemData("ischange", "changed").split(",")
    print lists
    for i in range(0,len(lists)):
        if i == 0:
            schedule.every(1).minute.do(runcase,lists[i])
        else:
            schedule.every(10).seconds.do(runcase,lists[i])
def grtflag():
    schedule.every(10).seconds.do(theadungsa())
theadungsa()
while True:
    times = int(time.time())
    onemin = times % 60
    print onemin
    if onemin == 0:
        for j in schedule.jobs:
            schedule.cancel_job(j)
        theadungsa()
        print schedule.jobs
    else:
        print schedule.jobs
    schedule.run_pending()



