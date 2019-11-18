# -*- coding: utf-8 -*-
from django.shortcuts import render
from models import *
from django.http.response import JsonResponse
import json, os


def projectconfiger(request):
    return render(request, "projectConfiger.html")
def getScheduleinitData(request):
    if request.method == 'GET':
        responseData = {
            "code":0,
            "data":[],
            "msg":""
        }
        try:
            allcase = schedule.objects.filter().values()
            print allcase
            for i in allcase:
                singleProject = {
                }
                singleProject["projectname"] = i["projectname"]
                allprojectcase = caseList.objects.filter(owningProject=i["projectname"]).values("id","caseName")
                singleProject["runcaseinfor"] = []
                allcaselist = []
                print len(allprojectcase)
                if len(allprojectcase) > 0:
                    for s in allprojectcase:
                            cases = {
                                "id":int(s["id"]),
                                "casename":s["caseName"],
                                "checked":False
                            }
                            allcaselist.append(cases)
                    print allcaselist
                    ss = (i["runcaseId"]).encode('unicode-escape').decode('string_escape')
                    checklist = ss.split(",")
                    print checklist
                    for w in checklist:
                        for s in allcaselist:
                            if int(w)==s["id"]:
                                s["checked"]=True
                    singleProject["runcaseinfor"] = allcaselist
                    singleProject["evirment"] = i["evirment"]
                    singleProject["reporter"] = i["reporter"]
                    singleProject["timeDay"] = i["timeDay"]
                    singleProject["timeTime"] = i["timeTime"]
                    responseData["data"].append(singleProject)
                else:
                    singleProject["runcaseinfor"] = allcaselist
                    singleProject["evirment"] = i["evirment"]
                    singleProject["reporter"] = i["reporter"]
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

