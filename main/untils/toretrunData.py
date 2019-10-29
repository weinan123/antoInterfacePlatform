# -*- coding: utf-8 -*-
import sys,os
sys.path.append(r"D:\project\auto_interface\antoInterfacePlatform\main\toretrunData.py")
class toType():
    def __init__(self,type,data):
        self.type = type
        self.data = data
    def toreturnType(self):
        data_type = {
            "Text":self.toText,
            "file":self.toFile,
            "String":self.toString,
            "boolean":self.toBoolean,
            "null":self.toNull,
            "array":self.toArray,
            "number":self.toNumber,
            "object":self.toObject
        }
        return data_type.get(self.type)(self.data)
    def toText(self,data):
        return str(data)
    def toFile(self,data):
        pass
    def toString(self,data):
        return str(data)
    def toBoolean(self,data):
        if(data=="false"):
            return False
        elif(data=="ture"):
            return True
    def toNull(self,data):
        pass
    def toArray(self,data):
        return list(data)
    def toNumber(self,data):
        return int(data)
    def toObject(self,data):
        return dict(data)


