# -*- coding: utf-8 -*-
from django.shortcuts import render
from models import reports
from django.http.response import JsonResponse
import json, os


def batchReports(request):
    return render(request, "reports.html")

def getReportList(request):
    result = {}
    if request.method == 'GET':
        allList = reports.objects.all().order_by("-startTime")
        json_list = []
        for i in allList:
            json_dict = {}
            json_dict["id"] = i.id
            json_dict["report_runName"] = i.report_runName
            json_dict["startTime"] = i.startTime.strftime('%Y-%m-%d %H:%M:%S')
            json_dict["endTime"] = i.endTime.strftime('%Y-%m-%d %H:%M:%S')
            json_dict["totalNum"] = i.totalNum
            json_dict["successNum"] = i.successNum
            json_dict["failNum"] = i.failNum
            json_dict["errorNum"] = i.errorNum
            json_dict["executor"] = i.executor
            json_dict["report_localName"] = i.report_localName
            json_list.append(json_dict)
        result = {
            'datas': json_list,
            'code': 0,
            'info': 'success'
        }
    return JsonResponse(result)

def reportDelete(request):
    result = {}
    if request.method == 'POST':
        req = json.loads(request.body)["params"]
        id = req['id']
        ainfo = reports.objects.get(id=id)
        reName = ainfo.report_localName
        if ainfo:
            try:
                # ainfo.delete()
                print("delete success from sql.")
            except BaseException as e:
                result = {'code': -1, 'info': 'delete error' + str(e)}
                return JsonResponse(result)
            a = delReport(reName)
            if a == 0:
                result = {'code': 0, 'info': 'delete success'}
            else:
                result = {'code': 1, 'info': 'delete sql success,delete local failed.'}
        else:
            result = {'code': -2, 'info': 'no exist'}
    return JsonResponse(result)

def reportbatchDelete(request):
    result = {}
    if request.method == 'POST':
        req = json.loads(request.body)["params"]
        idlist = req['idList']
        print idlist
        slist = []
        flist = []
        for id in idlist:
            ainfo = reports.objects.get(id=id)
            reName = ainfo.report_localName
            if ainfo:
                try:
                    ainfo.delete()
                    a = delReport(reName)
                    if a == 0:
                        print("delete %d success" % id)
                    else:
                        print("delete %d success from sql but delete failed from local." % id)
                    slist.append(id)
                except BaseException as e:
                    flist.append(id)
                    print("delete %d failed :%s" % (id, str(e)))
            else:
                flist.append(id)
                print("删除%d失败:不存在" % id)
        infos = "delete success:" + str(len(slist)) + ",fail:" + str(len(flist))
        result = {'code': 0, 'info': infos}
    return JsonResponse(result)

def delReport(rename):
    path = os.path.abspath(os.path.dirname(os.path.dirname(__file__))) + "\\main\\report\\"
    print path
    files = os.listdir(path)
    print files
    print "------------"
    report_name = rename
    print report_name
    print "--------------"
    res = 0
    for file in files:
        print file
        if str(file) == str(report_name):
            os.remove(path + file)
            print(file + " deleted")
            res = 0
            break
        else:
            print(file + "!=" + report_name + " not delete")
            res = -1
    return res

def viewReport(request):
    a = request.GET["report"]
    print a   # \report\2019-09-20-16_09_01_result.html
    reportName = a
    print reportName
    return render(request, reportName)
