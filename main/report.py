# -*- coding: utf-8 -*-
from django.shortcuts import render
from models import reports
from django.http.response import JsonResponse
import json


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
            json_dict["ownMoudle"] = i.ownMoudle
            json_dict["startTime"] = i.startTime.strftime('%Y-%m-%d %H:%M:%S')
            json_dict["endTime"] = i.endTime.strftime('%Y-%m-%d %H:%M:%S')
            json_dict["totalNum"] = i.totalNum
            json_dict["successNum"] = i.successNum
            json_dict["failNum"] = i.failNum
            json_dict["errorNum"] = i.errorNum
            json_dict["executor"] = i.executor
            json_dict["reportPath"] = i.reportName
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
        if ainfo:
            try:
                ainfo.delete()
                print("删除成功")
            except BaseException as e:
                result = {'code': -1, 'info': 'sql error' + str(e)}
                return JsonResponse(result)
            result = {'code': 0, 'info': 'delete success'}
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
            if ainfo:
                try:
                    ainfo.delete()
                    print("删除%d成功" % id)
                    slist.append(id)
                except BaseException as e:
                    flist.append(id)
                    print("删除%d失败:%s" % (id, str(e)))
            else:
                flist.append(id)
                print("删除%d失败:不存在" % id)
        infos = "delete success:" + str(len(slist)) + ",fail:" + str(len(flist))
        result = {'code': 0, 'info': infos}
    return JsonResponse(result)

def viewReport(request):
    a = request.GET["report"]
    print a   # \report\2019-09-20-16_09_01_result.html
    reportName = a.split("\\")[2]
    print reportName
    return render(request, reportName)
