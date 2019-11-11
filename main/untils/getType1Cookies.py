import sendRequests
import json,requests
from jpype import *
import jpype
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
    def getauth(self):
        jvmPath = ur"D:\jre_python\jre-8u231-windows-x64\jre1.8.0_231\bin\server\jvm.dll"
        jpype.startJVM(jvmPath,
                       "-Djava.class.path=C:\\Users\\nan.wei\\Desktop\\jiama\\module-httpFunctionTest-0.0.1-SNAPSHOT.jar")
        HanLP = JClass('com.ruifusoft.wm.WmEncrypt')
        uin, loginid,salt = self.getsalt()
        print  uin, loginid,salt
        uin = str(uin)
        pwd = self.password
        salt = str(salt)
        auth = HanLP.getLoginAuth(uin, pwd, salt)
        jpype.shutdownJVM()
        return auth
    def servirce(self):
        #url = "https://sso-qa.youyu.cn/v1/services/login"
        url = self.typecookie1.get(self.evirment)[0]
        uin,loginid,salt = self.getsalt()
        auth = self.getauth()
        body = {"uin":uin,"loginid":loginid,"auth":auth,"autoLogin":False,"verification":{"verificationKey":self.username,"verificationCode":"1234","type":4}}
        methods = "POST"
        headers = {"Content-Type": "application/json"}
        files = {}
        isRedirect = ""
        showflag = ""
        resp = sendRequests.sendRequest().sendRequest(methods,url,headers,body,files,isRedirect,showflag)
        cookies = requests.utils.dict_from_cookiejar(resp.cookies)
        return cookies
if __name__ == "__main__":
    cookies = getCookies1("+8610111112276","1234qwer").servirce()
