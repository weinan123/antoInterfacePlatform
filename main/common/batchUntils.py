# coding=utf-8
import unittest
import sys,os
from main.models import apiInfoTable, projectList,hostTags
import time
import json
from main.untils.until import mul_bodyData
from main.untils import sendRequests
from main.common import authService,getDependData
import sys,re
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


'''
根据环境查询host，如果为空，则正则创建
'''
def getHost(id,environment):
    hostdict = hostTags.objects.filter(id=id).values()
    hostqa = hostdict[0]["qa"]
    hoststage = hostdict[0]["stage"]
    hostlive = hostdict[0]["live"]
    hostdev = hostdict[0]["dev"]
    match1 = re.search('qa', hostqa)
    match2 = re.search('dev', hostqa)
    match3 = re.search('stage', hostqa)
    host = ""
    if (match1 != None) or (match2 != None) or (match3 != None):
        if environment=="QA":
                hoststr = hostqa.replace('qa', str(environment).lower())
                hoststr = hoststr.replace('stage', str(environment).lower())
                hoststr = hoststr.replace('dev', str(environment).lower())
                hostTags.objects.filter(id=id).update(qa=hoststr)
                host = hostdict[0]["qa"]
        elif environment=="Stage" :
            if hoststage=="":
                hoststr = hostqa.replace("qa", str(environment).lower())
                hostTags.objects.filter(id=id).update(stage=hoststr)
            host = hostdict[0]["stage"]
        elif environment == "Live":
            if hostlive == "":
                hoststr = hostqa.replace("-qa", "")
                hostTags.objects.filter(id=id).update(live=hoststr)
            host = hostdict[0]["live"]
        elif environment=="Dev" :
            if hostdev=="":
                hoststr = hostqa.replace("qa", str(environment).lower())
                hostTags.objects.filter(id=id).update(dev=hoststr)
            host = hostdict[0]["dev"]
    else:
        hostTags.objects.filter(id=id).update(dev=hostqa,live=hostqa,stage=hostqa)
        host = hostdict[0][str(environment).lower()]
    return  host
'''执行用例'''
def getResp(id,environment, dtime):
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
        print(u"是否有关联：否")
    else:
        dependData_list = query.depend_casedata
        dependData = isDependency(depend_flag, dependData_list)
    listid = query.owningListID
    querylist = projectList.objects.get(id=listid)
    print("所属项目-模块：%s - %s" % (querylist.projectName, querylist.moduleName))
    print u"请求方法：%s" % (methods)
    host = getHost(int(query.host),environment)
    print host
    url = str(host) + str(send_url)
    print u"请求地址：%s" % (url)
    Cookie = ""
    # 处理数据类型的方法
    send_body, files, showflag = mul_bodyData(bodyinfor)
    # print json.dumps(dependData)
    if len(dependData) != 0:
        for dd in dependData:
            for key, value in dd.items():
                if key == "Cookie":
                    Cookie = value
                else:
                    send_body[key.decode('raw_unicode_escape')] = value
    print u"请求体：%s "% (str(send_body).decode('raw_unicode_escape'))
    isRedirect = query.isRedirect
    isScreat = query.isScreat
    key_id = query.key_id
    secret_key = query.secret_key
    timestamp = int(time.time())
    assertinfo = str(query.assertinfo.replace(" ", ""))
    dtime = dtime
    responseText = ""
    # 非加密执行接口
    if isScreat == False or isScreat == "":
        try:
            resp = sendRequests.sendRequest().sendRequest(methods, url, headers, send_body, files, isRedirect, showflag, Cookie)
        except Exception as e:
            infos = {"status_code": 400, "error": str(e)}
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
                                                                showflag, Cookie)
        except Exception as e:
            infos = {"status_code": 400, "error": str(e)}
            apiInfoTable.objects.filter(apiID=id).update(lastRunTime=dtime, lastRunResult=-1, response=responseText)
            result = {"code": -1, "info": "run error:" + str(infos)}
            return result
    result = {"code": 0, "info": "success", "response": resp, "assert": assertinfo}
    return result


def isDependency(depend_flag, depend_data):
    depend_caseid = depend_flag
    depend_data = depend_data
    print u"关联用例t_id：%s" % (depend_caseid)
    if depend_data != "" or depend_data != "[]":
        dependRes = getDependData.getdepands(depend_caseid, depend_data)
        if dependRes["code"] == 0:
            dependData = dependRes["dependdata"]
            print u"关联数据：%s" % (str(dependData).decode('raw_unicode_escape'))
        else:
            dependData = []
            print(u"关联数据：无")
    else:
        dependData = []
        print(u"关联数据：无")
    return dependData