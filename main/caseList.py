# -*- coding: utf-8 -*-
from django.shortcuts import render, redirect
import json, time
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse, FileResponse
from main.models import *
from forms import *
from untils import until
from common.batchUntils import checkFormat
from common import batchstart


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
        projectName = request.GET["projectName"]
        pageNum = int(request.GET["pageNum"])
        cut = pageNum * 10
        resp = caseList.objects.filter(owningProject=projectName).values("id", "caseName", "includeAPI",
                                                                         "creator", "executor",
                                                                         "updateTime", "createTime",
                                                                         "runResult", "lastRunTime")
        user = request.session.get('username')
        totalCase = resp.count()
        disflag_right = "disabled"
        disflag_left = "disabled"
        pageview = False
        if (totalCase != 0):
            if (pageNum > 0):
                if (totalCase > pageNum * 10):  # 说明不在尾页
                    resp = resp[cut - 10:cut]
                    if (pageNum > 1):
                        disflag_left = ""
                else:  # 说明在尾页
                    pageNum = int((totalCase - 1) / 10) + 1
                    cut = pageNum * 10
                    resp = resp[cut - 10:cut]
                    disflag_left = ""
                if (totalCase < 11):
                    pageview = False
                else:
                    pageview = True
                if (totalCase <= pageNum * 10):
                    disflag_right = "disabled"
                else:
                    disflag_right = ""
            else:
                pageNum = int((totalCase - 1) / 10) + 1
                cut = pageNum * 10
                resp = resp[cut - 10:cut]
                disflag_left = ""
                pageview = True

        resp2 = users.objects.filter(username=user).values("batch_check", "batch_del", "batch_run")
        batch_check = resp2[0]['batch_check']
        batch_del = resp2[0]['batch_del']
        batch_run = resp2[0]['batch_run']
        permit = {
            'batch_check': batch_check,
            'batch_del': batch_del,
            'batch_run': batch_run
        }
        respList = list(resp)
        for i in range(len(respList)):
            id = respList[i]['id']
            respList[i]['projectName'] = projectName
            respList[i]['updateTime'] = str(respList[i]['updateTime']).split('.')[0]
            respList[i]['createTime'] = str(respList[i]['createTime']).split('.')[0]
            respList[i]['lastRunTime'] = str(respList[i]['lastRunTime']).split('.')[0]
            APIID = str(respList[i]['includeAPI']).split(',')
            num = 0
            respList[i]['describe'] = ''
            describe = []
            strAPI = ''
            deleteList = []
            if (APIID[0] != ''):
                for x in APIID:
                    if (apiInfoTable.objects.filter(apiID=x).count() == 0):
                        deleteList.append(x)
            if (len(deleteList) > 0):
                for y in deleteList:
                    APIID.remove(y)
                if (len(APIID) > 0):
                    api = str(APIID[0])
                    if (len(APIID) > 1):
                        for z in range(len(APIID) - 1):
                            api = api + ',' + str(APIID[z + 1])
                    caseList.objects.filter(id=id).update(includeAPI=api)
                else:
                    api = ''
                    caseList.objects.filter(id=id).update(includeAPI=api)
            if (APIID[0] != ''):
                for x in APIID:
                    mydict = {}
                    num = num + 1
                    respApi = apiInfoTable.objects.filter(apiID=x).values('apiName', 'lastRunResult',
                                                                          'depend_caseId',
                                                                          'depend_casedata')
                    respApiList = list(respApi)
                    strAPI = '第' + str(num) + '个API：' + respApiList[0]['apiName']
                    mydict["name"] = strAPI
                    result = respApiList[0]['lastRunResult']
                    if (result == 1):
                        mydict["runResult"] = "成功"
                    elif (result == 0):
                        mydict["runResult"] = "暂未执行"
                    elif (result == -1):
                        mydict["runResult"] = "失败"
                    depend = respApiList[0]['depend_caseId']
                    if (depend is None) or (depend == ''):
                        mydict["depend"] = "无"
                    else:
                        caseName = apiInfoTable.objects.filter(t_id=depend).values('apiName')[0]['apiName']
                        mydict["depend"] = str(caseName)
                    dependData = respApiList[0]['depend_casedata']
                    if (dependData is None) or (dependData == ''):
                        mydict["dependData"] = "无"
                    else:
                        mydict["dependData"] = str(dependData)
                    describe.append(mydict)
                    respList[i]['describe'] = describe
                respList[i]['apiCount'] = num
            else:
                respList[i]['apiCount'] = num
            if (respList[i]['executor'] is None) or (respList[i]['executor'] == ''):
                respList[i]['executor'] = '暂未执行'
            if (respList[i]['runResult'] is None) or (respList[i]['runResult'] == ''):
                respList[i]['runResult'] = '暂未执行'
            if (respList[i]['lastRunTime'] is None) or (respList[i]['lastRunTime'] == '') or (
                    respList[i]['lastRunTime'] == 'None'):
                respList[i]['lastRunTime'] = '暂未执行'
        result = {
            'pageNum': pageNum,
            'disflag_left': disflag_left,
            'pageview': pageview,
            'disflag_right': disflag_right,
            'data': respList,
            'permit': permit,
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
        if (APIID[0] != ''):
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
        'info': '接口调用错误！'
    }
    if request.method == 'POST':
        req = json.loads(request.body)["params"]
        id = req['idCookie']
        environment = req['environment']
        runResultName = req['runResultName']
        # reportflag = "Y"
        reportflag = req['reportflag']
        exeuser = request.session.get('username')
        starttime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        batchrun_list = []
        info = ""
        for case in id:
            paramList = str(case).split(',')
            caseID = paramList[0]
            cookieID = paramList[1]
            list = []
            caseName = caseList.objects.filter(id=caseID).values("caseName")[0]['caseName']
            includeAPI = caseList.objects.filter(id=caseID).values("includeAPI")[0]['includeAPI']
            APIID = str(includeAPI).split(',')
            if (APIID[0] != ''):
                for x in APIID:
                    list.append(x)
                    # [{"sname":"登录","list":[1,5,10],"cookices":{}}]
                if (cookieID == '不使用Cookie'):
                    batchrunJson = {
                        "sname": str(caseName),
                        "list": list,
                    }
                    batchrun_list.append(batchrunJson)
                else:
                    cookie = userCookies.objects.filter(id=cookieID).values("cookies")[0]['cookies']
                    cookices = json.loads(cookie)
                    batchrunJson = {
                        "sname": str(caseName),
                        "list": list,
                        "cookices": cookices,
                    }
                    batchrun_list.append(batchrunJson)
        batchResult = batchstart.start_main(batchrun_list, environment, reportflag, exeuser)
        if (reportflag == 'Y'):
            report_localName = batchResult["reportPath"]
            report_runName = runResultName
            successNum = batchResult["sNum"]
            failNum = batchResult["fNum"]
            errorNum = batchResult["eNum"]
            totalNum = successNum + failNum + errorNum
            endtime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
            result_infos = {
                "report_runName": report_runName,
                "environment": environment,
                "startTime": starttime,
                "endTime": endtime,
                "totalNum": totalNum,
                "successNum": successNum,
                "failNum": failNum,
                "errorNum": errorNum,
                "executor": exeuser,
                "report_localName": report_localName,
            }
            try:
                s = reports.objects.create(**result_infos)
                s.save()
            except BaseException as e:
                print(" SQL Error: %s" % e)
                result = {'code': -2, 'info': 'sql error'}
                return JsonResponse(result)
            for case in id:
                paramList = str(case).split(',')
                caseID = paramList[0]
                inter = caseList.objects.get(id=caseID)
                inter.lastRunTime = starttime
                inter.reportLocation = report_localName
                includeAPI = caseList.objects.filter(id=caseID).values("includeAPI")[0]['includeAPI']
                APIID = str(includeAPI).split(',')
                Success = True
                if (APIID[0] != ''):
                    for x in APIID:
                        flag = int(
                            apiInfoTable.objects.filter(apiID=x).values("lastRunResult")[0][
                                'lastRunResult'])
                        if (flag == -1):
                            Success = False
                if (Success):
                    inter.runResult = str(environment) + "环境运行成功"
                else:
                    inter.runResult = str(environment) + "环境运行失败"
                inter.save()
                result = {"code": 0, "info": "执行结束，结果请查看报告"}
        else:
            for case in id:
                paramList = str(case).split(',')
                caseID = paramList[0]
                successNum = batchResult["sNum"]
                failNum = batchResult["fNum"]
                errorNum = batchResult["eNum"]
                inter = caseList.objects.get(id=caseID)
                inter.lastRunTime = starttime
                if (failNum == 0) and (errorNum == 0):
                    inter.runResult = str(environment) + "环境运行成功"
                else:
                    inter.runResult = str(environment) + "环境运行失败"
                inter.save()
                info = u"执行结束,结果：<br>成功：" + str(successNum) + "；失败：" + str(failNum) + "；出错：" + str(
                    errorNum)
            result = {
                "code": 0,
                "info": info
            }
    return JsonResponse(result, safe=False)


