# -*- coding: utf-8 -*-
from django.shortcuts import render
from models import reports
from django.http.response import JsonResponse


def batchReports(request):
    return render(request, "reports.html")

def getReportList(request):
    result = {}
    if request.method == 'GET':
        allList = reports.objects.all()
        json_list = []
        for i in allList:
            json_dict = {}
            json_dict["id"] = i.id
            json_dict["ownMoudle"] = i.ownMoudle
            json_dict["startTime"] = i.startTime
            json_dict["endTime"] = i.endTime.strftime('%Y-%m-%d %H:%M:%S')
            json_dict["totalNum"] = i.totalNum
            json_dict["successNum"] = i.successNum.strftime('%Y-%m-%d %H:%M:%S')
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