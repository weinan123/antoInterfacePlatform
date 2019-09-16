# -*- coding: utf-8 -*-
from django.shortcuts import redirect
from toretrunData import toType
import time,os,sched,subprocess
def my_login(func):
    def inner(*args,**kwargs):
        login_user_id = args[0].session.get('username')
        print login_user_id
        if login_user_id is not None:
            return func(*args,**kwargs)
        else:
            return redirect('/login')
    return inner

def mul_bodyData(bodyinfor):
    body = {}
    files={}
    paramsData = bodyinfor["datas"]
    if bodyinfor["showflag"] == 3:
        body = paramsData[0]["paramValue"]
    else:
        for i in range(0,len(paramsData)):
            params_name = paramsData[i]["paramName"]
            params_value = paramsData[i]["paramValue"]
            params_type = paramsData[i]["paramType"]
            print params_name,params_value,params_type
            if(params_type=='file'):
                path = r'main/postfiles/%s' % bodyinfor[i]["paramValue"]
                if os.path.exists(path):
                    files = {'file':open(path, 'rb')}
                else:
                    files = {'file':""}
            else:
                getvalue = toType(params_type,params_value).toreturnType()
                print getvalue
                body[params_name] = getvalue
    print body,files
    return body,files
'''
#定制任务
schedule = sched.scheduler(time.time,time.sleep)
def perform_command(cmd,inc):
    schedule.enter(inc, 0, perform_command, (cmd, inc))
    os.system(cmd)
    print ('task')
def timming_exe(cmd,inc=60):
    schedule.enter(inc, 0, perform_command, (cmd, inc))
    schedule.run()
def runSched():
    cmd1 = "cd ../"
    cmd2 = "python runChartData.py "
    cmd = cmd1+ " && " + cmd2
    subprocess.Popen(cmd, shell=True)
    subprocess.call(cmd,shell=True)
'''
import time,os
def re_exe(cmd,inc = 60):
  while True:
      try:
          subprocess.Popen(cmd, shell=True)
          subprocess.call(cmd, shell=True)
          time.sleep(inc)
      except Exception as e:
          print e
def run():
    cmd1="cd\\"
    cmd2="d:"
    cmd3 = "cd D:/project/auto_interface/antoInterfacePlatform/main/common"
    cmd4 = "python runChartData.py "
    cmd = cmd1 + " && " + cmd2+ " && " + cmd3+ " && " + cmd4
    re_exe(cmd,5)

