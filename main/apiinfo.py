# -*- coding: utf-8 -*-
import sys
reload(sys)
sys.setdefaultencoding('utf8')
from django.shortcuts import render
from models import apiInfoTable, interfaceList
import datetime
import json
from django.http.response import JsonResponse
import requests


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
        if i.lastRunResult is None:
            json_dict["lastrunrslt"] = 'null'
        else:
            json_dict["lastrunrslt"] = i.lastRunResult
        if i.lastRunTime is None:
            json_dict["lastruntime"] = 'null'
        else:
            json_dict["lastruntime"] = i.lastRunTime.strftime('%Y-%m-%d %H:%M:%S')
        json_dict["owing"] = i.creator
        json_dict["listid"] = i.owningListID.id
        json_dict["listname"] = i.owningListID.projectName
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
            'lastRunResult': None,
            'lastRunTime': None,
            'creator': user,
            'owningListID_id': listid
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
                print i['owningListID_id'],pid
                if str(i['owningListID_id']) == pid:
                    print "222222222222222222222222222222222"
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
                    json_dict["listid"] = i['owningListID_id']
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
            result = {'code':0,'data':json_list,'info':'success'}
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
        query = apiInfoTable.objects.get(apiID=id)
        print query
        result = runrequest(query,id)
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
    assertinfo = sqlquery.assertinfo
    if method == "" or url == "":
        result = {"code": -1, "datas": "参数不能为空"}
        return result
    else:
        if header == "" or header is None:
            headers = {}
        else:
            headers = json.loads(header)
        print headers
        if bodys == "" or bodys is None:
            bodys = {}
        else:
            bodys = json.loads(bodys)
        a = requests.request(method=method, url=url, headers=headers, data=bodys)
        print a
        print a.status_code
        print a.text
        text = a.text
        dtime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print dtime
        datas = {}
        if assertinfo == "":
            datas = {"status_code": a.status_code}
            if a.status_code == 200:
                apiInfoTable.objects.filter(apiID=id).update(lastRunTime=dtime, lastRunResult=True)
                result = {"code": 0, "info": "run success", "datas": str(datas)}
            else:
                apiInfoTable.objects.filter(apiID=id).update(lastRunTime=dtime, lastRunResult=False)
                result = {"code": 1, "info": "run fail", "datas": str(datas)}
        else:
            datas = {"status_code": a.status_code, "responseText": text, "assert": assertinfo}
            print assertinfo in text
            if a.status_code == 200 and assertinfo in text:
                    apiInfoTable.objects.filter(apiID=id).update(lastRunTime=dtime, lastRunResult=True)
                    result = {"code": 0, "info": "run success", "datas": str(datas)}
            else:
                apiInfoTable.objects.filter(apiID=id).update(lastRunTime=dtime, lastRunResult=False)
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
            content = ""
            showbodyState = 0
            body_list = []
            if query.headers:
                header_data = json.loads(query.headers)
                try:
                    print(str(header_data["Content-Type"]))
                    content = str(header_data["Content-Type"])
                except BaseException as e:
                    content = ""
                for k in header_data:
                    header_dict = {}
                    header_dict["type"] = k
                    header_dict["value"] = header_data[k]
                    header_list.append(header_dict)
                print header_list
                json_dict["header"] = header_list
            else:
                header_list.append({"type": "", "value": ""})
                json_dict["header"] = header_list
            print header_list
            if query.body:
                bodydata = json.loads(query.body)
                print("-----bodydata------", bodydata)
                if content == "text/plain":
                    showbodyState = 3
                    for i in bodydata:
                        body_dict = {}
                        print i
                        body_dict["value"] = i["params_value"]
                        body_list.append(body_dict)
                    json_dict["body"] = body_list
                elif content == "application/json":
                    for i in bodydata:
                        body_dict = {}
                        print i
                        body_dict["name"] = i["params_name"]
                        body_dict["type"] = i["params_type"]
                        body_dict["value"] = i["params_value"]
                        body_list.append(body_dict)
                    showbodyState = 1
                    json_dict["body"] = body_list
                elif content == "application/xml":
                    showbodyState = 2
                    for i in bodydata:
                        body_dict = {}
                        print i
                        body_dict["name"] = i["params_name"]
                        body_dict["type"] = i["params_type"]
                        body_dict["value"] = i["params_value"]
                        body_list.append(body_dict)
                    json_dict["body"] = body_list
                elif content == "multipart/form-data":
                    showbodyState = 0
                    for i in bodydata:
                        body_dict = {}
                        print i
                        body_dict["name"] = i["params_name"]
                        body_dict["type"] = i["params_type"]
                        body_dict["value"] = i["params_value"]
                        body_list.append(body_dict)
                    json_dict["body"] = body_list
                else:
                    showbodyState = 0
                    json_dict["body"] = []
            else:
                json_dict["body"] = []
            json_dict["url"] = query.url
            json_dict["assert"] = query.assertinfo
            json_dict["listid"] = query.owningListID.id
            json_dict["projectName"] = query.owningListID.projectName
            json_dict["moduleName"] = query.owningListID.moduleName
            modulelist = interfaceList.objects.filter().values("projectName", "moduleName").distinct()
            print modulelist
            for module in modulelist:
                if module["projectName"] == json_dict["projectName"]:
                    module_list.append(module["moduleName"])
            result = {'code': 0, 'datas': json_dict, 'info': 'success', "module_list": module_list,
                      "showbody": showbodyState}
    return JsonResponse(result)