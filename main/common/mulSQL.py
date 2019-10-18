# -*- coding: UTF-8 -*-
import pymysql
class mulSql():
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
    def insertData(self,sql):
        try:
            self.cursor.execute(sql)
            self.conn.commit()
        except Exception as e:
            print e

            #self.conn.rollback()
        self.conn.close()
    def selectData(self,sql):
        try:
            self.cursor.execute(sql)
            result = self.cursor.fetchone()
            return result
        except Exception as e:
            print e

            #self.conn.rollback()
        self.conn.close()

