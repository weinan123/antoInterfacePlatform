# -*- coding: utf-8 -*-
from django.shortcuts import render
from models import apiInfoTable, projectList, moduleList
from untils import configerData
import json, os
import re
import sys

reload(sys)
sys.setdefaultencoding('utf8')
from django.http.response import JsonResponse


def configer(request):
    return render(request, 'configer.html')


def getAllcase(request):
    returndata = {
        "code": 0,
        "data": []
    }
    projectlist = []
    projectName = projectList.objects.filter().values("projectName").distinct()
    for s in projectName:
        projectlist.append(s["projectName"])
    returndata["projectList"] = projectlist
    '''

    caseinfor = projectList.objects.filter().values_list("projectName","moduleName")
    for i in caseinfor:
        if i[1]=="":
            continue
        cases = {
            "allcase":[]
        }
        cases["projectName"]=i[0]
        cases["moduleName"] = i[1]
        id = projectList.objects.filter(projectName=i[0], moduleName=i[1]).values("id")
        owningListID= id[0]["id"]
        allcase = apiInfoTable.objects.filter(owningListID=int(owningListID)).values("apiID","apiName")
        print id,allcase
        for s in allcase:
            caseinfor = {}
            caseinfor["caseName"] = (s["apiName"])
            caseinfor["caseId"] = s["apiID"]
            caseinfor["checked"] = False
            cases["allcase"].append(caseinfor)
        returndata["data"].append(cases)
    '''
    return JsonResponse(returndata, safe=False)


def getprojectCase(request):
    if request.method == 'GET':
        returndata = {
            "code": 0,
            "data": []
        }
        try:
            projectName = request.GET['initProjectName']
            owningListID = projectList.objects.filter(projectName=projectName).values("id")[0]['id']
            caseinfor = moduleList.objects.filter(owningListID=owningListID).values("id", "moduleName")
            # print caseinfor
            for i in caseinfor:
                cases = {
                    "allcase": []
                }
                cases["moduleName"] = i["moduleName"]
                # id = projectList.objects.filter(projectName=projectName, moduleName=i["moduleName"],).values("id")
                # owningListID = id[0]["id"]
                allcase = apiInfoTable.objects.filter(owningListID=int(i["id"])).values("apiID",
                                                                                        "apiName")
                # print id, allcase
                for s in allcase:
                    caseinfor = {}
                    caseinfor["caseName"] = (s["apiName"])
                    caseinfor["caseId"] = s["apiID"]
                    caseinfor["checked"] = False
                    cases["allcase"].append(caseinfor)
                returndata["data"].append(cases)
        except:
            returndata = {
                "msg": "请求数据为空",
                "code": 0,
                "data": []
            }

        return JsonResponse(returndata, safe=False)


def saveConfigData(request):
    if request.method == "POST":
        reqdata = json.loads(request.body)
        # print reqdata
        # print reqdata.items
        reqdata["senderList"] = ",".join(reqdata["senderList"])
        reqdata["runcase"] = list(set(reqdata["runcase"]))
        reqdata["runcase"] = ",".join(reqdata["runcase"])
        conf = configerData.configerData()
        try:
            conf.saveData("configerinfor", reqdata)
            #updateHost()
            data = {
                "code": 0,
                "msg": "保存成功"
            }
            configerData.configerData().setData("scheduleChanged", "caseflag", "true")
        except:
            data = {
                "code": -1,
                "msg": "保存失败"
            }

        return JsonResponse(data, safe=False)


# 更新host环境
'''
def updateHost():
    conf = configerData.configerData()
    evirment = conf.getItemData("configerinfor", "eviorment").lower()
    if (evirment == "live"):
        evirment = ""
    # print evirment
    allHost = apiInfoTable.objects.all().values_list("apiID", "host")
    for i in allHost:
        print i
        id = i[0]
        host = i[1]
        if host == None:
            continue
        else:
            match1 = re.search('qa', host)
            match2 = re.search('dev', host)
            match4 = re.search('.youyu', host)
            match3 = re.search('stage', host)
            # print match1,match2,match3,match4
            if (match1 != None):
                host = host.replace('qa', evirment)
                apiInfoTable.objects.filter(apiID=id).update(host=host)
                continue
            if (match2 != None):
                host = host.replace('dev', evirment)
                apiInfoTable.objects.filter(apiID=id).update(host=host)
                continue
            if (match3 != None):
                host = host.replace('stage', evirment)
                apiInfoTable.objects.filter(apiID=id).update(host=host)
                continue
            if (match4 != None):
                host = host.replace('.youyu', evirment + ".youyu")
                apiInfoTable.objects.filter(apiID=id).update(host=host)
                continue
                '''


def getConfiginitData(request):
    conf = configerData.configerData()
    confData = conf.getData("configerinfor")
    # print confData
    data = {}
    for i in confData:
        data[i[0]] = i[1]
    # print data
    return JsonResponse(data, safe=False)
