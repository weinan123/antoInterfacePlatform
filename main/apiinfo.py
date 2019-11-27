# -*- coding: utf-8 -*-
from django.shortcuts import render
from models import apiInfoTable, projectList,moduleList,reports, users, hostTags, userCookies
import time, re
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
    result = {}
    if request.method == 'POST':
        req = json.loads(request.body)["params"]
        id = req['aid']
        ainfo = apiInfoTable.objects.get(apiID=id)
        # 判断用例是否有被依赖的用例
        dependflag = False
        if ainfo.t_id is not None:
            dependflag = checkdependCaseID(ainfo.t_id)
        if dependflag:
            result = {'code': -1, 'info': '接口被依赖不能删除'}
        else:
            if ainfo:
                try:
                    ainfo.delete()
                    print("删除成功")
                except BaseException as e:
                    result = {'code': -1, 'info': 'sql error' + str(e)}
                    return JsonResponse(result)
                result = {'code': 0, 'info': 'delete success'}
            else:
                result = {'code': -2, 'info': 'no exist'}
    return JsonResponse(result)


def batchdel(request):
    result = {}
    if request.method == 'POST':
        req = json.loads(request.body)["params"]
        idlist = req['idList']
        slist = []
        flist = []
        for id in idlist:
            try:
                ainfo = apiInfoTable.objects.get(apiID=id)
            except Exception as e:
                print(u"删除%d失败:%s" % (id, str(e)))
                flist.append(id)
                continue
            # 判断用例是否有被依赖的用例
            dependflag = False
            if ainfo.t_id is not None:
                dependflag = checkdependCaseID(ainfo.t_id)
            if dependflag:
                flist.append(id)
            else:
                try:
                    ainfo.delete()
                    print(u"删除%d成功" % id)
                    slist.append(id)
                except BaseException as e:
                    flist.append(id)
                    print(u"删除%d失败:%s" % (id, str(e)))
        infos = "delete success:" + str(len(slist)) + ",fail:" + str(len(flist))
        result = {'code': 0, 'info': infos, 'successNum': len(slist)}
    return JsonResponse(result)

def checkdependCaseID(tid):
    query = apiInfoTable.objects.filter(depend_caseId=tid)
    if len(query) == 0:
        flag = False
    else:
        flag = True
    return flag


def runsingle(request):
    result = {}
    if request.method == 'POST':
        req = json.loads(request.body)["params"]
        id = req["id"]
        environment = req["environment"]
        dtime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        exeuser = request.session.get('username')
        try:
            projectid = moduleList.objects.get(id=int(apiInfoTable.objects.get(apiID=int(id)).owningListID)).owningListID
            projectname = projectList.objects.get(id=int(projectid)).projectName
            cookies = getCookies(environment, exeuser, projectname)
        except Exception as e:
            cookies = None
        respResult = batchUntils.getResp(id,environment, dtime, cookices=cookies)
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
            assertResult = batchUntils.checkAssertinfo(str(assertinfo), str(text))
            if assertResult:
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
                result = {"code": -2, "info": "用例不存在，" + str(e)}
                return JsonResponse(result)
            if query.method == "" or query.url == "":
                result = {"code": -1, "info": "method或url不能为空"}
                return JsonResponse(result)
        # batchrun_list = [{"sname": "批量执行", "list": idlist, "cookices": cookices}]
        try:
            batchrun_list = getbatchrunList(idlist, exeuser, environment)
            # print("batchrun_list: ", batchrun_list)
        except Exception as e:
            result = {"code": -1, "info": "获取执行列表失败"}
            return JsonResponse(result)
        batchResult = batchstart.start_main(batchrun_list, environment, reflag, exeuser)
        # print batchResult
        if reportflag == True:
            report_localName = batchResult["reportPath"]
            report_runName = req["pmName"] # +"_" + batchResult["reportname"]
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


