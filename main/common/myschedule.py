import os,django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "auto_interface.settings")
django.setup()
import schedule,subprocess
from main.untils import configerData,batchstart
def runCase():
    conf = configerData.configerData()
    runcase = conf.getItemData("runcase").split(",")
    scheduleList = []
    for i in runcase:
        if(i!=""):
            scheduleList.append(int(i))
    print scheduleList
    batchstart.start_main(scheduleList)

def runChart():
    cmd1 = "cd\\"
    cmd2 = "d:"
    cmd3 = "cd D:/project/auto_interface/antoInterfacePlatform/main/common"
    cmd4 = "python runChartData.py "
    cmd = cmd1 + " && " + cmd2 + " && " + cmd3 + " && " + cmd4
    while True:
        try:
            subprocess.Popen(cmd, shell=True)
            subprocess.call(cmd, shell=True)
        except Exception as e:
            print e
if __name__ == '__main__':
    runCase()
    '''
    schedule.every(2).seconds.do(runChart)
    schedule.every().day.at('17:49').do(runChart)
    while True:
        schedule.run_pending()
    '''