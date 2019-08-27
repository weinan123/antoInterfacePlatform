# -*- coding: utf-8 -*-
from django.shortcuts import render, redirect
import json,time
from django.http import HttpResponse, JsonResponse
import requests,urllib2
from forms import UserForm
from django.contrib import auth
from django.contrib.auth.models import User
from .models import *
from .untils.until import my_login,mul_bodyData
from common import authService
from django.core import serializers
@my_login
def index(request):
    if request.method == 'GET':
        return render(request,'index.html')
def login(request):
    username = request.COOKIES.get('username')
    print username
    if username is not None:
        returndata = {"status": "success", "message": "login success", "username": username}
        return JsonResponse(returndata, safe=False)
        #return redirect('/',{'username':username})
    else:
        if request.method == 'POST':
            data = json.loads(request.body)
            username = data["username"]
            password = data["password"]
            try:
                url = 'http://10.9.19.212:8888/accounts/ldapVerify/'
                data = {'username':username,'password':password}
                response = requests.post(url,data = data)
                print response.text
                if response.text == 'pass':
                    response = redirect('index/', {'username': username})
                    request.session['username'] = username
                    request.session['password'] = password
                    response.set_cookie('username', username, 3600)
                    response.set_cookie('password', password, 3600)
                    returndata = {"status": "success", "message": "login success", "username": username}
                    return JsonResponse(returndata, safe=False)
                    #return redirect('/', {'username': username})
                else:
                    re = auth.authenticate(username = username,password=password)
                    print re
                    if re is not None:
                        auth.login(request,re)
                        response = redirect('index/',{'username':username })
                        request.session['username'] = username
                        request.session['password'] = password
                        response.set_cookie('username',username,3600)
                        response.set_cookie('password', password, 3600)
                        returndata = {"status": "success", "message": "login success","username":username}
                        return JsonResponse(returndata,safe=False)
                        #return redirect('/',{'username':username })
                    else:
                        returndata = {"status": "fail", "message": "用户名或者密码错误"}
                        return JsonResponse(returndata,safe=False)
                        #return render(request,'login.html',{'login_error':'用户名或者密码错误'})
            except:
                print Exception
        return render(request,'login.html')
        #return redirect('/', {'username': username})
def logout(request):
    auth.logout(request)
    response = HttpResponse('/login/')
    response.delete_cookie('username')
    return render(request, "login.html")
def register(request):
    if request.method == 'POST':
        uf = UserForm(request.POST)
        if uf.is_valid():
            username = uf.cleaned_data['username']
            password = uf.cleaned_data['password']
            password2 = uf.cleaned_data['password2']
            print password, password2
            if password == password2:
                User.objects.create_user(username=username, password=password)
                re = auth.authenticate(username=username, password=password)
                auth.login(request, re)
                response = redirect('/', {'username': username})
                request.session['username'] = username
                response.set_cookie('username', username, 3600)
                return redirect('/', {'username': username})
                # return render(request,'index.html',{'username':username })
            else:
                return render(request, 'register.html', {'register_error': '两次输入密码不一致'})
    else:
        uf = UserForm()
    return render(request, 'register.html', {'uf': uf})
def singleInterface(request):
    return render(request, 'singleInterface.html')