def getbatchrunList(idlist, exeuser, environment):
    batchrun_list = []
    try:
        projectname_list = projectList.objects.all().values("projectName").distinct()
    except Exception as e:
        print(u"error: %s" % str(e))
        return batchrun_list
    for pm in projectname_list:
        batchrun_dict = {}
        list = []
        for id in idlist:
            try:
                projectid = moduleList.objects.get(
                    id=int(apiInfoTable.objects.get(apiID=int(id)).owningListID)).owningListID
                projectname = projectList.objects.get(id=int(projectid)).projectName
                if str(projectname) == str(pm["projectName"]):
                    list.append(id)
            except Exception as e:
                print(u"error: %s" % str(e))
                continue
        if len(list) == 0:
            continue
        else:
            cookies = getCookies(environment, exeuser, pm["projectName"])
            batchrun_dict = {"sname": str(pm["projectName"]), "list": list, "cookices": cookies}
            batchrun_list.append(batchrun_dict)
    return batchrun_list


def getCookies(environment, exeuser, projectname):
    try:
        cookies = {}
        environment = str(environment).lower()
        cookies_list = userCookies.objects.filter(user=exeuser, cookiename="basecookie", evirment=environment, projectname=projectname).values("cookies")
        cookiesstr = cookies_list[0]["cookies"]
        if cookiesstr != "" and cookiesstr is not None:
            cookies = json.loads(cookiesstr)
    except Exception as e:
        cookies = None
    return cookies


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
            if query.headers != "{}" and query.headers != "" and query.headers is not None:
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
            if query.body != "{}" and query.body != "" and query.body is not None:
                bodydata = json.loads(query.body)
                stateflag = bodydata["showflag"]
                if stateflag == 3:
                    showbodyState = 3
                    for i in bodydata["datas"]:
                        body_dict = {}
                        body_dict["value"] = i["paramValue"]
                        body_list.append(body_dict)
                    json_dict["body"] = body_list
                    # json_dict["body"] = bodydata["datas"][0]["paramValue"]
                elif stateflag==1:
                    for i in bodydata["datas"]:
                        body_dict = {}
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
            json_dict["response"] = query.response
            listdata = moduleList.objects.get(id=int(query.owningListID))
            json_dict["moduleName"] = listdata.moduleName
            pid = listdata.owningListID
            json_dict["projectName"] = projectList.objects.get(id=int(pid)).projectName
            json_dict["host"] = batchUntils.getHost(int(query.host),environment)
            caseOwnID_list = []
            modulelist = moduleList.objects.filter(owningListID=int(pid))
            for module in modulelist:
                module_list.append(module.moduleName)
                caseOwnID_list.append(module.id)
            depend_caseList = getdependCaseList(caseOwnID_list, id)
            # print "*******modulelist*******", module_list
            json_dict["depend_list"] = depend_caseList
            json_dict["depend_data"] = query.depend_casedata
            json_dict["t_id"] = query.t_id
            json_dict["depend_caseId"] = query.depend_caseId
            if query.depend_caseId != "" and query.depend_caseId is not None:
                json_dict["dependCaseId_apiid"] = apiInfoTable.objects.get(t_id=query.depend_caseId).apiID  # dependCaseId_apiid表示tid不为空的用例所依赖用例的id
            else:
                json_dict["dependCaseId_apiid"] = 0
            result = {'code': 0, 'datas': json_dict, 'info': 'success',"module_list": module_list,"showbody":showbodyState}
    return JsonResponse(result)


def getdependCaseList(ownID_list,id):
    dependCaseList = []
    query = apiInfoTable.objects.filter(owningListID__in=ownID_list).values("apiID", "apiName")
    for item in query:
        if str(item["apiID"]) != str(id):
            dependCaseList.append(item)
    return dependCaseList


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
            json_dict["tid_apiName"] = apiInfoTable.objects.get(t_id=i.depend_caseId).apiName  #tid_id表示tid不为空的用例所依赖用例的id
        else:
            json_dict["tid_apiName"] = ""
        depend_casedata = i.depend_casedata
        json_dict["depend_data"] = depend_casedata
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
            id = int(request.GET["pid"])
            query = moduleList.objects.get(id=id)
            moduName = query.moduleName
            pid = query.owningListID
            projName = projectList.objects.get(id=int(pid)).projectName
            # print(id, projName, moduName)
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


