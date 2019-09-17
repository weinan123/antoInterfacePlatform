# -*- coding: utf-8 -*-
from django.shortcuts import render
from models import apiInfoTable, interfaceList
import time
import json
from django.http.response import JsonResponse
import requests
import sys
def configer(request):
    return render(request, 'configer.html')
def getAllcase(request):
    returndata = {
        "code":0,
        "data":[]
    }
    projectList = []
    projectName = interfaceList.objects.filter().values("projectName").distinct()
    for s in projectName:
        projectList.append(s["projectName"])
    returndata["projectList"] =projectList
    caseinfor = interfaceList.objects.filter().values_list("projectName","moduleName")
    for i in caseinfor:
        cases = {
            "allcase":[]
        }
        cases["projectName"]=i[0]
        cases["moduleName"] = i[1]
        id = interfaceList.objects.filter(projectName=i[0], moduleName=i[1]).values("id")
        owningListID= id[0]["id"]
        allcase = apiInfoTable.objects.filter(owningListID=int(owningListID)).values("apiName")
        print id,allcase
        for s in allcase:
            cases["allcase"].append(s["apiName"])
        returndata["data"].append(cases)
    return JsonResponse(returndata, safe=False)

