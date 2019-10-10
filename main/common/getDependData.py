# -*- coding: utf-8 -*-

from main.models import reports,apiInfoTable,interfaceList
from main.untils.until import mul_bodyData
from main.untils import sendRequests
import authService
import json,time,re

def getdepands(depend_list, depend_data):
    datas = []
    dependCase = json.loads(depend_list)
    dependData = json.loads(depend_data)
    print(dependCase)
    print(dependData)
    for tid in dependCase:
        data_dict = {}
        query = apiInfoTable.objects.get(t_id=tid)
        methods = query.method
        send_url = query.url
        if methods == "" or send_url == "":
            result = {"code": -1, "datas": "参数不能为空"}
            return result
        headers = query.headers
        if headers != "":
            headers = json.loads(headers)
        bodyinfor = query.body
        if bodyinfor != "" or bodyinfor != "{}":
            bodyinfor = json.loads(bodyinfor)
        listid = query.owningListID
        querylist = interfaceList.objects.get(id=listid)
        host = querylist.host
        url = host + send_url
        # 处理数据类型的方法
        send_body, files = mul_bodyData(bodyinfor)
        isRedirect = query.isRedirect
        isScreat = query.isScreat
        if isScreat == False or isScreat == "":
            resp = sendRequests.sendRequest().sendRequest(methods, url, headers, send_body, files, isRedirect)
        # 加密执行
        else:
            key_id = query.key_id
            secret_key = query.secret_key
            credentials = authService.BceCredentials(key_id, secret_key)
            headers_data = {
                'Accept': 'text/html, */*; q=0.01',
                'X-Requested-With': 'XMLHttpRequest',
                'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2272.89 Safari/537.36'
            }
            headersOpt = {'X-Requested-With', 'User-Agent', 'Accept'}
            timestamp = int(time.time())
            Authorization = authService.simplify_sign(credentials, methods, send_url, headers_data, timestamp, 300,
                                                      headersOpt)
            resp = sendRequests.sendRequest().sendSecretRequest(key_id, secret_key, Authorization, methods, url,send_url, headers, send_body, files, isRedirect)
        print(resp.headers)
        print(resp.raw)
        print(resp.cookies)
        print(resp.text)
        key = dependData[tid]
        print(key)
        # 这里拿依赖的数据
        value = re.findall("'%s':'(.*?)'" % str(key), resp.text)
        if len(value) != 0:
            data_dict[tid] = value[0]
            datas.append(data_dict)
        print datas
    return datas
