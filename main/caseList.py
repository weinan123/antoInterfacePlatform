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
        dtime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        user = request.session.get('username')
        req = json.loads(request.body)["params"]
        selectAPI = req['selectAPI']
        owningProject = req['owningProject']
        caseName = req['caseName']
        api = str(selectAPI[0][0])
        if (len(selectAPI) > 1):
            for x in range(len(selectAPI) - 1):
                api = api + ',' + str(selectAPI[x + 1][0])
        if (caseList.objects.filter(owningProject=owningProject, caseName=caseName).count() == 0):
            inter = caseList.objects.create(owningProject=owningProject, caseName=caseName,
                                            includeAPI=api, creator=user)
            inter.save()
            caseList.objects.filter(owningProject=owningProject, caseName=caseName).update(
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
            APIID = str(respList[i]['includeAPI']).split(',')
            num = 1
            respList[i]['describe'] = ''
            describe = []
            strAPI = ''
            for x in APIID:
                strAPI = '第' + str(num) + '个API：' + \
                         apiInfoTable.objects.filter(apiID=x).values('apiName')[0][
                             'apiName']
                describe.append(strAPI)
                respList[i]['describe'] = describe
                num = num + 1
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


def caseAPIInfo(request):
    result = {
        'code': -1,
        'info': '调用的方法错误，请使用GET方法查询！'
    }
    if request.method == 'GET':
        projectName = request.GET.get('projectName')
        projectID = projectList.objects.filter(projectName=projectName).values('id')[0]['id']
        resp2 = moduleList.objects.filter(owningListID=projectID).values('id')
        respList2 = list(resp2)
        respList = []
        for i in range(len(respList2)):
            resp = apiInfoTable.objects.filter(owningListID=respList2[i]['id']).values("apiID",
                                                                                       "apiName")
            respList = respList + list(resp)
        result = {
            'data': respList,
            'code': 0,
            'info': 'success'
        }
    return JsonResponse(result, safe=False)


def submitAPI(request):
    result = {
        'code': -1,
        'info': '调用的方法错误，请使用POST方法查询！'
    }
    if request.method == 'POST':
        req = json.loads(request.body)["params"]
        selectAPI = req['selectAPI']
        respList = []
        num = 1
        describe = []
        for x in selectAPI:
            strAPI = '第' + str(num) + '个API：' + \
                     apiInfoTable.objects.filter(apiID=int(x[0])).values('apiName')[0][
                         'apiName']
            describe.append(strAPI)
            respList = list(describe)
            num = num + 1
        code = 0
        info = '删除成功！'
    result = {
        'data': respList,
        'code': code,
        'info': info
    }
    return JsonResponse(result, safe=False)
