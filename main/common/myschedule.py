# -*- coding: UTF-8 -*-
import os,django
import sys
reload(sys)
import runChartData,sendmail_exchange
import mulSQL,time
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "auto_interface.settings")
django.setup()
from main.models import projectschedule,apiInfoTable,projectList,moduleList
import schedule,subprocess,batchstart
from main.untils import configerData
from main import apiinfo
'''
定时批量执行用例
'''
def getbatchrunList(idlist):
    batchrun_list = []
    try:
        projectname_list = projectList.objects.all().values("projectName").distinct()
    except Exception as e:
        print(u"error: %s" % str(e))
        return batchrun_list
    for pm in projectname_list:
        batchrun_dict = {}
        list = []
        for id in idlist:
            try:
                projectid = moduleList.objects.get(
                    id=int(apiInfoTable.objects.get(apiID=int(id)).owningListID)).owningListID
                projectname = projectList.objects.get(id=int(projectid)).projectName
                if str(projectname) == str(pm["projectName"]):
                    list.append(id)
            except Exception as e:
                print(u"error: %s" % str(e))
                continue
        if len(list) == 0:
            continue
        else:
            cookieslist = projectschedule.objects.filter(projectname=str(pm["projectName"])).values("cookies")
            if len(cookieslist)==0:
                cookies = {}
            else:
                cookies = cookieslist[0]["cookies"]
            print cookies
            batchrun_dict = {"sname": str(pm["projectName"]), "list": list, "cookices": cookies}
            batchrun_list.append(batchrun_dict)
    return batchrun_list
def runCase(ismail):
    conf = configerData.configerData()
    runcase = conf.getItemData("configerinfor","runcase").split(",")
    environment = conf.getItemData("configerinfor","eviorment")
    scheduleList = []
    for i in runcase:
        if(i!=""):
            scheduleList.append(int(i))
    print scheduleList
    schedulePList = getbatchrunList(scheduleList)
    print schedulePList
    reportName = u"定时接口批量执行报告"
    starttime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    isreport = conf.getItemData("configerinfor", "isreport")

    batchResult = batchstart.start_main(schedulePList,environment,isreport,"")
    successNum = batchResult["sNum"]
    faileNum = batchResult["fNum"]
    errorNum = batchResult["eNum"]
    totalNum = successNum+faileNum+errorNum
    if(isreport=='Y'):
        reportPath = "\\"+batchResult["reportPath"]
        print reportPath
        exeuser = ""
        endtime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        print reportName,starttime,endtime,totalNum,successNum,faileNum,errorNum,exeuser,reportPath
        sql = "insert into main_reports(report_runName,startTime,endTime,totalNum,successNum,failNum,errorNum,executor,environment,report_localName)" \
              "values ('%s','%s','%s','%s','%s','%s','%s','%s','%s','%s')"%(reportName,starttime,endtime,totalNum,successNum,faileNum,errorNum,exeuser,environment,reportPath)
        mulSQL.mulSql().insertData(sql)
    else:
        pass
    if(ismail=="Y"):
        getEamilData(isreport,successNum,faileNum,errorNum)
'''
图表数据定时更新
'''
def runChart():
    getChartData = runChartData.getChartData()
    getChartData.nullmodel()
'''
获取配置文件数据，是否生成报告及发送邮件
'''
def getCofigerData():
    conf = configerData.configerData()
    isreport = conf.getItemData("configerinfor","isreport")
    ismail = conf.getItemData("configerinfor","ismail")
    sechdel_time = conf.getItemData("configerinfor", "sechdel_time")
    everyRounder = sechdel_time.split("&")[0]
    localTime = sechdel_time.split("&")[1]
    print isreport,ismail
    return isreport,ismail,everyRounder,localTime
def getEamilData(isreport,successNum,faileNum,errorNum):
    conf = configerData.configerData()
    senderlist = conf.getItemData("configerinfor", "senderlist").split(",")
    senderList = []
    for i in senderlist:
        if (i != ""):
            senderList.append(i)
    print senderList
    subject = '定时接口运行报告'
    content = '接口运行详情见附件'
    mailsender = sendmail_exchange.MailSender()
    if isreport=="Y":
        sql = "select report_localName from main_reports where id=(select MAX(id) from main_reports )"
        reportname = mulSQL.mulSql().selectData(sql)
        print str(reportname[0])
        reportpath = os.path.dirname(os.path.dirname(__file__)) + "\\report\\"+ str(reportname[0])
    else:
        reportpath=""
    mailsender.sendMail(senderList, subject, content,True,
                        reportpath,successNum,faileNum,errorNum,'normal')
def runSchedule():
        schedule.every(3).minutes.do(runChart)
        isreport, ismail,everyRounder,localTime = getCofigerData()
        if everyRounder =="每天":
            schedule.every().day.at(localTime).do(runCase,ismail)
        elif everyRounder =="每周":
            schedule.every().monday.at(localTime).do(runCase)
        elif everyRounder =="每月":
            schedule.every(28).to(31).at(localTime).do(runCase)
if __name__ == '__main__':
    runSchedule()
    while True:
        flag = configerData.configerData().getItemData("scheduleChanged", "caseflag")
        print flag
        if flag == "true":
            for j in schedule.jobs:
                schedule.cancel_job(j)
            runSchedule()
            configerData.configerData().setData("scheduleChanged", "caseflag", "false")
            print schedule.jobs
        else:
            print schedule.jobs
        schedule.run_pending()











