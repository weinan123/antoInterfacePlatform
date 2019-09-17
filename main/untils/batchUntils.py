# coding=utf-8
import datetime
import unittest
import sys,os,time
import ConfigParser
'''
读取配置文件数据方法
'''
def getconfig(model,model_case):
    data_file = r"D:\pycharm\youyu_auto\config\conf.ini"
    data = ConfigParser.RawConfigParser()
    data.read(data_file)
    config_data = data.get(model,model_case)
    return config_data
'''
格式化错误输出
'''
def getErrInfo(errInfo):
    return "%s" % (errInfo)
#日期格式化函数
'''
获取当前时间的格式化字符串
'''

def getNowStrftime():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def getNowStrftime2():
    return datetime.datetime.now().strftime("%Y%m%d%H%M%S")

def getNowDart():
    return time.strftime("%d/%m/%Y")

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
获取相对路径并拼接路径方法
'''
def getAbsPath(relativePath):
    curPath = os.path.abspath(os.path.dirname(__file__))
    rootPath = curPath[:curPath.find("youyu_auto\\") + len("youyu_auto\\")]
    # 拼接路径，拼接THIS_DIR+relativePath
    return os.path.join(rootPath, relativePath)
'''
查找文件，如果没有，则创建文件
'''
def create():
    t = time.strftime('%Y-%m-%d', time.localtime())  # 将指定格式的当前时间以字符串输出
    suffix = "result.html"
    newfile = getAbsPath("report")
    filepath = getAbsPath("report\\" + t + suffix)
    if not os.path.exists(newfile):
        f = open(filepath, 'w')
        print newfile
        f.close()
    else:
        print filepath + " already existed."
    return filepath