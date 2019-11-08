# -*- coding: utf-8 -*-
from django.shortcuts import render
from models import apiInfoTable, projectList,moduleList,reports, users
import time
import json
from django.http.response import JsonResponse
from common import batchstart, batchUntils
import sys
reload(sys)
sys.setdefaultencoding('utf8')


def apiCases(request):
    return render(request, "apiCases.html")

def getPermission(request):
    username = str(request.GET['username'])
    # username = request.session.get('username')
    try:
        query = users.objects.get(username=username)
    except Exception as e:
        result = {
            "code": -1,
            "info": "get permission failed,username:" + username
        }
        return JsonResponse(result)
    permission_run = query.batch_run
    permission_del = query.batch_del
    permission_view = query.batch_check
    permission = {"code": 0,
                  "username": username,
                  "permits": {
                      "permission_run": permission_run,
                      "permission_del": permission_del,
                      "permission_view": permission_view
                  }
                  }
    return JsonResponse(permission)

def apidel(request):
    result={}
    if request.method == 'POST':
        req = json.loads(request.body)["params"]
        id = req['aid']
        ainfo = apiInfoTable.objects.get(apiID=id)
        if ainfo:
            try:
                ainfo.delete()
                print("删除成功")
            except BaseException as e:
                result = {'code': -1, 'info': 'sql error' + str(e)}
                return JsonResponse(result)
            result = {'code': 0, 'info': 'delete success'}
        else:
            result = {'code': -2,'info':'no exist'}
    return JsonResponse(result)


def batchdel(request):
    result = {}
    if request.method == 'POST':
        req = json.loads(request.body)["params"]
        idlist = req['idList']
        # print idlist
        slist = []
        flist = []
        for id in idlist:
            # id = ids[0]
            ainfo = apiInfoTable.objects.get(apiID=id)
            if ainfo:
                try:
                    ainfo.delete()
                    print("删除%d成功" % id)
                    slist.append(id)
                except BaseException as e:
                    flist.append(id)
                    print("删除%d失败:%s" % (id, str(e)))
            else:
                flist.append(id)
                print("删除%d失败:不存在" % id)
        infos = "delete success:" + str(len(slist)) + ",fail:" + str(len(flist))
        result = {'code': 0, 'info': infos, 'successNum': len(slist)}
    return JsonResponse(result)

def runsingle(request):
    result = {}
    if request.method == 'POST':
        req = json.loads(request.body)["params"]
        id = req["id"]
        environment = req["environment"]
        dtime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        respResult = batchUntils.getResp(id,environment, dtime)
        code = respResult["code"]
        responseText = ""
        if code == 0:
            resp = respResult["response"]
            assertinfo = respResult["assert"]
        else:
            respinfo = respResult["info"]
            result = {"code": -1, "datas": respinfo}
            return JsonResponse(result)
        try:
            statusCode = resp.status_code
            text = resp.text
            responseText = text
        except AttributeError as e:
            statusCode = 400
            text = "error!code: -999"

        if assertinfo == "":
            datas = {"status_code": statusCode}
            if str(statusCode).startswith("2"):
                apiInfoTable.objects.filter(apiID=id).update(lastRunTime=dtime, lastRunResult=1, response=responseText)
                result = {"code": 0, "info": "run success", "datas": str(datas)}
            else:
                apiInfoTable.objects.filter(apiID=id).update(lastRunTime=dtime, lastRunResult=-1, response=responseText)
                result = {"code": 1, "info": "run fail", "datas": str(datas)}
        else:
            datas = {"status_code": statusCode, "responseText": str(text), "assert": str(assertinfo)}
            if str(assertinfo) in str(text):
                apiInfoTable.objects.filter(apiID=id).update(lastRunTime=dtime, lastRunResult=1, response=responseText)
                result = {"code": 0, "info": "run success", "datas": str(datas)}
            else:
                apiInfoTable.objects.filter(apiID=id).update(lastRunTime=dtime, lastRunResult=-1, response=responseText)
                result = {"code": 1, "info": "run fail", "datas": str(datas)}
        # print result
    return JsonResponse(result)

