# -*- coding: UTF-8 -*-
import pymysql
class getChartData():
    def __init__(self):
        host = "127.0.0.1"  # 数据库服务器名称或IP
        user = "root"
        password = ""
        database = "my_web"
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
        sql = " select id,owningListID,moduleName from main_modulelist "
        self.cursor.execute(sql)
        # 获取所有记录列表
        results = self.cursor.fetchall()
        for data in results:
            print data
            projetname = " select id,projectName from main_projectlist where id= %d" % (data[1])
            self.cursor.execute(projetname)
            projectinfor = self.cursor.fetchall()
            print projectinfor[0][1]
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
                #print result[0][0]
                self.updatedb(i["casetype"],result[0][0],projectinfor[0][1],data[2])

if __name__=='__main__':
    getChartData = getChartData()
    getChartData.nullmodel()

