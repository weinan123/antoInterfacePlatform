# coding=utf-8
import unittest
import sys,os
from main.models import apiInfoTable, interfaceList
import time
import json
from main.untils.until import mul_bodyData
from main.untils import sendRequests
from main.common import authService,getDependData
import sys
reload(sys)
sys.setdefaultencoding('utf8')


'''
获取测试套件
'''
# 获取TestSuite
def getTestSuite(*classes):
    valid_types = (unittest.TestSuite, unittest.TestCase)
    suite = unittest.TestSuite()
    for cls in classes:
        if isinstance(cls, str):
            if cls in sys.modules:
                suite.addTest(unittest.findTestCases(sys.modules[cls]))
            else:
                raise ValueError("str arguments must be keys in sys.modules")
        elif isinstance(cls, valid_types):
            suite.addTest(cls)
        else:
            suite.addTest(unittest.makeSuite(cls))
    return suite


'''
查找文件，如果没有，则创建文件
'''
def create():
    t = time.strftime("%Y-%m-%d-%H_%M_%S", time.localtime(time.time()))  # 将指定格式的当前时间以字符串输出
    suffix = "_result.html"
    relpath = t + suffix
    report_path = os.path.dirname(os.path.dirname(__file__)) + "\\report\\" + relpath
    reportname = t
    return report_path, relpath, reportname


'''执行用例'''
def getResp(id, dtime):
    try:
        query = apiInfoTable.objects.get(apiID=id)
    except Exception as e:
        result = {"code": -1, "info": "执行用例不存在，" + str(e)}
        return result
    methods = query.method
    send_url = query.url
    if methods == "" or send_url == "":
        result = {"code": -1, "info": "参数不能为空"}
        return result
    headers = query.headers
    if headers != "":
        headers = json.loads(headers)
    bodyinfor = query.body
    showflag = ""
    if bodyinfor != "" and str(bodyinfor) != "{}":
        bodyinfor = json.loads(bodyinfor)
        showflag = bodyinfor["showflag"]
    # 判断是否有关联用例
    depend_flag = query.depend_caseId
    dependData = []
    if depend_flag == "" or depend_flag is None:
        print(u"是否关联：否")
    else:
        depend_list = json.loads(depend_flag)
        depend_data = query.depend_casedata
        print u"关联用例集：%s" % (depend_list)
        if depend_data != "" or depend_data != "{}":
            dependData = getDependData.getdepands(depend_list, depend_data)
            print u"关联数据：%s" % (dependData)
        else:
            print(u"关联数据：无")
    listid = query.owningListID
    querylist = interfaceList.objects.get(id=listid)
    print("所属项目-模块：%s - %s" % (querylist.projectName, querylist.moduleName))
    print u"请求方法：%s" % (methods)
    host = query.host
    url = str(host) + str(send_url)
    print u"请求地址：%s" % (url)
    # 处理数据类型的方法
    send_body, files, showflag = mul_bodyData(bodyinfor)
    if len(dependData) != 0:
        for dd in dependData:
            send_body[dd.keys()[0]] = dd.values()[0]
    print(u"请求体：%s ", send_body)
    isRedirect = query.isRedirect
    isScreat = query.isScreat
    key_id = query.key_id
    secret_key = query.secret_key
    timestamp = int(time.time())
    assertinfo = str(query.assertinfo)
    dtime = dtime
    responseText = ""
    # 非加密执行接口
    if isScreat == False or isScreat == "":
        try:
            resp = sendRequests.sendRequest().sendRequest(methods, url, headers, send_body, files, isRedirect, showflag)
        except Exception as e:
            infos = {"status_code": -999, "error": str(e)}
            apiInfoTable.objects.filter(apiID=id).update(lastRunTime=dtime, lastRunResult=-1, response=responseText)
            result = {"code": -1, "info": "run error:" + str(infos)}
            return result
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
            resp = sendRequests.sendRequest().sendSecretRequest(key_id, secret_key, Authorization, methods, url,
                                                                send_url, headers, send_body, files, isRedirect,
                                                                showflag)
        except Exception as e:
            infos = {"status_code": -999, "error": str(e)}
            apiInfoTable.objects.filter(apiID=id).update(lastRunTime=dtime, lastRunResult=-1, response=responseText)
            result = {"code": -1, "info": "run error:" + str(infos)}
            return result
    result = {"code": 0, "info": "success", "response": resp, "assert": assertinfo}
    return result
