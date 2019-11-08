import sendRequests
import json
from jpype import *
import jpype
class getCookies():
    def __init__(self):
        pass
    def getsalt(self):
        url = "https://uc-qa.youyu.cn/v1/users/check"
        body = {"type": "mobile", "value": "+8610111112236", "aver": 1}
        methods = "POST"
        headers = {"Content-Type": "application/json"}
        files = {}
        isRedirect = ""
        showflag = ""
        resp = sendRequests.sendRequest().sendRequest(methods,url,headers,body,files,isRedirect,showflag)
        datajson =  resp.json()
        return datajson["data"]["uin"],datajson["data"]["loginid"],datajson["data"]["salt"]
    def getauth(self):
        jvmPath = ur"D:\jre_python\jre-8u231-windows-x64\jre1.8.0_231\bin\server\jvm.dll"
        jpype.startJVM(jvmPath,
                       "-Djava.class.path=C:\\Users\\nan.wei\\Desktop\\jiama\\module-httpFunctionTest-0.0.1-SNAPSHOT.jar")
        HanLP = JClass('com.ruifusoft.wm.WmEncrypt')
        uin, loginid,salt = self.getsalt()
        print  uin, loginid,salt
        uin = str(uin)
        pwd = "1234qwer"
        salt = str(salt)
        sss = HanLP.getLoginAuth(uin, pwd, salt)
        print sss
        jpype.shutdownJVM()
        return sss
    def servirce(self):
        url = "https://sso-qa.youyu.cn/v1/services/login"
        uin,loginid,salt = self.getsalt()
        print uin,loginid,salt
        auth = self.getauth()
        print auth
        body = {"uin":uin,"loginid":loginid,"auth":auth,"autoLogin":False,"verification":{"verificationKey":"+8610111112236","verificationCode":"1234","type":4}}
        methods = "POST"
        headers = {"Content-Type": "application/json"}
        files = {}
        isRedirect = ""
        showflag = ""
        resp = sendRequests.sendRequest().sendRequest(methods,url,headers,body,files,isRedirect,showflag)
        print resp.cookies
        datajson =  resp.json()
        print datajson
if __name__ == "__main__":
    getCookies().servirce()
