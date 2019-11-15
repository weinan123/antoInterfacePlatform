import sendRequests
import json,requests
from jpype import *
import jpype
import multiprocessing
class getCookies3():
    typecookie1 = {
        "qa":["https://cxsit.yflife.app/v1/mma/connect/sso/login"],
        "stage":["https://cxsit.yflife.app/v1/mma/connect/sso/login"],
        "live":["https://cxsit.yflife.app/v1/mma/connect/sso/login"],
    }
    typecookie2 = {
        "qa": ["https://servicesit.yflife.app/v1/mma/connect/sso/login"],
        "stage": ["https://servicesit.yflife.app/v1/mma/connect/sso/login"],
        "live": ["https://servicesit.yflife.app/v1/mma/connect/sso/login"],
    }
    def __init__(self,evirment,username,password):
        self.username = username
        self.password = password
        self.evirment = evirment
    def getsalt(self):
        #url = "https://uc-qa.youyu.cn/v1/users/check"
        url = self.typecookie1.get(self.evirment)[0]
        body = {"type": "mobile", "value": self.username, "aver": 1}
        methods = "POST"
        headers = {"Content-Type": "application/json"}
        files = {}
        isRedirect = ""
        showflag = ""
        resp = sendRequests.sendRequest().sendRequest(methods,url,headers,body,files,isRedirect,showflag)
        datajson = resp.json()
        return datajson["data"]["uin"],datajson["data"]["loginid"],datajson["data"]["salt"]
    def getauth(self,q):
        jvmPath = ur"D:\jre_python\jre-8u231-windows-x64\jre1.8.0_231\bin\server\jvm.dll"
        jpype.startJVM(jvmPath,
                       "-Djava.class.path=C:\\Users\\nan.wei\\Desktop\\jiama\\SmartAuth.jar")
        HanLP = JClass('yflife.SmartAuth')
        auth = HanLP.getAuth()
        q.put(auth)
        jpype.shutdownJVM()
        return auth

    def servirce(self,cookieFlag):
        url = ""
        if int(cookieFlag==3):
            url = self.typecookie1.get(self.evirment)[0]
        elif int(cookieFlag==4):
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
        body = {"loginname":self.username,"logintype":2,"auth":auth,"value":self.password}
        methods = "POST"
        headers = {"Content-Type": "application/json"}
        files = {}
        isRedirect = ""
        showflag = ""
        resp = sendRequests.sendRequest().sendRequest(methods,url,headers,body,files,isRedirect,showflag)
        print resp.text
        cookies = requests.utils.dict_from_cookiejar(resp.cookies)
        return cookies
if __name__ == "__main__":
  cookiess = getCookies3("qa","27775411","test13579").servirce()
  print cookiess
