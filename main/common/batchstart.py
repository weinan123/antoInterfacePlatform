# coding=utf-8
import unittest
from libs import HTMLTestRunner1
import batchUntils
from main.models import apiInfoTable
import time
import sys
reload(sys)
sys.setdefaultencoding('utf8')


class RunTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        print("batch run start....")

    def actions(self, arg1, arg2):
        # 获取元素的方式
        caseID = arg1
        state = False
        caseName = arg2
        print(u"\n用例名称:%s." % caseName)  # 报告输出中使用，请勿删除
        print(u"用例id:%s." % caseID)  # 报告输出中使用，请勿删除
        singleResult = self.singleRun(caseID)
        if singleResult["code"] == 0:
            state = True
            print (u"执行结果：case (%s:%s) 执行成功." % (caseID, caseName))
        else:
            state = False
            print(u"执行结果：case (%s:%s) 执行失败:%s" % (caseID, caseName, str(singleResult["datas"])))
        self.assertEqual(True, state)

    # 闭包函数
    @staticmethod
    def getTestFunc(arg1, arg2):
        def func(self):
            self.actions(arg1, arg2)
        return func

    @classmethod
    def tearDownClass(cls):
        print("batch run end....")

    def singleRun(self,caseID):
        id = caseID
        dtime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        respResult = batchUntils.getResp(id, dtime)
        code = respResult["code"]
        if code == 0:
            resp = respResult["response"]
            assertinfo = respResult["assert"]
        else:
            respinfo = respResult["info"]
            result = {"code": -1, "datas": respinfo}
            return result
        statusCode = resp.status_code
        text = resp.text
        responseText = text
        print u"返回数据：%s " % str(responseText).decode('raw_unicode_escape')
        if assertinfo == "":
            print(u"断言数据：空")
        else:
            print(u"断言数据：%s " % str(assertinfo).decode('raw_unicode_escape'))
        if assertinfo == "":
            datas = {"status_code": statusCode}
            if statusCode == 200:
                apiInfoTable.objects.filter(apiID=caseID).update(lastRunTime=dtime, lastRunResult=1, response=responseText)
                result = {"code": 0, "info": "run success", "datas": str(datas)}
            else:
                apiInfoTable.objects.filter(apiID=caseID).update(lastRunTime=dtime, lastRunResult=-1, response=responseText)
                result = {"code": 1, "info": "run fail", "datas": str(datas)}
        else:
            datas = {"status_code": statusCode, "responseText": str(text), "assert": assertinfo}
            if str(assertinfo) in str(text):
                apiInfoTable.objects.filter(apiID=caseID).update(lastRunTime=dtime, lastRunResult=1, response=responseText)
                result = {"code": 0, "info": "run success", "datas": str(datas)}
            else:
                apiInfoTable.objects.filter(apiID=caseID).update(lastRunTime=dtime, lastRunResult=-1, response=responseText)
                result = {"code": 1, "info": "run fail", "datas": str(datas)}
        return result

def _getTestcase(list):
    testlist = list
    for attr in dir(RunTest):
        if str(attr).startswith("test_func_"):
            delattr(RunTest, attr)
    for args in testlist:
        try:
            caseName = apiInfoTable.objects.get(apiID=args).apiName
        except Exception as e:
            print("用例ID:%s, 不存在，跳过执行..." % str(args))
            continue
        fun = RunTest.getTestFunc(args, caseName)
        setattr(RunTest, 'test_func_%s_%s' % (args, caseName), fun)


def start_main(list, reportflag, exeuser):
    _getTestcase(list)
    testSuite = batchUntils.getTestSuite(RunTest)
    # print("testSuite: %s" % str(testSuite))
    if reportflag == "Y":
        reportFile, pathName, reportname= batchUntils.create()
        fp = open(reportFile, "wb")
        runner = HTMLTestRunner1.HTMLTestRunner(stream=fp, title=u'测试报告', description=u'用例执行情况', tester=str(exeuser))
        result = runner.run(testSuite)
        fp.close()
        return {"reportPath": pathName, "reportname": reportname,"sNum": result.success_count, "fNum": result.failure_count,
                "eNum": result.error_count}
    else:
        runner = unittest.TextTestRunner()
        result = runner.run(testSuite)
        return {"sNum": testSuite.countTestCases() - len(result.errors) - len(result.failures),
                "fNum": len(result.failures),
                "eNum": len(result.errors)}
