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
        return datajson
    def scretData(self):
        datajson = self.getsalt()
        if datajson["code"]==0:
            salt = datajson['data']['uniKey']
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
            scretdata = {
                "code": 0,
                "msg": "获取加密信息失败",
                "timeStamp":timeStamp,
                "rand":rand,
                "sha2":sha2
            }
        else:
            scretdata = {
                "code": -1,
                "msg": "获取cookie失败",
                "error_msg": datajson["msg"]
            }
        return scretdata
    def getcookies(self):
        #timeStamp, rand, sha2 = self.scretData()
        scretdata = self.scretData()
        if scretdata["code"]== 0:
            timeStamp, rand, sha2 = scretdata["timeStamp"],scretdata["rand"],scretdata["sha2"]
            url = self.typecookie2.get(self.evirment)[1]
            body = {'account': self.username, 'info': sha2, 'rand': rand, 'timeStamp': timeStamp}
            methods = "POST"
            headers = {"Content-Type": "application/json"}
            files = {}
            isRedirect = ""
            showflag = ""
            resp = sendRequests.sendRequest().sendRequest(methods, url, headers, body, files, isRedirect, showflag)
            datajson1 = resp.json()
            print datajson1
            if datajson1["code"]==200:
                cookies = requests.utils.dict_from_cookiejar(resp.cookies)
                cookies["UID"] = datajson1["uid"]
                cookiedata = {
                    "code": 0,
                    "msg": "获取cookie成功",
                    "cookies": cookies,
                }
            else:
                cookiedata = {
                    "code": -2,
                    "msg": "获取cookie失败",
                    "error_msg": datajson1["msg"]
                }
        else:
            cookiedata = {
                "code": -1,
                "msg": "获取cookie失败",
                "error_msg": scretdata["msg"]
            }
        return cookiedata
if __name__ == "__main__":
    cookies = getCookies2("qa",'aa01','aa123456..').getcookies()
    print cookies
