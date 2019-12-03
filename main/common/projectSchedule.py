# -*- coding: UTF-8 -*-
import sys,os,django
from main.untils import configerData
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "auto_interface.settings")
django.setup()
from main.models import projectschedule,caseList,reports
from multiprocessing import Process
import batchstart,time,json
import sendmail_exchange
import schedule,subprocess,batchstart
reload(sys)
class runProSchdeule():
    def __init__(self):
        pass
    def getProinfor(self):
        projectschList = []
        allcase = projectschedule.objects.values()
        for i in allcase:
            if i["runcaseId"] != "" and i["runcaseId"] != None:
               batchrun_list = []
               runcaselist =  i["runcaseId"].split(",")
               projectname = i["projectname"]
               evirment = i["evirment"].encode('unicode-escape').decode('string_escape')
               print  i["reporter"]
               if i["reporter"] == "" or i["reporter"] == None:
                   reporter=[]
               else:
                    reporter  =i["reporter"].split(",")
               cookies = i["cookies"].encode('unicode-escape').decode('string_escape')
               timeDay = i["timeDay"]
               timeTime = i["timeTime"]
               for j in runcaselist:
                   runcaseinfor = caseList.objects.filter(id=int(j)).values("caseName","includeAPI")
                   if runcaseinfor[0]["includeAPI"]==""or i["reporter"] == None:
                       list = []
                   else:
                       list = map(int, runcaseinfor[0]["includeAPI"].split(","))
                   print str(runcaseinfor[0]["caseName"])
                   batchrunJson = {
                       "sname": str(runcaseinfor[0]["caseName"]),
                       "list": list,
                       "cookices":json.loads(cookies)
                   }
                   batchrun_list.append(batchrunJson)
                   print batchrun_list
                   projectschinfor = {
                       "projectname": projectname,
                       "scheduleinfor": batchrun_list,
                       "reporter":reporter,
                       "evirment":evirment,
                       "timeDay":timeDay,
                       "timeTime":timeTime
                   }
                   projectschList.append(projectschinfor)
        return projectschList
    def getEamilData(self,senderlist,report_runName,reportpath, successNum, faileNum, errorNum):
        senderList = []
        for i in senderlist:
            if (i != ""):
                senderList.append(i)
        print senderList
        subject = report_runName
        content = '测试详情见附件'
        mailsender = sendmail_exchange.MailSender()
        reportpath = os.path.dirname(os.path.dirname(__file__)) + "\\report\\" + str(reportpath)
        print reportpath
        mailsender.sendMail(senderList, subject, content, True,
                            reportpath, successNum, faileNum, errorNum, 'normal')
    def runcase(self,batchrun_list,evirment,projectname,reporter):
        batchResult = batchstart.start_main(batchrun_list, evirment, "Y", "")
        report_localName = batchResult["reportPath"]
        report_runName = projectname + "定时业务场景回测报告"
        successNum = batchResult["sNum"]
        failNum = batchResult["fNum"]
        errorNum = batchResult["eNum"]
        totalNum = successNum + failNum + errorNum
        endtime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        reportpath = batchResult["reportPath"]
        print reportpath
        result_infos = {
            "report_runName": report_runName,
            "environment": evirment,
            "startTime": time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())),
            "endTime": endtime,
            "totalNum": totalNum,
            "successNum": successNum,
            "failNum": failNum,
            "errorNum": errorNum,
            "executor": "",
            "report_localName": report_localName,
        }
        try:
            s = reports.objects.create(**result_infos)
            s.save()
            faileNum = failNum
            errorNum = errorNum
            senderlist = reporter
            self.getEamilData(senderlist,report_runName,reportpath, successNum, faileNum, errorNum)
        except BaseException as e:
            print(" SQL Error: %s" % e)
    def runschedule(self,):
        ddd = self.getProinfor()
        for i in ddd:
            batchrun_list = i["scheduleinfor"]
            projectname = i["projectname"]
            evirment = i["evirment"]
            reporter = i["reporter"]
            everyRounder = i["timeDay"]
            localTime = str(i["timeTime"])
            print reporter
            if everyRounder == "每天":
                schedule.every().day.at(localTime).do(self.runcase, batchrun_list, evirment, projectname, reporter)
            elif everyRounder == "每周":
                schedule.every().monday.at(localTime).do(self.runcase, batchrun_list, evirment, projectname, reporter)
            elif everyRounder == "每月":
                schedule.every(28).to(31).at(localTime).do(self.runcase, batchrun_list, evirment, projectname,
                                                             reporter)
if __name__ == '__main__':
    runcase = runProSchdeule()
    runcase.runschedule()
    while True:
        flag = configerData.configerData().getItemData("scheduleChanged", "projectflag")
        print flag
        if flag == "true":
            for j in schedule.jobs:
                schedule.cancel_job(j)
            runcase.runschedule()
            configerData.configerData().setData("scheduleChanged", "projectflag", "false")
            print schedule.jobs
        else:
            print schedule.jobs
        schedule.run_pending()









