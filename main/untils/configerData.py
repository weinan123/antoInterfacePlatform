# -*- coding: utf-8 -*-
import ConfigParser,os
'''
处理配置文件的函数
'''
class configerData():
    def __init__(self):
        self.conf = ConfigParser.ConfigParser()
        curpath = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
        print curpath
        self.iniFileUrl = curpath+"/configerdatas/config_data"
        print self.iniFileUrl
        try:
            self.conf.read(self.iniFileUrl)
        except Exception as e:
            print e
    def saveData(self,reqdata):
        print reqdata
        print reqdata.items
        print self.conf.sections()
        for key,value in reqdata.items():
            print key,value
            self.conf.set("configerinfor",key,(value))
        self.conf.write(open(self.iniFileUrl, "w"))

    def getData(self):
        alldata = self.conf.items("configerinfor")
        return alldata
    def getItemData(self,option):
        itemData = self.conf.get("configerinfor",option)
        return itemData
if __name__ == "__main__":
    datas = {
        "eviorment":"qa",
        "runcase":[1,2.34],
        "sendlist":[u"weinann".encode("raw_unicode_escape"),"hahhaha","shihshis"]
    }
    s = configerData()
    s.saveData(datas)
    data = s.getData()[3][1]
    print data