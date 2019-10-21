# -*- coding: UTF-8 -*-
import os,django
import runChartData,sendmail_exchange
import mulSQL,time
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "auto_interface.settings")
django.setup()
import schedule,subprocess,batchstart
from main.untils import configerData
'''
定时批量执行用例
'''
def runCase(ismail):
    conf = configerData.configerData()
    runcase = conf.getItemData("configerinfor","runcase").split(",")
    scheduleList = []
    for i in runcase:
        if(i!=""):
            scheduleList.append(int(i))
    print scheduleList
    reportName = u"定时报告" + "_" + time.strftime('%Y-%m-%d-%H-%M-%S', time.localtime(time.time()))
    totalNum = len(scheduleList)
    starttime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    isreport = conf.getItemData("configerinfor", "isreport")
    batchResult = batchstart.start_main(scheduleList,isreport)
    successNum = batchResult["sNum"]
    faileNum = batchResult["fNum"]
    errorNum = batchResult["eNum"]
    reportPath = "\\"+batchResult["reportPath"]
    exeuser = ""
    endtime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    print reportName,starttime,endtime,totalNum,successNum,faileNum,errorNum,exeuser,reportPath
    sql = "insert into main_reports(report_runName,startTime,endTime,totalNum,successNum,failNum,errorNum,executor,report_localName)" \
          "values ('%s','%s','%s','%s','%s','%s','%s','%s','%s')"%(reportName,starttime,endtime,totalNum,successNum,faileNum,errorNum,exeuser,reportPath)
    mulSQL.mulSql().insertData(sql)
    if(ismail=="Y"):
        getEamilData()
'''
图表数据定时更新
'''
def runChart():
    sqlList = [
        {"casetype":"allcase",
         "sql":"select count(*),owningListID from main_apiInfoTable group by owningListID"},
        {"casetype": "passcase",
         "sql": "select count(*),owningListID,lastRunResult from main_apiInfoTable where lastRunResult=1 group by owningListID " },
        {"casetype": "failcase",
         "sql": "select count(*),owningListID,lastRunResult from main_apiInfoTable where lastRunResult=-1 group by owningListID "},
        {"casetype": "nullcase",
         "sql": "select count(*),owningListID,lastRunResult from main_apiInfoTable where lastRunResult=0 group by owningListID "}
    ]
    getChartData = runChartData.getChartData()
    for i in range(0,len(sqlList)):
        casetype=sqlList[i]["casetype"]
        sql = sqlList[i]["sql"]
        getChartData.runDb(casetype,sql)
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
def getEamilData():
    conf = configerData.configerData()
    senderlist = conf.getItemData("configerinfor", "senderlist").split(",")
    senderList = []
    for i in senderlist:
        if (i != ""):
            senderList.append(i)
    subject = '定时接口运行报告'
    content = '接口运行详情见附件'
    mailsender = sendmail_exchange.MailSender()
    sql = "select report_localName from main_reports where id=(select MAX(id) from main_reports )"
    reportname = mulSQL.mulSql().selectData(sql)
    print str(reportname[0])
    reportpath = os.path.dirname(os.path.dirname(__file__)) + "\\report\\"+ str(reportname[0])
    mailsender.sendMail(senderList, subject, content,True,
                        reportpath, 'normal')
if __name__ == '__main__':
    schedule.every(5).minutes.do(runChart)
    isreport, ismail,everyRounder,localTime = getCofigerData()
    if everyRounder =="每天":
        schedule.every().day.at(localTime).do(runCase,ismail)
    elif everyRounder =="每周":
        schedule.every().monday.at(localTime).do(runCase)
    elif everyRounder =="每月":
        schedule.every(28).to(31).at(localTime).do(runCase)
    while True:
        schedule.run_pending()




