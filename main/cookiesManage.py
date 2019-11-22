# -*- coding: utf-8 -*-
from django.shortcuts import render
from models import *
from untils import getType1Cookies,getType2Cookies,until
import json, time
import re
import jpype
import sys
reload(sys)
sys.setdefaultencoding('utf8')
from django.http.response import JsonResponse
def getCookies(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        id = data["id"]
        username = data["username"]
        index = data["index"]
        password = data["password"]
        cookiename = data["cookiename"]
        evirment = data["evirment"]
        projectname = data["projectname"]
        starttime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        cookieFlag = projectList.objects.filter(projectName=projectname).values("cookieFlag")[0]["cookieFlag"]
        print cookieFlag,id
        try:
            cookiedata = until.getcookies(cookieFlag, evirment, username, password)
            if cookiedata["code"]==0:
                cookies=cookiedata["cookies"]
            else:
                response = {
                    "code": -1,
                    "msg": cookiedata["msg"],
                    "error": cookiedata["error_msg"]
                }
                return JsonResponse(response, safe=False)
        except Exception as e:
            response = {
                "code":-1,
                "msg":"获取cookie失败",
                "error":str(e),
            }
            return JsonResponse(response, safe=False)
        cookies = json.dumps(cookies)
        if id == "":
            userCookies.objects.create(user=request.session['username'],username=username,password=password,
                                       projectname=projectname,cookiename=cookiename,
                                       evirment=evirment,cookies=cookies,iseffect=1,createTime=starttime)
            response = {
                "code": 0,
                "msg": "获取cookie成功",
                "cookies": cookies,
                "evirment": evirment,
                "index": index
            }
        else:
            userCookies.objects.filter(id=int(id)).update(user=request.session['username'], username=username,
                                              password=password,
                                              projectname=projectname, cookiename=cookiename,
                                              evirment=evirment, cookies=cookies, iseffect=1, updateTime=starttime)
            response = {
                "code": 0,
                "msg": "获取cookie成功",
                "cookies": cookies,
                "evirment": evirment,
                "index": index
            }

        return JsonResponse(response, safe=False)
def getCookieList(request):
    if request.method == 'GET':
        projectname = request.GET["projectname"]
        cookieList = userCookies.objects.filter(user=request.session['username'],projectname=projectname).values()
        qaList = []
        stageList = []
        liveList = []
        for i in cookieList:
            evirment = i["evirment"]
            if evirment=="qa":
                data = {
                    "id":i["id"],
                    "cookiename":i["cookiename"],
                     "username":i["username"],
                    "password":i["password"],
                    "cookies":i["cookies"],
                    "iseffect":i["iseffect"],
                }
                qaList.append(data)
            elif evirment=="stage":
                data = {
                    "id": i["id"],
                    "cookiename": i["cookiename"],
                    "username": i["username"],
                    "password": i["password"],
                    "cookies": i["cookies"],
                    "iseffect": i["iseffect"],
                }
                stageList.append(data)
            elif evirment=="live":
                data = {
                    "id": i["id"],
                    "cookiename": i["cookiename"],
                    "username": i["username"],
                    "password": i["password"],
                    "cookies": i["cookies"],
                    "iseffect": i["iseffect"],
                }
                liveList.append(data)
        response = {
            "code":0,
            "data":{"qa":qaList,"stage":stageList,"live":liveList}
        }
        return JsonResponse(response, safe=False)

def delCookies(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        id = data["id"]
        try:
            userCookies.objects.filter(id=int(id)).delete()
            response = {
                "code": 0,
                "msg": "删除成功",
            }
        except:
            response = {
                "code": -1,
                "msg": "删除失败",
            }
        return JsonResponse(response, safe=False)













