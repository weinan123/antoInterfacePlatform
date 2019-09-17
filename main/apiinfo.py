# -*- coding: utf-8 -*-
from django.shortcuts import render
from models import apiInfoTable, interfaceList
import time
import json
from django.http.response import JsonResponse
import requests
from untils.until import mul_bodyData
from untils import sendRequests
from common import authService
import sys
reload(sys)
sys.setdefaultencoding('utf8')

def allinfo(request):
    proid = request.GET['pid']
    print("pid:%s" % proid)
    # 使用get方法只获取一条匹配的数据，若有多条会报错,有多条使用filter
    apilist = apiInfoTable.objects.filter(owningListID=proid)
    print("apilist:%s." % apilist)
    json_list = []
    for i in apilist:
        json_dict = {}
        json_dict["id"] = i.apiID
        json_dict["name"] = i.apiName
        if i.lastRunResult == 0:
            json_dict["lastrunrslt"] = 'null'
        else:
            json_dict["lastrunrslt"] = i.lastRunResult
        if i.lastRunTime is None:
            json_dict["lastruntime"] = 'null'
        else:
            json_dict["lastruntime"] = i.lastRunTime.strftime('%Y-%m-%d %H:%M:%S')
        json_dict["owing"] = i.creator
        json_dict["listid"] = i.owningListID
        #json_dict["listname"] = i.owningListID.projectName
        json_dict["method"] = i.method
        json_dict["url"] = i.url
        # data = json.dumps(json_dict)       #转化为json字符串
        json_list.append(json_dict)
    result = {
        'data': json_list,
        'code': 0,
        'info': 'success'
    }
    # return render(request, 'apiInfo.html', {'datas': data})
    return JsonResponse(result)


def allinfopage(request):
    return render(request, "apiInfo.html")


# def list(request):
#     list = interfaceList.objects.all()
#     return render(request, 'list.html', {'list': list})


def addApi(request):
    result = {}
    if request.method == 'POST':
        """ post获取不到前台传递过来的数据，原因是数据没有序列化，1.前台解决：使用URLSearchParams传递参数；后端解决（推荐）：request的json数据是封装在body中的，应该从body中获取"""
        req = json.loads(request.body)["params"]
        listid = req['listid']
        apiname = req['apiname']
        print apiname
        if (apiname == "") or (apiname is None):
            result = {'code': -2, 'info': '名称不能为空'}
            return JsonResponse(result)
        user = req['user']
        api_infos = {
            'apiName': apiname,
            'lastRunResult': 0,
            'lastRunTime': None,
            'creator': user,
            'owningListID': int(listid)
        }
        print(api_infos)
        try:
            s = apiInfoTable.objects.create(**api_infos)
            allinfo = apiInfoTable.objects.all()
            print(allinfo)
            s.save()
        except BaseException as e:
            print(" SQL Error: %s" % e)
            result = {'code':-1,'info':'sql error'}
            return JsonResponse(result)
        result = {'code':0, 'info':'insert success'}
    return JsonResponse(result)

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
            result = {'code':-2,'info':'no exist'}
    return JsonResponse(result)

def searchapi(request):
    result={}
    if request.method == 'GET':
        pid = request.GET['listid']
        sear = request.GET['searinfo']
        print("pid:%s,sear:%s" % (pid,sear))
        query = apiInfoTable.objects.filter(apiName__icontains=sear).values()
        print(query.values())
        if query != None:
            json_list = []
            for i in query:
                print i
                json_dict = {}
                print i['owningListID'],pid
                if str(i['owningListID']) == pid:
                    json_dict["id"] = i['apiID']
                    json_dict["name"] = i['apiName']
                    if i['lastRunResult'] is None:
                        json_dict["lastrunrslt"] = 'null'
                    else:
                        json_dict["lastrunrslt"] = i['lastRunResult']
                    if i['lastRunTime'] is None:
                        json_dict["lastruntime"] = 'null'
                    else:
                        json_dict["lastruntime"] = i['lastRunTime'].strftime('%Y-%m-%d %H:%M:%S')
                    json_dict["owing"] = i['creator']
                    json_dict["listid"] = i['owningListID']
                    json_list.append(json_dict)
                print json_list
            result = {
                'data': json_list,
                'code': 0,
                'info': 'success'
            }
    return JsonResponse(result)


