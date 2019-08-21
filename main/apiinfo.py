# -*- coding: utf-8 -*-
import sys
reload(sys)
sys.setdefaultencoding('utf8')
from django.shortcuts import render
from apimodel.models import apiInfoTable, interfaceList
import time
import json
from django.http.response import JsonResponse


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