def batchrun(request):
    result = {}
    if request.method == 'POST':
        req = json.loads(request.body)["params"]
        idlist = req['idList']
        environment = req["environment"]
        if len(idlist)==0:
            result = {"code": -1, "info": "执行列表为空"}
            return JsonResponse(result)
        reportflag = req["reportflag"]
        exeuser = request.session.get('username')
        starttime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        if reportflag == True:
            reflag = "Y"
        else:
            reflag = "N"
        for id in idlist:
            try:
                query = apiInfoTable.objects.get(apiID=id)
            except Exception as e:
                result = {"code": -2, "datas": "用例不存在，" + str(e)}
                return JsonResponse(result)
            if query.method == "" or query.url == "":
                result = {"code": -1, "datas": "method或url不能为空"}
                return JsonResponse(result)

        batchResult = batchstart.start_main(idlist,environment, reflag, exeuser)
        # print batchResult
        if reportflag == True:
            report_localName = batchResult["reportPath"]
            report_runName = req["pmName"] +"_" + batchResult["reportname"]
            successNum = batchResult["sNum"]
            failNum = batchResult["fNum"]
            errorNum = batchResult["eNum"]
            totalNum = successNum + failNum + errorNum
            endtime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
            result_infos = {
                "report_runName": report_runName,
                "environment":environment,
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
                result = {'code': -1, 'info': 'sql error'}
                return JsonResponse(result)
            result = {"code": 0, "info": "执行结束，结果请查看报告"}
        else:
            result = {"code": 0, "info": "执行结束,结果：" + str(batchResult)}
    return JsonResponse(result)


def getapiInfos(request):
    result = {}
    if request.method == 'GET':
        id = request.GET['apiid']
        environment = request.GET["environment"]
        try:
            query = apiInfoTable.objects.get(apiID=id)
        except BaseException as e:
            print(" SQL Error: %s" % e)
            result = {'code': -1, 'info': 'sql error!'}
            return JsonResponse(result)
        if query != None:
            json_dict = {}
            module_list = []
            header_list = []
            json_dict["id"] = query.apiID
            json_dict["name"] = query.apiName
            json_dict["creator"] = query.creator
            json_dict["method"] = query.method
            showbodyState =0
            body_list = []
            if query.headers != "{}" and query.headers != "":
                header_data = json.loads(query.headers)
                for k in header_data:
                    header_dict = {}
                    header_dict["type"] = k
                    header_dict["value"] = header_data[k]
                    header_list.append(header_dict)
                # print header_list
                json_dict["header"] = header_list
            else:
                json_dict["header"] = []
            # print header_list
            # print("query.body:",query.body)
            if query.body != "{}" and query.body != "":
                bodydata = json.loads(query.body)
                # print("bodydata:", bodydata)
                stateflag = bodydata["showflag"]
                # print("stateflag:",stateflag)
                if stateflag==3:
                    showbodyState = 3
                    for i in bodydata["datas"]:
                        body_dict = {}
                        # print i
                        body_dict["value"] = i["paramValue"]
                        body_list.append(body_dict)
                    json_dict["body"] = body_list
                elif stateflag==1:
                    for i in bodydata["datas"]:
                        body_dict = {}
                        # print i
                        body_dict["name"] = i["paramName"]
                        body_dict["type"] = i["paramType"]
                        body_dict["value"] = i["paramValue"]
                        body_list.append(body_dict)
                    showbodyState = 1
                    json_dict["body"] = body_list
                elif stateflag == 2:
                    showbodyState = 2
                    for i in bodydata["datas"]:
                        body_dict = {}
                        # print i
                        body_dict["name"] = i["paramName"]
                        body_dict["type"] = i["paramType"]
                        body_dict["value"] = i["paramValue"]
                        body_list.append(body_dict)
                    json_dict["body"] = body_list
                    # print("body:****", json_dict["body"])
                elif stateflag == 0:
                    showbodyState = 0
                    for i in bodydata["datas"]:
                        body_dict = {}
                        # print i
                        body_dict["name"] = i["paramName"]
                        body_dict["type"] = i["paramType"]
                        body_dict["value"] = i["paramValue"]
                        body_list.append(body_dict)
                    json_dict["body"] = body_list
                else:
                    showbodyState = 0
                    json_dict["body"] = []
            else:
                json_dict["body"] = []
            json_dict["url"] = query.url
            json_dict["assert"] = query.assertinfo.replace(" ", "")
            json_dict["listid"] = query.owningListID
            json_dict["response"] = query.response
            listdata = moduleList.objects.get(id=int(query.owningListID))
            json_dict["moduleName"] = listdata.moduleName
            pid = listdata.owningListID
            json_dict["projectName"] = projectList.objects.get(id=int(pid)).projectName
            json_dict["host"] = batchUntils.getHost(int(query.host),environment)
            modulelist = moduleList.objects.filter(owningListID=int(pid)).values("moduleName").distinct()
            for module in modulelist:
                module_list.append(module["moduleName"])
            # print "*******modulelist*******", module_list
            result = {'code': 0, 'datas': json_dict, 'info': 'success',"module_list": module_list,"showbody":showbodyState}
    return JsonResponse(result)


def getAllCases(request):
    # 根据分页获取数据
    pagenum = request.GET["pageNum"]
    count = request.GET["pageCount"]
    startidx = (int(pagenum) - 1) * int(count)
    endidx = int(pagenum) * int(count)
    # print(startidx, endidx)
    sear = request.GET['searchinfo']
    projectID = request.GET["projectID"]
    moduleName = request.GET["moduleName"]
    print("***11*",projectID,moduleName,sear)
    pidList = []
    if projectID != "" and moduleName != "":
        moduleID = moduleList.objects.get(owningListID=projectID , moduleName=moduleName).id
        pidList.append(moduleID)
    elif projectID != "":
        moduleID = moduleList.objects.filter(owningListID=projectID).values("id")
        for pj in moduleID:
            pidList.append(pj["id"])
    if len(pidList) == 0:
        apilist2 = apiInfoTable.objects.filter(apiName__contains=sear).order_by("apiID")[startidx:endidx]
        count = apiInfoTable.objects.filter(apiName__contains=sear).count()
    else:
        apilist2 = apiInfoTable.objects.filter(owningListID__in=pidList).filter(apiName__contains=sear).order_by("apiID")[
                startidx:endidx]
        count = apiInfoTable.objects.filter(owningListID__in=pidList).filter(apiName__contains=sear).count()
    # 使用get方法只获取一条匹配的数据，若有多条会报错,有多条使用filter
    json_list = []
    for i in apilist2:
        json_dict = {}
        json_dict["id"] = i.apiID
        json_dict["name"] = i.apiName
        if i.lastRunResult == 0:
            json_dict["lastrunrslt"] = 0
        else:
            json_dict["lastrunrslt"] = i.lastRunResult
        if i.lastRunTime is None:
            json_dict["lastruntime"] = 'null'
        else:
            json_dict["lastruntime"] = i.lastRunTime.strftime('%Y-%m-%d %H:%M:%S')
        json_dict["owing"] = i.creator
        json_dict["listid"] = i.owningListID
        json_dict["method"] = i.method
        json_dict["url"] = i.url
        json_dict["t_id"] = i.t_id
        json_dict["depend_caseId"] = i.depend_caseId
        # print("****i.depend_caseId****",i.depend_caseId)
        if i.depend_caseId != "" and i.depend_caseId is not None:
            json_dict["tid_id"] = apiInfoTable.objects.get(t_id=i.depend_caseId).apiID  #tid_id表示tid不为空的用例所依赖用例的id
        else:
            json_dict["tid_id"] = ""
        # print("****json_dict[tid_id]****",json_dict["tid_id"])
        json_dict["depend_data"] = i.depend_casedata
        json_list.append(json_dict)
    result = {
        'data': json_list,
        'code': 0,
        'info': 'success',
        'totalCount': count,
        'currentPageCount': len(json_list),
    }
    return JsonResponse(result)


def getProjInfos(request):
    result = {}
    if request.method == 'GET':
        try:
            id = request.GET["pid"]
            query = projectList.objects.get(id=id)
            projName = query.projectName
            moduName = query.moduleName
        except Exception as e:
            projName = ""
            moduName = ""
        projectLists = []
        allModuleList = []
        try:
            projInfos = projectList.objects.filter().values("id", "projectName").distinct()
            modInfos = moduleList.objects.filter().values("owningListID", "moduleName").distinct()
        except Exception as e:
            result = {'code': -1, 'info': 'sql error:' + str(e)}
            return JsonResponse(result)
        for pro in projInfos:
            projectLists.append(pro)
        for mod in modInfos:
            allModuleList.append(mod)
        result = {'code': 0,
                  'info': 'query success',
                  'data': {"allProjList": projectLists,
                           "allModuleList": allModuleList,
                           "projName": projName,
                           "moduName": moduName}}
    return JsonResponse(result)

def getProjectInfos(request):
    result = {}
    proid = int(request.GET["pid"])
    projectName = ""
    moduleName = ""
    try:
        pmInfos = projectList.objects.filter(id=proid).values("projectName", "moduleName").distinct()
    except Exception as e:
        result = {'code': -1, 'info': 'sql error:' + str(e)}
        return JsonResponse(result)
    for pm in pmInfos:
        projectName = pm["projectName"]
        moduleName = pm["modubleName"]
    result = {'code': 0, 'info': 'query success',
                  'data': {"projectName": projectName, "moduleName": moduleName}}
    return JsonResponse(result)