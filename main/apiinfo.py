# -*- coding: utf-8 -*-
from django.shortcuts import render
from models import apiInfoTable, interfaceList,reports, users
import time
import json
from django.http.response import JsonResponse
from untils.until import mul_bodyData
from untils import sendRequests
from common import authService,batchstart,getDependData
import sys
reload(sys)
sys.setdefaultencoding('utf8')


def apiCases(request):
    return render(request, "apiCases.html")

def getPermission(request):
    username = request.session.get('username')
    query = users.objects.get(username=username)
    permission_run = query.batch_run
    permission_del = query.batch_del
    permission_view = query.batch_check
    permission = {"code": 0,
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
        print id
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
        print idlist
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
        result = {'code': 0, 'info': infos}
    return JsonResponse(result)

def runsingle(request):
    result = {}
    if request.method == 'POST':
        req = json.loads(request.body)["params"]
        id = req["id"]
        try:
            query = apiInfoTable.objects.get(apiID=id)
        except Exception as e:
            result = {"code": -2, "datas": "执行用例不存在，" + str(e)}
            return JsonResponse(result)
        methods = query.method
        send_url = query.url
        if methods == "" or send_url == "":
            result = {"code": -1, "datas": "参数不能为空"}
            return JsonResponse(result)
        headers = query.headers
        if headers != "":
            headers = json.loads(headers)
        bodyinfor = query.body
        if bodyinfor != "" or bodyinfor != "{}":
            bodyinfor = json.loads(bodyinfor)
        # 判断是否有关联用例
        depend_flag = query.depend_caseId

        dependData = []
        if depend_flag == "" or depend_flag is None:
            print("not depend")
        else:
            depend_list = depend_flag
            depend_data = query.depend_casedata
            if depend_data != "" or depend_data != "{}":
                dependData = getDependData.getdepands(depend_list, depend_data)
                print("dependData:",dependData)
            else:
                print("depend data is None.")
        listid = query.owningListID
        querylist = interfaceList.objects.get(id=listid)
        host = querylist.host
        url = host + send_url
        # 处理数据类型的方法
        send_body, files = mul_bodyData(bodyinfor)
        if len(dependData) != 0:
            for dd in dependData:
                send_body[dd.keys()[0]] = dd.values()[0]
        print("body:",send_body)
        isRedirect = query.isRedirect
        isScreat = query.isScreat
        key_id = query.key_id
        secret_key = query.secret_key
        timestamp = int(time.time())
        assertinfo = str(query.assertinfo)
        dtime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        # 非加密执行接口
        if isScreat == False or isScreat == "":
            try:
                resp = sendRequests.sendRequest().sendRequest(methods, url, headers, send_body, files, isRedirect)
            except Exception as e:
                datas = {"status_code": -999, "error": str(e)}
                apiInfoTable.objects.filter(apiID=id).update(lastRunTime=dtime, lastRunResult=-1)
                result = {"code": -1, "info": "run error", "datas": str(datas)}
                return JsonResponse(result)
        # 加密执行
        else:
            credentials = authService.BceCredentials(key_id, secret_key)
            print credentials
            headers_data = {
                'Accept': 'text/html, */*; q=0.01',
                'X-Requested-With': 'XMLHttpRequest',
                'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2272.89 Safari/537.36'
            }
            headersOpt = {'X-Requested-With', 'User-Agent', 'Accept'}
            Authorization = authService.simplify_sign(credentials, methods, send_url, headers_data, timestamp, 300,
                                                      headersOpt)
            try:
                resp = sendRequests.sendRequest().sendSecretRequest(key_id, secret_key, Authorization, methods, url,send_url, headers, send_body, files, isRedirect)
            except Exception as e:
                datas = {"status_code": -999, "error": str(e)}
                apiInfoTable.objects.filter(apiID=id).update(lastRunTime=dtime, lastRunResult=-1)
                result = {"code": -1, "info": "run error", "datas": str(datas)}
                return JsonResponse(result)
        try:
            statusCode = resp.status_code
            text = resp.text
        except AttributeError as e:
            statusCode = -999
            text = "error!code: -999"

        if assertinfo == "":
            datas = {"status_code": statusCode}
            if statusCode == 200:
                apiInfoTable.objects.filter(apiID=id).update(lastRunTime=dtime, lastRunResult=1)
                result = {"code": 0, "info": "run success", "datas": str(datas)}
            else:
                apiInfoTable.objects.filter(apiID=id).update(lastRunTime=dtime, lastRunResult=-1)
                result = {"code": 1, "info": "run fail", "datas": str(datas)}
        else:
            datas = {"status_code": statusCode, "responseText": str(text), "assert": str(assertinfo)}
            if str(assertinfo) in str(text):
                apiInfoTable.objects.filter(apiID=id).update(lastRunTime=dtime, lastRunResult=1)
                result = {"code": 0, "info": "run success", "datas": str(datas)}
            else:
                apiInfoTable.objects.filter(apiID=id).update(lastRunTime=dtime, lastRunResult=-1)
                result = {"code": 1, "info": "run fail", "datas": str(datas)}
        print result
    return JsonResponse(result)

def batchrun(request):
    result = {}
    if request.method == 'POST':
        req = json.loads(request.body)["params"]
        idlist = req['idList']
        reportflag = req["reportflag"]
        exeuser = request.session.get('username')
        starttime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        if reportflag == True:
            reflag = "Y"
        else:
            reflag = "N"
        batchResult = batchstart.start_main(idlist,reflag, exeuser)
        print batchResult
        if reportflag == True:
            report_localName = batchResult["reportPath"]
            report_runName = req["pmName"] +"_" + batchResult["reportname"]
            totalNum = len(idlist)
            successNum = batchResult["sNum"]
            failNum = batchResult["fNum"]
            errorNum = batchResult["eNum"]
            endtime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
            result_infos = {
                "report_runName": report_runName,
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
                print header_list
                json_dict["header"] = header_list
            else:
                json_dict["header"] = []
            print header_list
            print("query.body:",query.body)
            if query.body != "{}" and query.body != "":
                bodydata = json.loads(query.body)
                print("bodydata:", bodydata)
                stateflag = bodydata["showflag"]
                print("stateflag:",stateflag)
                if stateflag==3:
                    showbodyState = 3
                    for i in bodydata["datas"]:
                        body_dict = {}
                        print i
                        body_dict["value"] = i["paramValue"]
                        body_list.append(body_dict)
                    json_dict["body"] = body_list
                elif stateflag==1:
                    for i in bodydata["datas"]:
                        body_dict = {}
                        print i
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
                        print i
                        body_dict["name"] = i["paramName"]
                        body_dict["type"] = i["paramType"]
                        body_dict["value"] = i["paramValue"]
                        body_list.append(body_dict)
                    json_dict["body"] = body_list
                    print("body:****", json_dict["body"])
                elif stateflag == 0:
                    showbodyState = 0
                    for i in bodydata["datas"]:
                        body_dict = {}
                        print i
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
            json_dict["assert"] = query.assertinfo
            json_dict["listid"] = query.owningListID
            listdata = interfaceList.objects.get(id=query.owningListID)
            json_dict["projectName"] = listdata.projectName
            json_dict["moduleName"] = listdata.moduleName
            json_dict["host"] = listdata.host
            modulelist = interfaceList.objects.filter().values("projectName", "moduleName").distinct()
            print modulelist
            for module in modulelist:
                if module["projectName"] == json_dict["projectName"]:
                    module_list.append(module["moduleName"])
            result = {'code': 0, 'datas': json_dict, 'info': 'success',"module_list": module_list,"showbody":showbodyState}
    return JsonResponse(result)


def getAllCases(request):
    # 根据分页获取数据
    pagenum = request.GET["pageNum"]
    count = request.GET["pageCount"]
    startidx = (int(pagenum) - 1) * int(count)
    endidx = int(pagenum) * int(count)
    print(startidx, endidx)
    sear = request.GET['searchinfo']
    projectName = request.GET["projectName"]
    moduleName = request.GET["moduleName"]
    pidList = []
    if projectName != "" or moduleName != "":
        if moduleName != "":
            query_projId = interfaceList.objects.filter(projectName=projectName).filter(moduleName=moduleName).values("id")
        else:
            query_projId = interfaceList.objects.filter(projectName=projectName).values("id")
        for pj in query_projId:
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
        projectLists = []
        allModuleList = []
        try:
            projInfos = interfaceList.objects.filter().values("projectName").distinct()
            modInfos = interfaceList.objects.filter().values("projectName", "moduleName").distinct()
        except Exception as e:
            result = {'code': -1, 'info': 'sql error:' + str(e)}
            return JsonResponse(result)
        for pro in projInfos:
            projectLists.append(pro["projectName"])
        for mod in modInfos:
            allModuleList.append(mod)
        result = {'code': 0, 'info': 'query success', 'data': {"allProjList": projectLists, "allModuleList": allModuleList}}
    return JsonResponse(result)

def getProjectInfos(request):
    result = {}
    proid = int(request.GET["pid"])
    projectName = ""
    moduleName = ""
    try:
        pmInfos = interfaceList.objects.filter(id=proid).values("projectName", "moduleName").distinct()
    except Exception as e:
        result = {'code': -1, 'info': 'sql error:' + str(e)}
        return JsonResponse(result)
    for pm in pmInfos:
        projectName = pm["projectName"]
        moduleName = pm["modubleName"]
    result = {'code': 0, 'info': 'query success',
                  'data': {"projectName": projectName, "moduleName": moduleName}}
    return JsonResponse(result)