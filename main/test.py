# -*- coding: UTF-8 -*-
import pymysql



host = "10.9.8.20"  # 数据库服务器名称或IP
user = "monitor"
password = "monitor123"
database = "monitor"
conn = pymysql.connect(host, user, password, database)
# 使用cursor()方法获取操作游标
cursor = conn.cursor()
#sql = "select lastRunResult from main_apiInfoTable where owningListID_id=2 "
sql= "select count(*),owningListID_id,lastRunResult from main_apiInfoTable where lastRunResult='None' group by owningListID_id "
cursor.execute(sql)
results = cursor.fetchall()
print results