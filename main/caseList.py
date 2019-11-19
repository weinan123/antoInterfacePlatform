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
            num = 0
            respList[i]['describe'] = ''
            describe = []
            strAPI = ''
            for x in APIID:
                mydict = {}
                num = num + 1
                strAPI = '第' + str(num) + '个API：' + \
                         apiInfoTable.objects.filter(apiID=x).values('apiName')[0][
                             'apiName']
                mydict["name"] = strAPI
                mydict["runResult"] = "成功"
                mydict["href"] = "#"
                describe.append(mydict)
                respList[i]['describe'] = describe
            respList[i]['apiCount'] = num
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
            moduleName = moduleList.objects.filter(id=respList2[i]['id']).values("moduleName")[0][
                'moduleName']
            resp = apiInfoTable.objects.filter(owningListID=respList2[i]['id']).values("apiID",
                                                                                       "apiName")
            resp = list(resp)
            result2 = {
                'data': resp,
                'moduleName': moduleName
            }
            respList.append(result2)
        result = {
            'data': respList,
            'code': 0,
            'info': 'success'
        }
    return JsonResponse(result, safe=False)


def getCaseAPIInfo(request):
    result = {
        'code': -1,
        'info': '调用的方法错误，请使用GET方法查询！'
    }
    if request.method == 'GET':
        id = request.GET.get('id')  # 获取的是用例的id
        resp = caseList.objects.filter(id=id).values("includeAPI", "owningProject", "caseName")
        respList = list(resp)
        APIID = str(respList[0]['includeAPI']).split(',')
        checkList = []
        temp = []
        print APIID
        for x in APIID:
            temp = []
            temp.append(x)
            checkList.append(temp)
        projectName = respList[0]['owningProject']
        caseName = respList[0]['caseName']
        projectID = projectList.objects.filter(projectName=projectName).values('id')[0]['id']
        resp2 = moduleList.objects.filter(owningListID=projectID).values('id')
        respList2 = list(resp2)
        respList = []
        # 获取对应项目下，所有的api
        for i in range(len(respList2)):
            moduleName = moduleList.objects.filter(id=respList2[i]['id']).values("moduleName")[0][
                'moduleName']
            resp = apiInfoTable.objects.filter(owningListID=respList2[i]['id']).values("apiID",
                                                                                       "apiName")
            resp = list(resp)
            result2 = {
                'data': resp,
                'moduleName': moduleName
            }
            respList.append(result2)
        result = {
            'modifyCheckList': checkList,
            'caseName': caseName,
            'data': respList,
            'code': 0,
            'info': 'success'
        }
    return JsonResponse(result, safe=False)


def getUserCookieList(request):
    result = {
        'code': -1,
        'info': '调用的方法错误，请使用POST方法查询！'
    }
    if request.method == 'POST':
        req = json.loads(request.body)["params"]
        user = request.session.get('username')
        projectName = req['projectName']
        environment = req['environment']
        resp = userCookies.objects.filter(user=user, projectname=projectName,
                                          evirment=environment).values('id', 'cookiename')
        respList = list(resp)
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


def caseDelete(request):
    if request.method == 'GET':
        id = request.GET.get('id')
        caseList.objects.filter(id=id).delete()
        code = 0
        info = '删除成功！'
        result = {
            'code': code,
            'info': info
        }
    return JsonResponse(result, safe=False)


def caseBatchDelete(request):
    result = {
        'code': -1,
        'info': '未知错误！'
    }
    if request.method == 'POST':
        req = json.loads(request.body)["params"]
        idDelete = req['idDelete']
        for x in idDelete:
            caseList.objects.filter(id=x[0]).delete()
        code = 0
        info = '删除成功！'
        result = {
            'code': code,
            'info': info
        }
    return JsonResponse(result, safe=False)


def caseBatchRun(request):
    result = {
        'code': -1,
        'info': '未知错误！'
    }
    if request.method == 'POST':
        req = json.loads(request.body)["params"]
        idRun = req['idRun']
        idCookie = req['idCookie']
        for x in idRun:
            print x
        print '**************************************'
        print '**************************************'
        for x in idCookie:
            print x
        code = 0
        info = '运行成功！'
        result = {
            'code': code,
            'info': info
        }
    return JsonResponse(result, safe=False)


def runCase(request):
    if request.method == 'GET':
        id = request.GET.get('id')
        print id
        code = 0
        info = '运行成功！'
        result = {
            'code': code,
            'info': info
        }
    return JsonResponse(result, safe=False)


def modifyCase(request):
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
        caseID = req['caseID']
        if (len(selectAPI) > 1):
            for x in range(len(selectAPI) - 1):
                api = api + ',' + str(selectAPI[x + 1][0])
        originalIncludeAPI = str(
            caseList.objects.filter(id=caseID).values("includeAPI")[0]['includeAPI'])
        originalCaseName = str(caseList.objects.filter(id=caseID).values("caseName")[0]['caseName'])

        if (originalIncludeAPI == api and originalCaseName == caseName):
            code = -1
            info = '未做任何修改！'
            result = {
                'code': code,
                'info': info
            }
        else:
            if (originalIncludeAPI == api):  # 说明只修改了caseName，此时不需要将执行情况重置
                inter = caseList.objects.get(id=caseID)
                inter.includeAPI = api
                inter.caseName = caseName
                inter.save()
                code = 0
                info = '修改成功！'
                result = {
                    'code': code,
                    'info': info
                }
            else:
                inter = caseList.objects.get(id=caseID)
                inter.includeAPI = api
                inter.executor = ''
                inter.runResult = ''
                # inter.lastRunTime = ''
                inter.caseName = caseName
                inter.save()
                code = 0
                info = '修改成功！'
                result = {
                    'code': code,
                    'info': info
                }
    return JsonResponse(result, safe=False)
