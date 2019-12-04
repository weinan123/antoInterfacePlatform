'''
import os,time
from untils import configerData
import schedule

def runSchedule():
        pid = os.getpid()
        print pid
        return pid
def runrun():
    pid = os.getpid()
    print pid
    os.system("C:\Python27\python.exe D:/project/auto_interface/antoInterfacePlatform/main/common/projectSchedule.py")
def runScedele():
    flag = configerData.configerData().getItemData("ischange", "changed")
    if flag=="true":
        os.system("taskkill /f /t /im  %d") % os.getpid()
        configerData.configerData().setData("ischange", "changed","false")
        runrun()
    else:
        pass
schedule.every(10).seconds.do(runScedele)
while True:
    schedule.run_pending()
    time.sleep(1)
'''
import weinannanananna
weinannanananna.grtflag(1)

