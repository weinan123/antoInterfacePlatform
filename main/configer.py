# -*- coding: utf-8 -*-
from django.shortcuts import render
from models import apiInfoTable, interfaceList
import ConfigParser
import json,os
from django.http.response import JsonResponse
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
        allcase = apiInfoTable.objects.filter(owningListID=int(owningListID)).values("apiID","apiName")
        print id,allcase
        for s in allcase:
            caseinfor = {}
            caseinfor["caseName"] = (s["apiName"])
            caseinfor["caseId"] = s["apiID"]
            cases["allcase"].append(caseinfor)
        returndata["data"].append(cases)
    return JsonResponse(returndata, safe=False)
def saveConfigData(request):
    if request.method == "POST":
        reqdata = json.loads(request.body)
        print reqdata
        eviorment=reqdata["eviorment"]
        isReport=reqdata["isReport"]
        isMail=reqdata["isMail"]
        sendList=reqdata["sendList"]
        runcase=reqdata["runcase"]
        sechdel_time=reqdata["sechdel_time"]
        iniFileUrl = r"main/configerdatas/config_data"
        conf = ConfigParser.ConfigParser()
        try:
            conf.read(iniFileUrl)
            print(conf.sections())
            conf.set("configerinfor","eviorment",eviorment)
            conf.set("configerinfor", "isReport", isReport)
            conf.set("configerinfor", "isMail", isMail)
            conf.set("configerinfor", "sendList", sendList)
            conf.set("configerinfor", "runcase", runcase)
            conf.set("configerinfor", "sechdel_time", sechdel_time)
            conf.write(open(iniFileUrl, "w"))
            data = {
                "code":0,
                "msg":"保存成功"
            }
        except:
            data={
                "code": -1,
                "msg": "保存失败"
            }
        return JsonResponse(data, safe=False)








