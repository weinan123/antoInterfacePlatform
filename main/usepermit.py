# -*- coding: utf-8 -*-
from django.shortcuts import render
from models import apiInfoTable, interfaceList,users,department
from untils import configerData
import json,os
import re
import sys
reload(sys)
sys.setdefaultencoding('utf8')
from django.http.response import JsonResponse
def userpermit(request):
    return render(request, 'userpermit.html')
def getUserLevel(request):
    if request.method == 'GET':
        username = request.GET['username']
        depart_lever = users.objects.filter(username=username).values("depart_lever")
        depart_lever_value = depart_lever[0]["depart_lever"]
        resonseData = {
            "code":0,
            "user_level":depart_lever_value
        }
        return JsonResponse(resonseData, safe=False)


def getUserData(request):
    if request.method == 'GET':
        username = request.GET['username']
        depart_lever = users.objects.filter(username=username).values("depart_lever")
        depart_lever_value = depart_lever[0]["depart_lever"]
        if depart_lever_value==1:
            allusers = users.objects.all()
            json_list = []
            for i in allusers:
                json_dict = {}
                json_dict["id"] = i.id
                json_dict["username"] = i.username
                json_dict["department"] = i.department
                depart_name = department.objects.filter(depart_lever = depart_lever_value).values("depart_name")
                json_dict["depart_name"] = depart_name[0]["depart_name"]
                json_dict["group"] = i.group
                json_dict["batch_check"] = i.batch_check
                json_dict["batch_run"] = i.batch_run
                json_dict["batch_del"] = i.batch_del
                json_dict["configer_permit"] = i.configer_permit
                json_list.append(json_dict)
            resonseData = {
                'datas': json_list,
                'code': 0,
                'info': 'success'
            }
            return JsonResponse(resonseData, safe=False)
        elif depart_lever_value==2:
            pass
        elif depart_lever_value==3:
            pass




