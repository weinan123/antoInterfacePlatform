# -*- coding: utf-8 -*-
from django.shortcuts import redirect
from toretrunData import toType
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
    for i in range(0,len(bodyinfor)):
        print bodyinfor[i]
        params_name = bodyinfor[i]["params_name"]
        params_value = bodyinfor[i]["params_value"]
        params_type = bodyinfor[i]["params_type"]
        print params_name,params_value,params_type
        getvalue = toType(params_type,params_value).toreturnType()
        print getvalue
        body[params_name] = getvalue
    print body
    return body

