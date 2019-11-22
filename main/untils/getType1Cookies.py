# -*- coding: utf-8 -*-
import sendRequests
import json,requests
import multiprocessing
from jpype import *
import jpype,os
class getCookies1():
    typecookie1 = {
        "qa":["https://uc-qa.youyu.cn/v1/users/check","https://sso-qa.youyu.cn/v1/services/login"],
        "stage":["https://uc-stage.youyu.cn/v1/users/check","https://sso-stage.youyu.cn/v1/services/login"],
        "live":["https://uc.youyu.cn/v1/users/check","https://sso.youyu.cn/v1/services/login"],
    }
    def __init__(self, evirment,username,password):
        self.username = username
        self.password = password
        self.evirment = evirment
    def getsalt(self):
        url = self.typecookie1.get(self.evirment)[0]
        body = {"type": "mobile", "value": self.username, "aver": 1}
        methods = "POST"
        headers = {"Content-Type": "application/json"}
        files = {}
        isRedirect = ""
        showflag = ""
        resp = sendRequests.sendRequest().sendRequest(methods,url,headers,body,files,isRedirect,showflag)
        datajson = resp.json()
        print datajson
        return datajson
        '''
        if(datajson["code"]==0):
            print datajson
            return datajson["data"]["uin"],datajson["data"]["loginid"],datajson["data"]["salt"]
        else:
            return datajson["code"],datajson["msg"]
        '''
    def getauth(self,q,uin,pwd,salt):
        #uin, loginid, salt = self.getsalt()
        #print  uin, loginid, salt
        uin = str(uin)
        #pwd = self.password
        salt = str(salt)
        jvmPath = jpype.getDefaultJVMPath()
        path = "\dependJar\module-httpFunctionTest-0.0.1-SNAPSHOT.jar"
        realpath = os.path.dirname(os.path.dirname(__file__)) + path
        print realpath
        jpype.startJVM(jvmPath,
                       "-Djava.class.path=%s" % (realpath))
        HanLP = JClass('com.ruifusoft.wm.WmEncrypt')

        auth = HanLP.getLoginAuth(uin, pwd, salt)
        q.put(auth)
        jpype.shutdownJVM()
        return auth
    def servirce(self):
        #url = "https://sso-qa.youyu.cn/v1/services/login"
        url = self.typecookie1.get(self.evirment)[1]
        #uin,loginid,salt = self.getsalt()
        datajson = self.getsalt()
        if datajson["code"] == 0:
            uin, loginid, salt = datajson["data"]["uin"],datajson["data"]["loginid"],datajson["data"]["salt"]
            q = multiprocessing.Queue()
            p = multiprocessing.Process(target=self.getauth,args=[q,uin,self.password,salt])
            p.daemon = True
            p.start()
            a = q.get()
            print a
            p.terminate()
            auth = a
            print auth
            body = {"uin":uin,"loginid":loginid,"auth":auth,"autoLogin":True,"verification":{"verificationKey":self.username,
                                                                                             "verificationCode":"1234","type":4}}
            methods = "POST"
            headers = {"Content-Type": "application/json"}
            files = {}
            isRedirect = ""
            showflag = ""
            resp = sendRequests.sendRequest().sendRequest(methods,url,headers,body,files,isRedirect,showflag)
            datajson1 = resp.json()
            if datajson1["code"] ==0:
                print datajson1
                cookies = requests.utils.dict_from_cookiejar(resp.cookies)
                cookiedata = {
                    "code": 0,
                    "msg": "获取cookie成功",
                    "cookies":cookies,
                }
            else:
                cookiedata = {
                    "code": -2,
                    "msg": "获取cookie失败",
                    "error_msg": datajson1["msg"]
                }
        else:
            cookiedata = {
                "code":-1,
                "msg":"获取cookie失败",
                "error_msg":datajson["msg"]
            }
        return cookiedata
if __name__ == "__main__":
    cookies = getCookies1("live","+8618740394057","wonder5566").servirce()
    print cookies