def runCase(request):
    result = {'code': -3, 'info': '接口调用错误！'}
    if request.method == 'POST':
        req = json.loads(request.body)["params"]
        id = req['id']
        environment = req['environment']
        runResultName = req['runResultName']
        # reportflag = "Y"
        reportflag = req['reportflag']
        exeuser = request.session.get('username')
        starttime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        paramList = str(id).split(',')
        caseID = paramList[0]
        cookieID = paramList[1]
        list = []
        caseName = caseList.objects.filter(id=caseID).values("caseName")[0]['caseName']
        includeAPI = caseList.objects.filter(id=caseID).values("includeAPI")[0]['includeAPI']
        APIID = str(includeAPI).split(',')
        if (APIID[0] != ''):
            for x in APIID:
                list.append(x)
                # [{"sname":"登录","list":[1,5,10],"cookices":{}}]
            if (cookieID == '不使用Cookie'):
                batchrunJson = {
                    "sname": str(caseName),
                    "list": list,
                }
            else:
                cookie = userCookies.objects.filter(id=cookieID).values("cookies")[0]['cookies']
                cookices = json.loads(cookie)
                batchrunJson = {
                    "sname": str(caseName),
                    "list": list,
                    "cookices": cookices,
                }
            batchrun_list = []
            batchrun_list.append(batchrunJson)
            batchResult = batchstart.start_main(batchrun_list, environment, reportflag, exeuser)
            if (reportflag == 'Y'):
                report_localName = batchResult["reportPath"]
                report_runName = runResultName
                successNum = batchResult["sNum"]
                failNum = batchResult["fNum"]
                errorNum = batchResult["eNum"]
                totalNum = successNum + failNum + errorNum
                endtime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
                result_infos = {
                    "report_runName": report_runName,
                    "environment": environment,
                    "startTime": starttime,
                    "endTime": endtime,
                    "totalNum": totalNum,
                    "successNum": successNum,
                    "failNum": failNum,
                    "errorNum": errorNum,
                    "executor": exeuser,
                    "report_localName": report_localName,
                }
                try:
                    s = reports.objects.create(**result_infos)
                    s.save()
                except BaseException as e:
                    print(" SQL Error: %s" % e)
                    result = {'code': -2, 'info': 'sql error'}
                    return JsonResponse(result)
                inter = caseList.objects.get(id=caseID)
                inter.lastRunTime = starttime
                inter.reportLocation = report_localName
                if (totalNum == successNum):
                    inter.runResult = str(environment) + "环境运行成功"
                else:
                    inter.runResult = str(environment) + "环境运行失败"
                inter.save()
                result = {"code": 0, "info": "执行结束，结果请查看报告"}
            else:
                successNum = batchResult["sNum"]
                failNum = batchResult["fNum"]
                errorNum = batchResult["eNum"]
                inter = caseList.objects.get(id=caseID)
                inter.lastRunTime = starttime
                if (failNum == 0) and (errorNum == 0):
                    inter.runResult = str(environment) + "环境运行成功"
                else:
                    inter.runResult = str(environment) + "环境运行失败"
                inter.save()
                info = u"执行结束,结果：<br>成功：" + str(successNum) + "；失败：" + str(failNum) + "；出错：" + str(
                    errorNum)
                result = {
                    "code": 0,
                    "info": info
                }
        else:
            code = -1
            info = '用例下不存在接口！'
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
        verification = True
        if (originalIncludeAPI == api and originalCaseName == caseName):
            code = -1
            info = '未做任何修改！'
            verification = False
            result = {
                'code': code,
                'info': info
            }
        if (caseList.objects.filter(owningProject=owningProject, caseName=caseName).count() > 0) and (
                originalCaseName != caseName):
            code = -2
            info = '用例名称与已存在的用例重复！'
            verification = False
            result = {
                'code': code,
                'info': info
            }
        if (verification):
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
                inter.lastRunTime = None
                inter.caseName = caseName
                inter.save()
                code = 0
                info = '修改成功！'
                result = {
                    'code': code,
                    'info': info
                }
    return JsonResponse(result, safe=False)