def sendRequest(request):
    data = json.loads(request.body)
    methods = data["methods"]
    url = data["url"]
    headers = data["headers"]
    bodyinfor = data["bodyinfor"]
    #处理数据类型的方法
    #send_body = mul_bodyData(bodyinfor)
    body = json.dumps(bodyinfor).decode('unicode-escape')
    print type(body)
    key_id = "b062f9721f2ed17596eaf599b6899f64"
    secret_key = "dc5a277173ef42f63de1e9c1134d4f7b"
    timestamp = int(time.time())
    credentials = authService.BceCredentials(key_id, secret_key)
    headersOpt = {'X-Requested-With', 'User-Agent', 'Accept'}
    headers['X-encryptflag'] = '1'
    path = "/api/v1/trade/business/query/funddetail"
    result = authService.simplify_sign(credentials, methods, path, headers, timestamp, 300, headersOpt)
    print result
    headers['Authorization'] = result
    if headers.get('X-encryptflag') == '1' and body:
        print 'body before encrypted: '
        print body
        body = authService.aes_encrypt(body)
    if(methods=="GET"):
        response = requests.get(url,headers =headers,params=body,verify=False)
    elif(methods=="POST"):
        response = requests.post(url, headers=headers, data=body, verify=False)
        resp = response.text
        if headers.get('X-encryptflag') != '1':
            print 'response: '
        else:
            print 'response before decrypt: '
            print resp
            resp = authService.aes_decrypt(resp)
            print('response: ')
        try:
            respDict = json.loads(resp)
            print(json.dumps(respDict, ensure_ascii=False, sort_keys=True, indent=4))
        except:
            print(resp)
    return JsonResponse(respDict,safe=False)
def getProjectList(request):
    project_list = interfaceList.objects.filter().values("projectName").distinct()
    model_list = interfaceList.objects.filter().values("projectName","moduleName").distinct()
    print project_list,model_list
    returnData = {
        "project_list":[],
        "model_list":[]
    }
    for i in range(0,len(project_list)):
        returnData["project_list"].append(project_list[i])
    for j in range(0,len(model_list)):
        returnData["model_list"].append(model_list[j])
    print returnData
    return JsonResponse(returnData,safe=False)
def newCase(request):
    if request.method=="POST":
        reqdata = json.loads(request.body)["params"]
        data = reqdata["data_to_send"]
        methods = data["methods"]
        url = data["url"]
        headers = json.dumps(data["headers"])
        bodyinfor = data["bodyinfor"]
        projectName = data["projectName"]
        moduleName = data["moduleName"]
        caseName = data["caseName"]
        creator = request.session.get('username')
        print creator
        send_body = mul_bodyData(bodyinfor)
        send_body = json.dumps(send_body)
        flag = reqdata["flag"]
        if(flag == False):
            try:
                id = interfaceList.objects.filter(projectName=projectName,moduleName=moduleName).values("id")
                owningListID = id[0]["id"]
                print owningListID
                apiInfoTable.objects.get_or_create(method=methods,headers = headers,url =url,body=send_body,
                                                   apiName=caseName,owningListID_id=int(owningListID),creator=creator)
                data = {
                    "code":0,
                    "msg":"保存成功"
                }
            except Exception as e:
                    data={
                        "code":-1,
                        "msg": "保存失败"
                    }
        else:
            try:
                id = int(data["apiid"])
                pid = apiInfoTable.objects.get(apiID=id).owningListID_id
                print("pid:", pid)
                apiInfoTable.objects.filter(apiID=id).update(apiName=caseName, method=methods, url=url, headers=headers,
                                                             body=send_body)
                interfaceList.objects.filter(id=pid).update(projectName=projectName, moduleName=moduleName)
            except Exception as e:
                data = {
                    "code": -1,
                    "msg": "更新失败"
                }
                return JsonResponse(data)
            data = {
                "code": 0,
                "msg": "更新成功"
            }
        return JsonResponse(data,safe=False)
def returnAuthorization(request):
    if request.method=="POST":
        data = json.loads(request.body)
        secret_key = data["secret_key"].encode("utf-8")
        key_id = data["key_id"]
        http_method = data["methods"]
        path = data["url"]
        #headers = data["headers"]
        timestamp = int(time.time())
        credentials = authService.BceCredentials(key_id, secret_key)
        headers = {
            'Accept': 'text/html, */*; q=0.01',
            'X-Requested-With': 'XMLHttpRequest',
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2272.89 Safari/537.36'
        }
        headersOpt = {'X-Requested-With', 'User-Agent', 'Accept'}
        result = authService.simplify_sign(credentials, http_method, path, headers, timestamp, 300, headersOpt)
        print result
        returnData = {
            "code":0,
            "data":result
        }
        return result
        #return JsonResponse(returnData,safe=False)










