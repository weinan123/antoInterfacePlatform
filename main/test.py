from .models import *
def getchartData(request):
    dataList=[]
    projectList = interfaceList.objects.filter().values("projectName").distinct()
    for i in range(0,len(projectList)):
        data = {}
        data["projectName"] = projectList[i]["projectName"]
        modelList = interfaceList.objects.filter(projectName=projectList[i]["projectName"]).values("moduleName")
        data["moduleName"] = []
        for j in modelList:
            data["moduleName"].append(j)
            pid = interfaceList.objects.get(projectName=projectList[i]["projectName"],moduleName =j["moduleName"]).id
            print pid
            allcase = apiInfoTable.objects.filter(apiID=pid).count()
            caseSuccess = apiInfoTable.objects.filter(apiID=pid,lastRunResult=True).count()
            caseFail = apiInfoTable.objects.filter(apiID=pid, lastRunResult=False).count()
            caseNull = apiInfoTable.objects.filter(apiID=pid, lastRunResult=None).count()
            j["allcase"] = allcase
            j["caseSuccess"] = caseSuccess
            j["caseFail"] = caseFail
            j["caseNull"] = caseNull
        dataList.append(data)
    returndata = {
        "code":0,
        "data":dataList
    }
    return JsonResponse(returndata, safe=False)