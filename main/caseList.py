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
