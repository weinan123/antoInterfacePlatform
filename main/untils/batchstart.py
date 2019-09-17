# coding=utf-8
import unittest
from until.openinit import get_driver
from until.autoFormAdv import AutoForm
from libs import HTMLTestRunner,sendMail
from until import untils
class RunTest(unittest.TestCase):
    # 类方法，cls为当前的类名
    @classmethod
    def setUpClass(cls):
        cls.bm = get_driver()
        cls.af = AutoForm(cls.bm)
        cls.filepath = untils.getAbsPath("testcases\\testcase.xlsx")
    def actions(self, arg1, arg2):
        # 获取元素的方式
        caseName = arg2
        res = self.af.runCase(self.filepath, caseName)
        state = True
        info = ""
        for i in range(0, res.__len__()):
            state = state and res.__getitem__(i).get("state")
            info = info + res.__getitem__(i).get("title") + ":" + \
                   res.__getitem__(i).get("info")
        print u"用例:" + arg1 + " " + u"用例方法:" + caseName
        print info
        self.assertEqual(True, state)
    # 闭包函数
    @staticmethod
    def getTestFunc(arg1,arg2):
        def func(self):
            self.actions(arg1,arg2)
        return func
    @classmethod
    def tearDownClass(cls):
        cls.bm = get_driver()
        cls.af = AutoForm(cls.bm)
        cls.af.quitDriver()

'''
    获取可执行的用例集并组装test方法
'''
def _getTestcase():
    filepath = untils.getAbsPath("testcases\\testcase.xlsx")
    print filepath
    testlist = AutoForm.getTestSuiteFromStdExcel(filepath)
    for args in testlist:
        fun = RunTest.getTestFunc(args["caseinfro"], args["casename"])
        setattr(RunTest, 'test_func_%s' % (args["casename"]), fun)
_getTestcase()

if __name__ == "__main__":
    testSuite = untils.getTestSuite(RunTest)
    print testSuite
    reportFile = untils.create()
    fp = file(reportFile, "wb")
    runner = HTMLTestRunner.HTMLTestRunner(stream=fp, title=u'测试报告', description=u'用例执行情况')
    runner.run(testSuite)
    #发送邮件报告
    #sendMail.sendemali(reportFile)

