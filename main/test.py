from .models import *
def getchartData():
    data={}
    projectList = interfaceList.objects.filter().values("projectName").distinct()
    for i in range(0,len(projectList)):
        data["projectName"] = projectList[i]
        modelList = interfaceList.objects.filter(projectName=projectList[i]).values("moduleName")
        data["moduleName"]=[]
        data["moduleName"]=modelList
    print data
getchartData()