def getlistpath(request):
    result={}
    if request.method == 'GET':
        lid = request.GET['id']
        try:
            query = interfaceList.objects.get(id=str(lid))
        except BaseException as e:
            print(" SQL Error: %s" % e)
            result = {'code': -1, 'info': 'sql error!'}
            return JsonResponse(result)
        if query != None:
            json_list = []
            json_dict = {}
            json_dict["id"] = query.id
            json_dict["projectName"] = query.projectName
            json_dict["moduleName"] = query.moduleName
            json_list.append(json_dict)
            print json_list
            result = {'code': 0, 'data': json_list, 'info': 'success'}
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
                    # ainfo.delete()
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
        # Authorization = data["Screatinfor"]["Screatinfor"]
        listid = query.owningListID
        querylist = interfaceList.objects.get(id=listid)
        host = querylist.host
        url = host + send_url
        # 处理数据类型的方法
        send_body, files = mul_bodyData(bodyinfor)
        print(send_body)
        isRedirect = query.isRedirect
        # isScreat = Screatinfor["isScreat"]
        isScreat = query.isScreat
        key_id = query.key_id
        secret_key = query.secret_key
        # key_id = Screatinfor["key_id"]
        # secret_key = Screatinfor["secret_key"].encode("utf-8")
        timestamp = int(time.time())
        # 非加密执行接口
        if isScreat == False or isScreat == "":
            resp = sendRequests.sendRequest().sendRequest(methods, url, headers, send_body, files, isRedirect)
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
            resp = sendRequests.sendRequest().sendSecretRequest(key_id, secret_key, Authorization, methods, url,send_url, headers, send_body, files, isRedirect)
        assertinfo = str(query.assertinfo)
        dtime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        if assertinfo == "":
            datas = {"status_code": resp.status_code}
            if resp.status_code == 200:
                apiInfoTable.objects.filter(apiID=id).update(lastRunTime=dtime, lastRunResult=1)
                result = {"code": 0, "info": "run success", "datas": str(datas)}
            else:
                apiInfoTable.objects.filter(apiID=id).update(lastRunTime=dtime, lastRunResult=-1)
                result = {"code": 1, "info": "run fail", "datas": str(datas)}
        else:
            datas = {"status_code": resp.status_code, "responseText": str(resp.text), "assert": assertinfo}
            if resp.status_code == 200 and assertinfo in str(resp.text):
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
        slist = {}
        print idlist
        for id in idlist:
            query = apiInfoTable.objects.get(apiID=id)
            sresult = runrequest(query, id)
            print sresult
            slist[id] = sresult
        result = {"code": 0, "info": "执行结束", "results": slist}
    return JsonResponse(result)


def runrequest(sqlquery, id):
    method = sqlquery.method
    url = sqlquery.url
    header = sqlquery.headers
    bodys = sqlquery.body
    assertinfo = str(sqlquery.assertinfo)
    bodys_data = {}
    if method == "" or url == "":
        result = {"code": -1, "datas": "参数不能为空"}
        return result
    else:
        if header == "{}" or header is None:
            headers = {}
        else:
            headers = json.loads(header)
        if bodys == "{}" or bodys is None:
            bodys_data = {}
        else:
            bodys = json.loads(bodys)
            stateflag = bodys["showflag"]
            if stateflag == 3:
                values = bodys["datas"][0]
                bodys_data = values["paramValue"]
            else:
                for i in bodys["datas"]:
                    bodys_data[i["paramName"]] = i["paramValue"]
        print("bodys_data:",bodys_data)
        a = requests.request(method=method, url=url, headers=headers, data=bodys_data, verify=False)
        print a.status_code
        text = str(a.text)
        dtime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        if assertinfo == "":
            datas = {"status_code": a.status_code}
            if a.status_code == 200:
                apiInfoTable.objects.filter(apiID=id).update(lastRunTime=dtime, lastRunResult=1)
                result = {"code": 0, "info": "run success", "datas": str(datas)}
            else:
                apiInfoTable.objects.filter(apiID=id).update(lastRunTime=dtime, lastRunResult=-1)
                result = {"code": 1, "info": "run fail", "datas": str(datas)}
        else:
            datas = {"status_code": a.status_code, "responseText": text, "assert": assertinfo}
            print assertinfo in text
            if a.status_code == 200 and assertinfo in text:
                    apiInfoTable.objects.filter(apiID=id).update(lastRunTime=dtime, lastRunResult=1)
                    result = {"code": 0, "info": "run success", "datas": str(datas)}
            else:
                apiInfoTable.objects.filter(apiID=id).update(lastRunTime=dtime, lastRunResult=-1)
                result = {"code": 1, "info": "run fail", "datas": str(datas)}
        return result


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
