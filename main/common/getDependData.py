# -*- coding: utf-8 -*-

from main.models import reports,apiInfoTable,projectList
from main.untils.until import mul_bodyData
from main.untils import sendRequests
import authService, batchUntils
import json,time,re


def getdepands(depend_caseid, depend_data, environment, Cookie):
    dependCase = str(depend_caseid)
    dependDataKeys = (str(depend_data).replace(" ", "")).split(",")
    # print("dependDataKeys list: %s " % str(dependDataKeys))
    try:
        query = apiInfoTable.objects.get(t_id=dependCase)
    except Exception as e:
        result = {"code": -1, "info": "依赖用例不存在"}
        return result
    # 判断是否有关联用例
    depend_flag = query.depend_caseId
    dependData_str = query.depend_casedata
    dependData = {}
    if depend_flag == "" or depend_flag is None:
        print(u"依赖接口%s是否有关联接口：否" % dependCase)
        if dependData_str == "" or dependData_str is None:
            print(u"依赖接口是否有自定义参数：否")
        else:
            defindData = batchUntils.getDefindData(dependData_str)
            dependData = defindData
            print(u"依赖接口自定义参数：%s" % str(dependData))
    else:
        dependData = batchUntils.isDependency(depend_flag, dependData_str, environment, Cookie)
    methods = query.method
    send_url = batchUntils.replaceStrParam(dependData, query.url)
    host = batchUntils.getHost(int(query.host), environment)
    host = batchUntils.replaceStrParam(dependData, host)
    if methods == "" or send_url == "" or host == "":
        result = {"code": -1, "info": "相关参数不能为空"}
        return result
    # headers = query.headers
    # # print("headers: ", headers)
    # headers_dict = {}
    # if headers != "" and headers is not None and str(headers) != "{}":
    #     headers_dict = batchUntils.replaceParam(dependData, json.loads(headers))
    # bodyinfor = query.body
    # if bodyinfor != "" and str(bodyinfor) != "{}" and bodyinfor is not None:
    #     bodyinfor = json.loads(bodyinfor)
    # listid = query.owningListID
    # querylist = projectList.objects.get(id=listid)
    headers = batchUntils.replaceStrParam(dependData, str(query.headers))
    bodyinfor = batchUntils.replaceStrParam(dependData, str(query.body))
    headers_dict = {}
    if headers != "" and headers is not None and str(headers) != "{}":
        headers_dict = json.loads(headers)
    if bodyinfor != "" and str(bodyinfor) != "{}" and bodyinfor is not None:
        bodyinfor = json.loads(bodyinfor)
    url = str(host) + str(send_url)
    # 处理数据类型的方法
    send_body, files, showflag = mul_bodyData(bodyinfor)
    send_body_dict = {}
    if len(send_body) != 0:
        send_body_dict = send_body
    isRedirect = query.isRedirect
    isScreat = query.isScreat
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
            resp = sendRequests.sendRequest().sendRequest(methods, url, headers_dict, send_body_dict, files, isRedirect, showflag, Cookie)
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
                                                                , headers_dict, send_body_dict, files, isRedirect, showflag, Cookie)
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
    if keyv.find("$") == -1:
        value = {k_key: keyv}
    else:
        try:
            keyv = keyv.replace("$", "respText.")
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
            value = {k_key: eval(aa)}
        except Exception as e:
            value = {k_key: ""}
    return value
