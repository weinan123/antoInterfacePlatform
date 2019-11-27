# -*- coding: utf-8 -*-
from django.shortcuts import redirect
from toretrunData import toType
import getType1Cookies,getType2Cookies,getType3Cookies
import time,os,sched,subprocess
import json
def my_login(func):
    def inner(*args,**kwargs):
        login_user_id = args[0].session.get('username')
        print login_user_id
        if login_user_id is not None:
            return func(*args,**kwargs)
        else:
            return redirect('/login')
    return inner

def mul_bodyData(bodyinfor):
    body = {}
    files = {}
    if bodyinfor == "" or str(bodyinfor) == "{}" or bodyinfor is None:
        body = {}
        files = {}
        showflag = 0
    else:
        paramsData = bodyinfor["datas"]
        showflag = bodyinfor["showflag"]
        if bodyinfor["showflag"] == 3:
            if str(paramsData[0]["paramValue"]) != "" or str(paramsData[0]["paramValue"]) != "{}":
                body = json.loads(paramsData[0]["paramValue"])
            else:
                body = {}
        else:
            for i in range(0,len(paramsData)):
                params_name = paramsData[i]["paramName"]
                params_value = paramsData[i]["paramValue"]
                params_type = paramsData[i]["paramType"]
                if(params_type == 'file'):
                    path = r'main/postfiles/%s' % bodyinfor[i]["paramValue"]
                    if os.path.exists(path):
                        files = {'file':open(path, 'rb')}
                    else:
                        files = {'file':""}
                else:
                    getvalue = toType(params_type,params_value).toreturnType()
                    body[params_name] = getvalue
    return body, files, showflag


def getcookies(cookieFlag,evirment,username,password):
    cookies = {}
    if int(cookieFlag==1):
        cookies = getType1Cookies.getCookies1(evirment, username, password).servirce()
    elif int(cookieFlag==2):
        cookies = getType2Cookies.getCookies2(evirment, username, password).getcookies()
    elif int(cookieFlag==3):
        cookies = getType3Cookies.getCookies3(evirment, username, password).servirce(cookieFlag)
    elif int(cookieFlag==4):
        cookies = getType3Cookies.getCookies3(evirment, username, password).servirce(cookieFlag)
    return cookies