def updataDatas(id, datas):
    checkresult = batchUntils.checkFormat(datas)
    # print("3...checkresult: ", checkresult)
    if checkresult["code"] == 0:
        updataData = checkresult["data"]
        # print("2...updataData: ",updataData)
        try:
            if updataData == "":
                apiInfoTable.objects.filter(apiID=id).update(depend_casedata=None)
            else:
                apiInfoTable.objects.filter(apiID=id).update(depend_casedata=updataData)
        except Exception as e:
            result = {"code": -1, "info": "updata failed"}
            return result
        result = {"code": 0, "info": "updata success"}
    else:
        result = {"code": -1, "info": "依赖数据格式有误"}
    return result


def updatedependcase(id, depend_id):
    apiID = int(id)
    dependID = int(depend_id)
    if dependID == 0:
        apiInfoTable.objects.filter(apiID=apiID).update(depend_caseId=None)
    else:
        # print("1: ", apiID, dependID)
        # 判断用例之间是否构成相互依赖
        flag = batchUntils.checkDepend(apiID, dependID)
        # print("2: ", flag)
        if flag == True:
            result = {"code": -1, "info": "所选接口已与当前用例建立依赖，请重新选择"}
            return result
        try:
            dependcaset_id = apiInfoTable.objects.get(apiID=dependID).t_id  # 查询到依赖用例的t_id
        except Exception as e:
            result = {"code": -1, "info": str(e)}
            return result
        if dependcaset_id == "" or dependcaset_id is None:
            t_id = "d" + str(dependID)
            try:
                apiInfoTable.objects.filter(apiID=dependID).update(t_id=t_id)
                apiInfoTable.objects.filter(apiID=apiID).update(depend_caseId=t_id)
            except Exception as e:
                result = {"code": -1, "info": "更新失败：" + str(e)}
                return result
        else:
            try:
                apiInfoTable.objects.filter(apiID=apiID).update(depend_caseId=dependcaset_id)
            except Exception as e:
                result = {"code": -1, "info": "更新失败：" + str(e)}
                return result
    result = {"code": 0, "info": "更新成功"}
    return result

def saveOrUpdateData(request):
    result = {}
    if request.method == 'POST':
        req = json.loads(request.body)["params"]
        id = int(req["apiid"])
        data = req["sendData"]
        apiName = data["apiName"]
        method = data["method"]
        host = data["host"]
        url = data["url"]
        if apiName == "" or host == "" or url == "":
            result = {"code": -1, "info": "名称、host、url不能为空"}
            return JsonResponse(result)
        dependcase_apiID = data["dependcase_apiID"]
        dependData = data["dependData"]
        header = data["header"]
        body_str = data["bodys"]
        cbody = body_str
        cheader = header
        if cbody != "" and cbody is not None:
            try:
                json.loads(cbody)
            except Exception as e:
                result = {"code": -1, "info": "body格式不正确"}
                return JsonResponse(result)
        if cheader != "" and cheader is not None:
            try:
                json.loads(cheader)
            except Exception as e:
                result = {"code": -1, "info": "header格式不正确"}
                return JsonResponse(result)
        if body_str != "" and body_str is not None and body_str != "{}":
            body = {"showflag": 3,
                    "datas": [{"paramValue": body_str}]
                    }
            body = json.dumps(body)
        else:
            body = "{}"
        if header == "" or header is None:
            header = "{}"
        assertinfo = data["assert"]
        environment = data["environment"]
        userName = data["user"]
        hostid = apiInfoTable.objects.get(apiID=id).host
        try:
            apiInfoTable.objects.filter(apiID=id).update(apiName=apiName, method=method, url=url, headers=header,
                                                         body=body, creator=userName, assertinfo=assertinfo)
            hostTags.objects.filter(id=int(hostid)).update(qa=host)
            batchUntils.getHost(hostid, environment)
        except Exception as e:
            result = {"code": -1, "info": "更新失败：" + str(e)}
            return JsonResponse(result)
        # 更新dependcase_id
        result = updatedependcase(id, dependcase_apiID)
        # 更新dependData
        result = updataDatas(id, dependData)
    return JsonResponse(result)
