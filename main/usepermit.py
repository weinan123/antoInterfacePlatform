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
        user_group = users.objects.filter(username=username).values("group")
        depart_lever_value = depart_lever[0]["depart_lever"]
        if depart_lever_value==1:
            allusers = users.objects.all()
            json_list = []
            for i in allusers:
                json_dict = {}
                json_dict["id"] = i.id
                json_dict["username"] = i.username
                json_dict["department"] = i.department
                depart_name = department.objects.filter(depart_lever = i.depart_lever).values("depart_name")
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
            json_list = []
            login_user = users.objects.get(username=username)
            json_dict = {}
            json_dict["id"] = login_user.id
            json_dict["username"] = login_user.username
            json_dict["department"] = login_user.department
            depart_name = department.objects.filter(depart_lever=login_user.depart_lever).values("depart_name")
            json_dict["depart_name"] = depart_name[0]["depart_name"]
            json_dict["group"] = login_user.group
            json_dict["batch_check"] = login_user.batch_check
            json_dict["batch_run"] = login_user.batch_run
            json_dict["batch_del"] = login_user.batch_del
            json_dict["configer_permit"] = login_user.configer_permit
            json_list.append(json_dict)
            allusers = users.objects.filter(group=user_group[0]["group"],depart_lever=3,).all()

            for i in allusers:
                json_dict = {}
                json_dict["id"] = i.id
                json_dict["username"] = i.username
                json_dict["department"] = i.department
                depart_name = department.objects.filter(depart_lever=i.depart_lever).values("depart_name")
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

        elif depart_lever_value==3:
            resonseData = {
                'datas': "login is user",
                'code': 0,
                'info': 'success'
            }
            return JsonResponse(resonseData, safe=False)
def delUserData(request):
    result = {}
    if request.method == 'POST':
        req = json.loads(request.body)["params"]
        id = req['id']
        print id
        userinfo = users.objects.get(id=id)
        if userinfo:
            try:
                userinfo.delete()
                print("删除成功")
            except BaseException as e:
                result = {'code': -1, 'info': 'sql error' + str(e)}
                return JsonResponse(result)
            result = {'code': 0, 'info': 'delete success'}
        else:
            result = {'code':-2,'info':'no exist'}
    return JsonResponse(result)





