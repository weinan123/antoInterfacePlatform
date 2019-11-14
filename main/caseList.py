# -*- coding: utf-8 -*-
from django.shortcuts import render, redirect
import json, time
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse, FileResponse
from main.models import *
from forms import *
from untils import until
from common.batchUntils import checkFormat


def addCase(request):
    result = {
        'code': -1,
        'info': '未知错误！'
    }
    if request.method == 'POST':
        # 接受request.POST参数构造form类的实例
        form = caseForm(request.POST)
        # 验证数据是否合法
        if form.is_valid():
            # 处理form.cleaned_data中的数据
            # ...
            # 重定向到一个新的URL
            # if ():
            #     return
            dtime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
            user = request.session.get('username')
            if (caseList.objects.filter(owningProject=form.cleaned_data['owningProject'],
                                        caseName=form.cleaned_data['caseName']).count() == 0):
                inter = moduleList.objects.create(owningListID=form.cleaned_data['owningProject'],
                                                  caseName=form.cleaned_data['caseName'],
                                                  includeAPI=form.cleaned_data['includeAPI'],
                                                  creator=user)
                inter.save()
                moduleList.objects.filter(owningProject=form.cleaned_data['owningProject'],
                                          caseName=form.cleaned_data['caseName']).update(
                    updateTime=dtime,
                    createTime=dtime)
                code = 0
                info = '新建成功！'
                result = {
                    'code': code,
                    'info': info
                }
            else:
                code = -2
                info = '同一项目下不可包含相同名称的用例！'
                result = {
                    'code': code,
                    'info': info
                }
        else:
            result = {
                'code': -1,
                'info': '数据格式不正确！'
            }

    return JsonResponse(result, safe=False)


def caseInfo(request):
    result = {
        'code': -1,
        'info': '调用的方法错误，请使用GET方法查询！'
    }
    if request.method == 'GET':
        projectName = request.GET.get('projectName')
        resp = caseList.objects.filter(owningProject=projectName).values("id", "caseName", "includeAPI",
                                                                         "creator", "executor",
                                                                         "updateTime", "createTime",
                                                                         "runResult", "lastRunTime")
        respList = list(resp)
        for i in range(len(respList)):
            respList[i]['projectName'] = projectName
            respList[i]['updateTime'] = str(respList[i]['updateTime']).split('.')[0]
            respList[i]['createTime'] = str(respList[i]['createTime']).split('.')[0]
            count=0
            for x in list(respList[i]['includeAPI']):
                respList[i]['includeAPI'] = x[0]
                count = count + 1
            if (respList[i]['executor'] is None) or (respList[i]['executor'] == ''):
                respList[i]['executor'] = '暂未执行'
            if (respList[i]['runResult'] is None) or (respList[i]['runResult'] == ''):
                respList[i]['runResult'] = '暂未执行'
            if (respList[i]['lastRunTime'] is None) or (respList[i]['lastRunTime'] == ''):
                respList[i]['lastRunTime'] = '暂未执行'
        result = {
            'data': respList,
            'code': 0,
            'info': 'success'
        }
        return JsonResponse(result, safe=False)
