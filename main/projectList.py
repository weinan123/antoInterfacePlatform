# -*- coding: utf-8 -*-
from django.shortcuts import render, redirect
import json, time
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from main.models import *
from forms import UserForm, projectForm
from django.contrib import auth
from django.contrib.auth.models import User
from django import forms


def addProjectList(request):
    if request.method == 'POST':
        # 接受request.POST参数构造form类的实例
        form = projectForm(request.POST)
        # 验证数据是否合法
        if form.is_valid():
            # 处理form.cleaned_data中的数据
            # ...
            # 重定向到一个新的URL
            inter = interfaceList.objects.create(projectName=form.cleaned_data['projectName'],
                                                 moduleName=form.cleaned_data['moduleName'])
            inter.save()
            return HttpResponseRedirect('/projectList/')


def projectListInfo(request):
    resp = interfaceList.objects.values("id", "projectName", "moduleName", "updateTime")
    return JsonResponse(list(resp), safe=False)


def projectList(request):
    form = projectForm()
    return render(request, 'projectList.html', {'form': form})
