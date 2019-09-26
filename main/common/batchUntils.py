# coding=utf-8
import datetime
import unittest
import sys,os,time

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
    print report_path, relpath
    return report_path, relpath
