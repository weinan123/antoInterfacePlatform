# -*- coding: utf-8 -*-

from main.models import reports,apiInfoTable,interfaceList
from main.untils.until import mul_bodyData
from main.untils import sendRequests
import authService, batchUntils
import json,time,re

def getdepands(depend_caseid, depend_data):
    dpdatas = []
    dependCase = str(depend_caseid)
    dependDataKeys = json.loads(depend_data)
    try:
        query = apiInfoTable.objects.get(t_id=dependCase)
    except Exception as e:
        result = {"code": -1, "info": "依赖用例不存在"}
        return result
    methods = query.method
    send_url = query.url
    host = query.host
    if methods == "" or send_url == "" or host == "":
        result = {"code": -1, "info": "相关参数不能为空"}
        return result
    headers = query.headers
    if headers != "":
        headers = json.loads(headers)
    bodyinfor = query.body
    showflag = ""
    if bodyinfor != "" and str(bodyinfor) != "{}":
        bodyinfor = json.loads(bodyinfor)
        showflag = bodyinfor["showflag"]
    listid = query.owningListID
    querylist = interfaceList.objects.get(id=listid)
    url = str(host) + str(send_url)
    # 处理数据类型的方法
    send_body, files, showflag1 = mul_bodyData(bodyinfor)
    isRedirect = query.isRedirect
    isScreat = query.isScreat
    Cookie = ""
    # 判断是否有关联用例
    depend_flag = query.depend_caseId
    dependData = []
    if depend_flag == "" or depend_flag is None:
        print(u"接口%s是否有关联：否" % dependCase)
    else:
        dependData_list = query.depend_casedata
        dependData = batchUntils.isDependency(depend_flag, dependData_list)
    # 写入获取的依赖数据
    if len(dependData) != 0:
        for dd in dependData:
            for key, value in dd.items():
                if key == "Cookie":
                    Cookie = value
                else:
                    send_body[key.decode('raw_unicode_escape')] = value
    if isScreat == False or isScreat == "":
        try:
            resp = sendRequests.sendRequest().sendRequest(methods, url, headers, send_body, files, isRedirect, showflag, Cookie)
            # print(u"依赖接口返回信息： %s " % str(resp.text).decode('raw_unicode_escape'))
            print(u"依赖接口返回信息： %s " % re.sub(r'(\\u[\s\S]{4})', lambda x: x.group(1).encode("utf-8").decode("unicode-escape"),
                   str(resp.text)))
        except Exception as e:
            result = {"code": -1, "info": "error"}
            return result
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
        try:
            Authorization = authService.simplify_sign(credentials, methods, send_url, headers_data, timestamp, 300,
                                                      headersOpt)
            resp = sendRequests.sendRequest().sendSecretRequest(key_id, secret_key, Authorization, methods, url,send_url
                                                                , headers, send_body, files, isRedirect, showflag, Cookie)
            print(u"依赖接口返回信息： %s " % str(resp.text).decode('raw_unicode_escape'))
        except Exception as e:
            result = {"code": -1, "info": "error"}
            return result
    # 获取对应的值
    for k in dependDataKeys:
        data_dict = {}
        keyv = k
        if keyv == "Cookie":
            responseCookice = resp.cookies
            print(u"依赖接口的Cookie信息： %s", str(responseCookice))
            value = responseCookice.get_dict()
            data_dict[keyv] = value
            dpdatas.append(data_dict)
        else:
            value = ""
            responseText = json.loads(resp.text)
            if "dict" in str(type(responseText["data"])):
                for v in responseText["data"]:
                    if keyv == v:
                        value = responseText[k][v]
                        break
            else:
                for v in responseText["data"]:
                    for j in v:
                        if keyv == j:
                            value = v[j]
                            break
                    if value != "":
                        break
            data_dict[keyv] = value
            dpdatas.append(data_dict)
    result = {"code": 0, "info": "success", "dependdata": dpdatas}
    return result
