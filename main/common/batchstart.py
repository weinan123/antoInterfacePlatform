# coding=utf-8
import unittest
from libs import HTMLTestRunner1
import batchUntils
from main.models import apiInfoTable
import time, re
import sys
reload(sys)
sys.setdefaultencoding('utf8')


@classmethod
def setUp(self):
    print(u"开始执行....")


def actions(self, arg1, arg2, environment, cookices):
    # 获取元素的方式
    caseID = arg1
    state = False
    caseName = arg2
    print(u"\n用例名称:%s." % caseName)  # 报告输出中使用，请勿删除
    print(u"用例id:%s." % caseID)  # 报告输出中使用，请勿删除
    singleResult = self.singleRun(caseID, environment, cookices)
    if singleResult["code"] == 0:
        state = True
        print (u"执行结果：case (%s:%s) 执行成功." % (caseID, caseName))
    else:
        state = False
        print(u"执行结果：case (%s:%s) 执行失败:%s" % (caseID, caseName, str(singleResult["datas"])))
    self.assertEqual(True, state)


# 闭包函数
@staticmethod
def getTestFunc(arg1, arg2, environment, cookices):
    def func(self):
        self.actions(arg1, arg2, environment, cookices)
    return func


def tearDown(self):
    print(u"执行结束....")


def singleRun(self, caseID, environment, cookices):
    id = caseID
    dtime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    respResult = batchUntils.getResp(id, environment, dtime, cookices)
    code = respResult["code"]
    if code == 0:
        resp = respResult["response"]
        assertinfo = respResult["assert"]
    else:
        respinfo = respResult["info"]
        result = {"code": -1, "datas": respinfo}
        return result
    statusCode = resp.status_code
    print(u"接口返回状态码：%s" % str(resp.status_code))
    text = resp.text
    responseText = text
    # print u"返回数据：%s " % str(responseText).decode('raw_unicode_escape')
    print u"返回数据：%s " % re.sub(r'(\\u[\s\S]{4})', lambda x: x.group(1).encode("utf-8").decode("unicode-escape"),
                               str(responseText))
    if assertinfo == "":
        print(u"断言数据：空")
    else:
        print(u"断言数据：%s " % str(assertinfo).decode('raw_unicode_escape'))
    if assertinfo == "":
        datas = {"status_code": statusCode}
        if str(statusCode).startswith("2"):
            apiInfoTable.objects.filter(apiID=caseID).update(lastRunTime=dtime, lastRunResult=1, response=responseText)
            result = {"code": 0, "info": "run success", "datas": str(datas)}
        else:
            apiInfoTable.objects.filter(apiID=caseID).update(lastRunTime=dtime, lastRunResult=-1, response=responseText)
            result = {"code": 1, "info": "run fail", "datas": str(datas)}
    else:
        datas = {"status_code": statusCode, "responseText": str(text), "assert": assertinfo}
        assertResult = batchUntils.checkAssertinfo(str(assertinfo), str(text))
        if assertResult:
            apiInfoTable.objects.filter(apiID=caseID).update(lastRunTime=dtime, lastRunResult=1, response=responseText)
            result = {"code": 0, "info": "run success", "datas": str(datas)}
        else:
            apiInfoTable.objects.filter(apiID=caseID).update(lastRunTime=dtime, lastRunResult=-1, response=responseText)
            result = {"code": 1, "info": "run fail", "datas": str(datas)}
    return result


def _getTestcase(list, classname, environment, cookices):
    testlist = list
    # for attr in dir(classname):
    #     if str(attr).startswith("test_func_"):
    #         delattr(classname, attr)
    for args in testlist:
        try:
            caseName = apiInfoTable.objects.get(apiID=args).apiName
        except Exception as e:
            print("用例ID:%s, 不存在，跳过执行...,报错：%s" % (str(args), str(e)))
            continue
        fun = classname.getTestFunc(args, caseName, environment, cookices)
        setattr(classname, 'test_func_%s_%s' % (args, caseName), fun)


def start_main(batchrun_list, environment, reportflag, exeuser):
    classList = createClass(batchrun_list, environment)
    suite = unittest.TestSuite()
    for caseclass in classList:
        tests = unittest.defaultTestLoader.loadTestsFromTestCase(caseclass)
        suite.addTests(tests)
    # testSuite = batchUntils.getTestSuite(RunTest)
    # print("testSuite: %s" % str(testSuite))
    if reportflag == "Y":
        reportFile, pathName, reportname= batchUntils.create()
        fp = open(reportFile, "wb")
        runner = HTMLTestRunner1.HTMLTestRunner(stream=fp, title=u'测试报告', description=u'用例执行情况', tester=str(exeuser),environment=str(environment))
        result = runner.run(suite)
        fp.close()
        return {"reportPath": pathName, "reportname": reportname, "sNum": result.success_count, "fNum": result.failure_count,
                "eNum": result.error_count}
    else:
        if len(batchrun_list) == 0:
            runner = unittest.TextTestRunner()
            result = runner.run(suite)
            return {"sNum": suite.countTestCases() - len(result.errors) - len(result.failures),
                    "fNum": len(result.failures),
                    "eNum": len(result.errors)}
        else:
            return {"sNum": 0,
                    "fNum": 0,
                    "eNum": 0}


def createClass(batchrun_list, environment):
    args = batchrun_list
    classList = []
    for i in args:
        classname = i["sname"]
        Class = type(classname, (unittest.TestCase,),
                     {"setUp": setUp, "actions": actions, "tearDown": tearDown, "getTestFunc": getTestFunc, "singleRun": singleRun})
        classList.append(Class)
        list = i["list"]
        try:
            sCookice = i["cookices"]
        except Exception as e:
            sCookice = None
        _getTestcase(list, Class, environment, sCookice)
        # testSuite = unittest.TestSuite()
        # # testSuite.addTest(unittest.makeSuite(Class))
        # # testSuite = getTestSuite(Class)
        # print classList
    return classList