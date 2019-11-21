# -*- coding: utf-8 -*-
import json
import random
import time,sendRequests
import requests
import hashlib
class getCookies2():
    typecookie2 = {
        "qa": ["http://wlb-cms-ui-qa.youyu.cn/v2/cms/account/permission/management/uniKey",
               "http://wlb-cms-ui-qa.youyu.cn/v2/cms/login/signin"],
        "stage": ["http://wlb-cms-ui-stage.youyu.cn/v2/cms/account/permission/management/uniKey",
               "http://wlb-cms-ui-stage.youyu.cn/v2/cms/login/signin"],
        "live": ["http://wlb-cms-ui.youyu.cn/v2/cms/account/permission/management/uniKey",
               "http://wlb-cms-ui.youyu.cn/v2/cms/login/signin"],
    }
    def __init__(self, evirment, username, password):
        self.username = username
        self.password = password
        self.evirment = evirment
    def getsalt(self):
        url = self.typecookie2.get(self.evirment)[0]
        body = {'account': self.username}
        methods = "POST"
        headers = {"Content-Type": "application/json"}
        files = {}
        isRedirect = ""
        showflag = ""
        resp = sendRequests.sendRequest().sendRequest(methods, url, headers, body, files, isRedirect, showflag)
        datajson = resp.json()
        salt = datajson['data']['uniKey']
        return salt
    def scretData(self):
        salt = self.getsalt()
        print salt,self.password
        sha1 = hashlib.sha256(bytes(self.password) + bytes(salt)).hexdigest()
        print(sha1)
        timeStamp = int(round(time.time() * 1000))  # 毫秒时间戳
        print(timeStamp)
        rand = ''.join(str(random.choice(range(10))) for _ in range(4))
        print(rand)

        sha2 = hashlib.sha256(
            bytes(self.username) + bytes(sha1) + bytes(str(timeStamp)) + bytes(rand)).hexdigest()
        print(sha2)
        return timeStamp,rand,sha2
    def getcookies(self):
        timeStamp, rand, sha2 = self.scretData()
        url = self.typecookie2.get(self.evirment)[1]
        body = {'account': self.username, 'info': sha2, 'rand': rand, 'timeStamp': timeStamp}
        methods = "POST"
        headers = {"Content-Type": "application/json"}
        files = {}
        isRedirect = ""
        showflag = ""
        resp = sendRequests.sendRequest().sendRequest(methods, url, headers, body, files, isRedirect, showflag)
        datajson = resp.json()
        print datajson
        cookies = requests.utils.dict_from_cookiejar(resp.cookies)
        cookies["UID"] = datajson["uid"]
        print cookies,datajson["code"]
        return cookies,datajson["code"]
if __name__ == "__main__":
    cookies = getCookies2("qa",'aa01','aa123456..').getcookies()
