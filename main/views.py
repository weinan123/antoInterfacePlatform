# -*- coding: utf-8 -*-
from django.shortcuts import render, redirect
import json
from django.http import HttpResponse, JsonResponse
import requests
from forms import UserForm
from django.contrib import auth
from django.contrib.auth.models import User

from .untils.until import my_login,mul_bodyData
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
    send_body = mul_bodyData(bodyinfor)
    if(methods=="GET"):
        response = requests.get(url,headers =headers,params=send_body,verify=False)
    elif(methods=="POST"):
        response = requests.post(url, headers=headers, data=json.dumps(send_body), verify=False)
    return_data = {
        "status_code": response.status_code,
        "result_content": response.text.decode("utf-8"),
        "times": str(response.elapsed.total_seconds())
    }
    return JsonResponse(return_data,safe=False)






