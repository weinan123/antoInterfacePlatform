# -*- coding: utf-8 -*-
from django.shortcuts import render, redirect
import json, time
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from main.models import *
from forms import UserForm, projectForm
from django.contrib import auth
from django.contrib.auth.models import User
from django import forms
import re


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
                                                 moduleName=form.cleaned_data['moduleName'],
                                                 host=form.cleaned_data['host'])

            counttable = countCase.objects.create(projectName=form.cleaned_data['projectName'],
                                                  moduleName=form.cleaned_data['moduleName'], )
            counttable.save()
            inter.save()
            return HttpResponseRedirect('/projectList/')


def projectListInfo(request):
    resp = interfaceList.objects.values("id", "projectName", "host", "moduleName", "updateTime", "createTime")
    respList = list(resp)
    for i in range(len(respList)):
        respList[i]['updateTime'] = str(respList[i]['updateTime']).split('.')[0]
    for i in range(len(respList)):
        respList[i]['createTime'] = str(respList[i]['createTime']).split('.')[0]
    result = {
        'data': respList,
        'code': 0,
        'info': 'success'
    }
    return JsonResponse(result, safe=False)


def projectList(request):
    # form = projectForm()
    # return render(request, 'projectList.html', {'form': form})
    return render(request, 'projectList.html')


def projectView(request):
    if request.method == 'GET':
        id = request.GET.get('id')
        print id
    return HttpResponseRedirect('/projectList/')


def projectDelete(request):
    if request.method == 'GET':
        id = request.GET.get('id')
        if (apiInfoTable.objects.filter(owningListID=id).count() == 0):
            interfaceList.objects.filter(id=id).delete()
        else:
            error = '项目中还存在用例，请先删除用例，再删除项目！'
    return HttpResponseRedirect('/projectList/')


def projectBatchDelete(request):
    result = {}
    if request.method == 'POST':
        req = json.loads(request.body)["params"]
        idDelete = req['idDelete']
        for x in idDelete:
            if (apiInfoTable.objects.filter(owningListID=x[0]).count() == 0):
                interfaceList.objects.filter(id=x[0]).delete()
            else:
                error = '项目中还存在用例，请先删除用例，再删除项目！'
    return JsonResponse(result)


def projectEdit(request):
    if request.method == 'POST':
        id = request.POST.get('id')
        projectName = request.POST.get('projectName')
        moduleName = request.POST.get('moduleName')
        host = request.POST.get('host')
        edit = interfaceList.objects.get(id=id)
        edit.projectName = projectName
        edit.moduleName = moduleName
        edit.host = host
        edit.save()
        return HttpResponseRedirect('/projectList/')


def projectSort(request):
    if request.method == 'GET':
        id = request.GET.get('id')
        interfaceList.objects.filter(id=id).delete()
    return HttpResponseRedirect('/projectList/')


def projectImport(request):
    Flag = Flag2 = True
    if request.method == 'POST':
        f = request.FILES['file']
        for line in f.readlines():  # 依次读取每行
            line = line.strip()  # 去掉每行头尾空白
            if not len(line) or line.startswith('#'):  # 判断是否是空行或注释行
                continue  # 跳过
            matchObj = re.match(r'(GET|POST) (https|http)://(.*?)/(.*) ', line, re.M | re.I)
            if matchObj:
                if (Flag):
                    Flag = False
                    method = matchObj.group(1)
                    protocol = matchObj.group(2)
                    host = matchObj.group(2) + r'://' + matchObj.group(3)
                    url = r'/' + matchObj.group(4)
                    print "method : ", method
                    print "protocol : ", protocol
                    print "host : ", host
                    print "url : ", url
            matchObj2 = re.match(r'Content-Type: (.*?);(.*)', line, re.M | re.I)
            if matchObj2:
                if (Flag2):
                    Flag2 = False
                    header = '{"Content-Type": "' + matchObj2.group(1) + '"}'  # {"Content-Type": "application/json"}
                    print "header : ", header
            matchObj3 = re.finditer(r'".+?":".+?"', line, re.M | re.I)
            if matchObj3:
                for match in matchObj3:
                    print (match.group())
                    json = re.finditer(r'".+?"', match.group())
                    for jsonMatch in json:
                        print jsonMatch.group()

        # with open('main/upload/file.txt', 'wb+') as destination:
        #     for chunk in f.chunks():
        #         destination.write(chunk)
    return HttpResponseRedirect('/projectList/')
