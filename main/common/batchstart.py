# coding=utf-8
import unittest
from libs import HTMLTestRunner,sendMail
import batchUntils
from main.models import apiInfoTable,interfaceList
from main.untils import until,sendRequests
from main.common import authService, getDependData
import time
import json


class RunTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        print("batch run start....")

    def actions(self, arg1):
        # 获取元素的方式
        caseID = arg1
        state = False
        try:
            caseName = apiInfoTable.objects.get(apiID=caseID).apiName
        except Exception as e:
            print("caseid:%s is not exist or run error." % caseID)
        else:
            print("caseName:%s." % caseName)  # 报告输出中使用，请勿删除
            singleResult = self.singleRun(caseID)
            if singleResult["code"] == 0:
                state = True
                print("case %s is run success." % caseID)
            else:
                state = False
                print("case %s is run fail.%s" % (caseID, str(singleResult["datas"])))
            self.assertEqual(True, state)


    # 闭包函数
    @staticmethod
    def getTestFunc(arg1):
        def func(self):
            self.actions(arg1)
        return func

    @classmethod
    def tearDownClass(cls):
        print("batch run end....")

    def singleRun(self,caseID):
        try:
            query = apiInfoTable.objects.get(apiID=caseID)
        except Exception as e:
            result = {"code": -2, "datas": "执行用例失败，" + str(e)}
            return result
        methods = query.method
        send_url = query.url
        if methods == "" or send_url == "":
            result = {"code": -1, "datas": "methods和url参数不能为空"}
            return result
        headers = query.headers
        if headers != "":
            headers = json.loads(headers)
        bodyinfor = query.body
        if bodyinfor != "" or bodyinfor != "{}":
            bodyinfor = json.loads(bodyinfor)

        # 判断是否有关联用例
        depend_flag = query.depend_caseId
        dependData = []
        if depend_flag == "" or depend_flag is None:
            print("not depend")
        else:
            depend_list = depend_flag
            depend_data = query.depend_casedata
            if depend_data != "" or depend_data != "{}":
                dependData = getDependData.getdepands(depend_list, depend_data)
            else:
                print("depend data is None.")

        listid = query.owningListID
        querylist = interfaceList.objects.get(id=listid)
        host = querylist.host
        url = host + send_url
        # 处理数据类型的方法
        send_body, files = until.mul_bodyData(bodyinfor)
        isRedirect = query.isRedirect
        isScreat = query.isScreat
        key_id = query.key_id
        secret_key = query.secret_key
        timestamp = int(time.time())
        assertinfo = str(query.assertinfo)
        dtime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        resp = ''
        # 非加密执行接口
        if isScreat == False or isScreat == "":
            try:
                resp = sendRequests.sendRequest().sendRequest(methods, url, headers, send_body, files, isRedirect)
            except Exception as e:
                datas = {"status_code": -999,"error": str(e)}
                apiInfoTable.objects.filter(apiID=caseID).update(lastRunTime=dtime, lastRunResult=-1)
                result = {"code": -1, "info": "run error", "datas": str(datas)}
                return result
        # 加密执行
        else:
            credentials = authService.BceCredentials(key_id, secret_key)
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
                                                                send_url, headers, send_body, files, isRedirect)
            except Exception as e:
                datas = {"status_code": -999,"error": str(e)}
                apiInfoTable.objects.filter(apiID=caseID).update(lastRunTime=dtime, lastRunResult=-1)
                result = {"code": -1, "info": "run error", "datas": str(datas)}
                return result
        try:
            statusCode = resp.status_code
            text = resp.text
        except AttributeError as e:
            result = {"code": -1, "info": "run error", "datas": str(e)}
            return result
        if assertinfo == "":
            datas = {"status_code": statusCode}
            if statusCode == 200:
                apiInfoTable.objects.filter(apiID=caseID).update(lastRunTime=dtime, lastRunResult=1)
                result = {"code": 0, "info": "run success", "datas": str(datas)}
            else:
                apiInfoTable.objects.filter(apiID=caseID).update(lastRunTime=dtime, lastRunResult=-1)
                result = {"code": 1, "info": "run fail", "datas": str(datas)}
        else:
            datas = {"status_code": statusCode, "responseText": str(text), "assert": assertinfo}
            if str(assertinfo) in str(text):
                apiInfoTable.objects.filter(apiID=caseID).update(lastRunTime=dtime, lastRunResult=1)
                result = {"code": 0, "info": "run success", "datas": str(datas)}
            else:
                apiInfoTable.objects.filter(apiID=caseID).update(lastRunTime=dtime, lastRunResult=-1)
                result = {"code": 1, "info": "run fail", "datas": str(datas)}
        return result

def _getTestcase(list):
    testlist = list
    for args in testlist:
        fun = RunTest.getTestFunc(args)
        setattr(RunTest, 'test_func_%s' % (args), fun)


def start_main(list, reportflag):
    _getTestcase(list)
    testSuite = batchUntils.getTestSuite(RunTest)
    if reportflag == "Y":
        reportFile, pathName, reportname= batchUntils.create()
        fp = file(reportFile, "wb")
        runner = HTMLTestRunner.HTMLTestRunner(stream=fp, title=u'测试报告', description=u'用例执行情况')
        result = runner.run(testSuite)
        return {"reportPath": pathName, "reportname": reportname,"sNum": result.success_count, "fNum": result.failure_count,
                "eNum": result.error_count}
    else:
        runner = unittest.TextTestRunner()
        result = runner.run(testSuite)
        return result
