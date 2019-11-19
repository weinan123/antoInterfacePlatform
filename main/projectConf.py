# -*- coding: utf-8 -*-
from django.shortcuts import render
from models import *
from django.http.response import JsonResponse
import json, os


def projectconfiger(request):
    return render(request, "projectConfiger.html")
def saveProConf(request):
    if request.method == "POST":
        data = json.loads(request.body)
        id = (data["datas"]["id"])
        evirment = data["datas"]["evirment"]
        reporter = data["datas"]["reporter"]
        cookies = data["datas"]["cookies"]
        runcaselist = data["datas"]["runcaseid"]
        runcaseid = ",".join(runcaselist)
        timeDay = data["datas"]["timeDay"]
        timeTime = data["datas"]["timeTime"]
        try:
            schedule.objects.filter(id=id).update(evirment=evirment,reporter=reporter,cookies=cookies,runcaseId=runcaseid,
                                              timeDay=timeDay,timeTime=timeTime)
            responseData = {
                "code": 0,
                "data": [],
                "msg": "保存成功"
            }
        except Exception as e:
            responseData = {
                "code": -1,
                "data": [],
                "msg": e
            }
        return JsonResponse(responseData, safe=False)
def getScheduleinitData(request):
    if request.method == 'GET':
        responseData = {
            "code":0,
            "data":[],
            "msg":""
        }
        try:
            allcase = schedule.objects.filter().values()
            for i in allcase:
                singleProject = {
                }
                singleProject["projectname"] = i["projectname"]
                allprojectcase = caseList.objects.filter(owningProject=i["projectname"]).values("id","caseName")
                singleProject["runcaseinfor"] = []
                allcaselist = []
                if len(allprojectcase) > 0:
                    for s in allprojectcase:
                            cases = {
                                "id":int(s["id"]),
                                "casename":s["caseName"],
                                "checkif":False
                            }
                            allcaselist.append(cases)

                    ss = (i["runcaseId"]).encode('unicode-escape').decode('string_escape')
                    if ss=="":
                        checklist = []
                    else:
                        checklist = ss.split(",")

                    for w in checklist:
                        for s in allcaselist:
                            if int(w)==s["id"]:
                                s["checkif"]=True
                    singleProject["runcaseid"] = checklist
                    singleProject["runcaseinfor"] = allcaselist
                    singleProject["id"] = i["id"]
                    singleProject["evirment"] = i["evirment"]
                    singleProject["reporter"] = i["reporter"]
                    singleProject["cookies"] = i["cookies"]
                    singleProject["timeDay"] = i["timeDay"]
                    singleProject["timeTime"] = i["timeTime"]
                    responseData["data"].append(singleProject)
                else:
                    singleProject["id"] = i["id"]
                    singleProject["runcaseinfor"] = allcaselist
                    singleProject["evirment"] = i["evirment"]
                    singleProject["reporter"] = i["reporter"]
                    singleProject["cookies"] = i["cookies"]
                    singleProject["timeDay"] = i["timeDay"]
                    singleProject["timeTime"] = i["timeTime"]
                    responseData["data"].append(singleProject)
        except Exception as e:
            responseData = {
                "code": -1,
                "data": [],
                "msg": e
            }
        print responseData
        return JsonResponse(responseData, safe=False)




