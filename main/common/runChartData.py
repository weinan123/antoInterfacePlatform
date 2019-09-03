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
    def runDb(self,casetype,sql):
        try:
           # 执行SQL语句
           self.cursor.execute(sql)
           # 获取所有记录列表
           results = self.cursor.fetchall()
           for data in results:
               queryproject = "select projectName,moduleName from main_interfaceList where id= %d" % (data[1])
               self.cursor.execute(queryproject)
               # 获取所有记录列表
               projectList = self.cursor.fetchall()
               casevalue = data[0]
               projectName = projectList[0][0]
               moduleName = projectList[0][1]
               print projectName,moduleName
               self.updatedb(casetype,casevalue,projectName,moduleName)
           print results
           # 关闭数据库连接
           #self.conn.close()
        except Exception as e:
           print e
    def updatedb(self,casetype,casevalue,projectName,moduleName):
        if (casetype=="allcase"):
            updataCount = " update main_countCase set allcaseNum=%d where (projectName='%s' and moduleName='%s')" % (casevalue,projectName,moduleName)
            self.cursor.execute(updataCount)
            self.conn.commit()
        elif(casetype=="passcase"):
            updataCount = " update main_countCase set passcaseNum=%d where (projectName='%s' and moduleName='%s')" % (
            casevalue, projectName, moduleName)
            self.cursor.execute(updataCount)
            self.conn.commit()
        elif(casetype=="failcase"):
            updataCount = " update main_countCase set failcaseNum=%d where (projectName='%s' and moduleName='%s')" % (
            casevalue, projectName, moduleName)
            self.cursor.execute(updataCount)
            self.conn.commit()
        elif(casetype=="nullcase"):
            updataCount = " update main_countCase set blockvaseNum=%d where (projectName='%s' and moduleName='%s')" % (
            casevalue, projectName, moduleName)
            self.cursor.execute(updataCount)
            self.conn.commit()
if __name__=='__main__':
    sqlList = [
        {"casetype":"allcase",
         "sql":"select count(*),owningListID from main_apiInfoTable group by owningListID"},
        {"casetype": "passcase",
         "sql": "select count(*),owningListID,lastRunResult from main_apiInfoTable where lastRunResult=1 group by owningListID " },
        {"casetype": "failcase",
         "sql": "select count(*),owningListID,lastRunResult from main_apiInfoTable where lastRunResult=-1 group by owningListID "},
        {"casetype": "nullcase",
         "sql": "select count(*),owningListID,lastRunResult from main_apiInfoTable where lastRunResult=0 group by owningListID "}
    ]
    getChartData = getChartData()
    for i in range(0,len(sqlList)):
        casetype=sqlList[i]["casetype"]
        sql = sqlList[i]["sql"]
        getChartData.runDb(casetype,sql)