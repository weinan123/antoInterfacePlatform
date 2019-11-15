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
                print i["projectname"]
                allprojectcase = caseList.objects.filter(owningProject=i["projectname"]).values("id","caseName")
                print allprojectcase
                singleProject["runcaseId"] = i["runcaseId"]
                singleProject["runcaseinfor"] = []
                for s in allprojectcase:
                    for w in list(i["runcaseId"]):
                        if s["id"] == int(w):
                            cases = {
                                "id":w,
                                "casename":s[1],
                                "checkd":True
                            }
                        else:
                            cases = {
                                "id": w,
                                "casename": s[1],
                                "checkd": False
                            }
                        singleProject["runcaseinfor"].append(cases)
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
        return JsonResponse(responseData, safe=False)

