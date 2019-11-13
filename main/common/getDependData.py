# -*- coding: utf-8 -*-

from main.models import reports,apiInfoTable,projectList
from main.untils.until import mul_bodyData
from main.untils import sendRequests
import authService, batchUntils
import json,time,re


def getdepands(depend_caseid, depend_data, environment):
    dependCase = str(depend_caseid)
    dependDataKeys = json.loads(depend_data)
    try:
        query = apiInfoTable.objects.get(t_id=dependCase)
    except Exception as e:
        result = {"code": -1, "info": "依赖用例不存在"}
        return result
    # 判断是否有关联用例
    depend_flag = query.depend_caseId
    dependData = {}
    if depend_flag == "" or depend_flag is None:
        print(u"接口%s是否有关联：否" % dependCase)
    else:
        dependData_list = query.depend_casedata
        dependData = batchUntils.isDependency(depend_flag, dependData_list, environment)
    methods = query.method
    send_url = batchUntils.replaceParam(dependData, query.url)
    host = batchUntils.getHost(int(query.host), environment)
    host = batchUntils.replaceParam(dependData, host)
    if methods == "" or send_url == "" or host == "":
        result = {"code": -1, "info": "相关参数不能为空"}
        return result
    headers = batchUntils.replaceParam(dependData, query.headers)
    if headers != "":
        headers = json.loads(headers)
    bodyinfor = batchUntils.replaceParam(dependData, query.body)
    showflag = ""
    if bodyinfor != "" and str(bodyinfor) != "{}":
        bodyinfor = json.loads(bodyinfor)
        showflag = bodyinfor["showflag"]
    listid = query.owningListID
    querylist = projectList.objects.get(id=listid)
    url = str(host) + str(send_url)
    # 处理数据类型的方法
    send_body, files, showflag1 = mul_bodyData(bodyinfor)
    isRedirect = query.isRedirect
    isScreat = query.isScreat
    Cookie = ""
    # # 写入获取的依赖数据
    # if len(dependData) != 0:
    #     for dd in dependData:
    #         for key, value in dd.items():
    #             if key == "Cookie":
    #                 Cookie = value
    #             else:
    #                 send_body[key.decode('raw_unicode_escape')] = value
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
    data_dict = {}
    for k in dependDataKeys:
        responseText = json.loads(resp.text)
        value = getdependValue(k, responseText)
        data_dict = dict(data_dict, **value)
    result = {"code": 0, "info": "success", "dependdata": data_dict}
    return result

def getdependValue(k, respText):
    k_key = k.split("=")[0]
    keyv = k.split("=")[1]
    keyv = keyv.replace("$", "respText")
    keyv1 = keyv.split(".")
    aa = ""
    for i in range(len(keyv1)):
        if i == 0:
            aa = keyv1[0]
        elif str(keyv1[i]).find("[") != -1:
            inx = str(keyv1[i]).split("[")
            aa = aa + '["' + inx[0] + '"]' + '[' + inx[1]
        else:
            aa = aa + '["' + keyv1[i] + '"]'
    try:
        value = {k_key: eval(aa)}
    except Exception as e:
        value = {k_key: ""}
    return value
