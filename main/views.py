# -*- coding: utf-8 -*-
from django.shortcuts import render, redirect
import json,time
from django.http import HttpResponse, HttpResponseRedirect,JsonResponse
from .models import *
from forms import UserForm
from django.contrib import auth
from django.contrib.auth.models import User
def index(request):
    return render(request,'index.html')
def login(request):
    username = request.COOKIES.get('username')
    print username
    if username is not None:
        return redirect('/',{'username':username})
    else:
        if request.method == 'POST':
            username = request.POST.get('username')
            password = request.POST.get('password')
            remember = request.POST.get('remember')
            print remember
            re = auth.authenticate(username = username,password=password)
            print re
            if re is not None:
                auth.login(request,re)
                response = redirect('/',{'username':username })
                request.session['username'] = username
                request.session['password'] = password
                response.set_cookie('username',username,3600)
                response.set_cookie('password', password, 3600)
                return redirect('/',{'username':username })
            else:
                return render(request,'login.html',{'login_error':'用户名或者密码错误'})
        return render(request,'login.html')

def logout(request):
    auth.logout(request)
    response = HttpResponse('/login/')
    response.delete_cookie('username')
    return render(request,"login.html")
def register(request):
    if request.method == 'POST':
        uf = UserForm(request.POST)
        if uf.is_valid():
            username = uf.cleaned_data['username']
            password = uf.cleaned_data['password']
            password2 = uf.cleaned_data['password2']
            print password,password2
            if password == password2:
                User.objects.create_user(username = username,password=password)
                re = auth.authenticate(username=username, password=password)
                auth.login(request, re)
                response = redirect('/', {'username': username})
                request.session['username'] = username
                response.set_cookie('username', username, 3600)
                return redirect('/', {'username': username})
                #return render(request,'index.html',{'username':username })
            else:
                return render(request, 'register.html', {'register_error': '两次输入密码不一致'})
    else:
        uf = UserForm()
    return render(request,'register.html',{'uf':uf })