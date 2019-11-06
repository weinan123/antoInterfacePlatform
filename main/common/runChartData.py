# -*- coding: UTF-8 -*-
import pymysql
class getChartData():
    def __init__(self):
        host = "10.9.8.20"  # 数据库服务器名称或IP
        user = "monitor"
        password = "monitor123"
        database = "monitor"
        conn = pymysql.connect(host, user, password, database)
        # 使用cursor()方法获取操作游标
        cursor = conn.cursor()
        self.cursor = cursor
        self.conn = conn
    def updatedb(self,casetype,casevalue,projectName,moduleName):
        print casetype, casevalue, projectName, moduleName
        if (casetype=="allcase"):
            updataCount = " update main_countCase set allcaseNum=%d  where (projectName='%s' and moduleName='%s')" % (casevalue,projectName,moduleName)
            self.cursor.execute(updataCount)
            self.conn.commit()
        elif(casetype=="passcase"):
            updataCount = " update main_countCase set passcaseNum=%d  where (projectName='%s' and moduleName='%s')" % (
            casevalue, projectName, moduleName)
            self.cursor.execute(updataCount)
            self.conn.commit()
        elif(casetype=="failcase"):
            updataCount = " update main_countCase set failcaseNum=%d  where (projectName='%s' and moduleName='%s')" % (
            casevalue, projectName, moduleName)
            self.cursor.execute(updataCount)
            self.conn.commit()
        elif(casetype=="nullcase"):
            updataCount = " update main_countCase set blockvaseNum=%d where (projectName='%s' and moduleName='%s')" % (
            casevalue, projectName, moduleName)
            self.cursor.execute(updataCount)
            self.conn.commit()
    def nullmodel(self):
        sql = " select id,projectName,moduleName from main_projectList "
        self.cursor.execute(sql)
        # 获取所有记录列表
        results = self.cursor.fetchall()
        for data in results:
            if data[2]=="":
                continue
            else:
                sqlList = [
                    {"casetype": "allcase",
                     "sql": "select COUNT(*)  from main_apiInfoTable where owningListID= %d" % (data[0])},
                    {"casetype": "passcase",
                     "sql": "select COUNT(*)  from main_apiInfoTable where owningListID= %d and  lastRunResult=1" % (data[0])},
                    {"casetype": "failcase",
                     "sql": "select COUNT(*)  from main_apiInfoTable where owningListID= %d and lastRunResult=-1 " % (data[0])},
                    {"casetype": "nullcase",
                     "sql": "select COUNT(*)  from main_apiInfoTable where owningListID= %d and lastRunResult=0" % (data[0])}
                ]
                for i in sqlList:
                    self.cursor.execute(i["sql"])
                    # 获取所有记录列表
                    result = self.cursor.fetchall()
                    print result[0][0]
                    self.updatedb(i["casetype"],result[0][0],data[1],data[2])
if __name__=='__main__':
    getChartData = getChartData()
    getChartData.nullmodel()

