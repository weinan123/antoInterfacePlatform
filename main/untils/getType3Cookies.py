# -*- coding: utf-8 -*-
import sendRequests
import json,requests
from jpype import *
import jpype,os
import multiprocessing
class getCookies3():
    typecookie1 = {
        "qa":["https://cxsit.yflife.app/v1/mma/connect/sso/login"],
        "stage":["https://cxsit.yflife.app/v1/mma/connect/sso/login"],
        "live":["https://cxsit.yflife.app/v1/mma/connect/sso/login"],
    }
    typecookie2 = {
        "qa": ["https://servicesit.yflife.app/v1/mma/smt/sso/login"],
        "stage": ["https://servicesit.yflife.app/v1/mma/smt/sso/login"],
        "live": ["https://servicesit.yflife.app/v1/mma/smt/sso/login"],
    }
    def __init__(self,evirment,username,password):
        self.username = username
        self.password = password
        self.evirment = evirment
    def getauth(self,q):
        #jvmPath = ur"D:\jre_python\jre-8u231-windows-x64\jre1.8.0_231\bin\server\jvm.dll"
        jvmPath = jpype.getDefaultJVMPath()
        path = "/dependJar/SmartAuth.jar"
        realpath = os.path.dirname(os.path.dirname(__file__)) + path
        print realpath
        jpype.startJVM(jvmPath,
                       "-Djava.class.path=%s"%(realpath))
        HanLP = JClass('yflife.SmartAuth')
        auth = HanLP.getAuth()
        q.put(auth)
        jpype.shutdownJVM()
        return auth

    def servirce(self,cookieFlag):
        url = ""
        if int(cookieFlag==4):
            url = self.typecookie1.get(self.evirment)[0]
        elif int(cookieFlag==3):
            url = self.typecookie2.get(self.evirment)[0]

        q = multiprocessing.Queue()
        p = multiprocessing.Process(target=self.getauth, args=[q])
        p.daemon = True
        p.start()
        a = q.get()
        print a
        p.terminate()
        auth = a
        print auth
        body = {}
        if(cookieFlag==4):
            body = {"loginname":self.username,"logintype":2,"auth":auth,"value":self.password}
        elif(cookieFlag==3):
            body = {"agentcode": self.username, "auth": auth, "agentpwd": self.password}
        methods = "POST"
        headers = {"Content-Type": "application/json"}
        files = {}
        isRedirect = ""
        showflag = ""
        resp = sendRequests.sendRequest().sendRequest(methods,url,headers,body,files,isRedirect,showflag)
        print resp.text
        datajson = resp.json()
        if datajson["code"] == 0:
            cookies = requests.utils.dict_from_cookiejar(resp.cookies)
            cookiedata = {
                "code": 0,
                "msg": "获取cookie成功",
                "cookies": cookies,
            }
        else:
            cookiedata = {
                "code": -2,
                "msg": "获取cookie失败",
                "error_msg": datajson["msg"]
            }
        return cookiedata
if __name__ == "__main__":
  cookiess = getCookies3("qa","87825","Test13579").servirce(3)
  print cookiess
