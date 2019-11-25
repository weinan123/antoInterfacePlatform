# -*- coding: utf-8 -*-
import xlrd
from django.shortcuts import render, redirect
import json, time
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse, FileResponse
from main.models import *
from forms import UserForm, projectForm, firstProjectForm
from common import mulExcel
from untils import until
from common.batchUntils import checkFormat


def addProjectList(request):
    result = {
        'code': -1,
        'info': '未知错误！'
    }
    if request.method == 'POST':
        # 接受request.POST参数构造form类的实例
        form = projectForm(request.POST)
        # 验证数据是否合法
        if form.is_valid():
            # 处理form.cleaned_data中的数据
            # ...
            # 重定向到一个新的URL
            # if ():
            #     return
            dtime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
            resp2 = projectList.objects.filter(projectName=form.cleaned_data['projectName']).values("id")
            owningListID = resp2[0]['id']
            if (moduleList.objects.filter(owningListID=owningListID,
                                          moduleName=form.cleaned_data['moduleName']).count() == 0):
                inter = moduleList.objects.create(owningListID=owningListID,
                                                  moduleName=form.cleaned_data['moduleName'])
                counttable = countCase.objects.create(projectName=form.cleaned_data['projectName'],
                                                      moduleName=form.cleaned_data['moduleName'], )
                counttable.save()
                inter.save()
                moduleList.objects.filter(owningListID=owningListID,
                                          moduleName=form.cleaned_data['moduleName']).update(
                    updateTime=dtime,
                    createTime=dtime)
                code = 0
                info = '新建成功！'
                result = {
                    'code': code,
                    'info': info
                }
            else:
                code = -1
                info = '同一项目下不可包含相同名称的模块！'
                result = {
                    'code': code,
                    'info': info
                }
        else:
            result = {
                'code': -1,
                'info': '数据格式不正确！'
            }

    return JsonResponse(result, safe=False)


def addProject(request):
    result = {
        'code': -1,
        'info': '未知错误！'
    }
    if request.method == 'POST':
        # 接受request.POST参数构造form类的实例
        form = firstProjectForm(request.POST)
        # 验证数据是否合法
        if form.is_valid():
            # 处理form.cleaned_data中的数据
            # ...
            # 重定向到一个新的URL
            # if ():
            #     return
            dtime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
            if (projectList.objects.filter(projectName=form.cleaned_data['projectName']).count() == 0):
                inter = projectList.objects.create(projectName=form.cleaned_data['projectName'],
                                                   cookieFlag=form.cleaned_data['cookieFlag'])
                inter.save()
                scheduledata = schedule.objects.create(projectname=form.cleaned_data['projectName'])
                scheduledata.save()
                projectList.objects.filter(projectName=form.cleaned_data['projectName']).update(
                    updateTime=dtime,
                    createTime=dtime)
                code = 0
                info = '新建成功！'
                result = {
                    'code': code,
                    'info': info
                }
            else:
                code = -1
                info = '项目名称不可重复！'
                result = {
                    'code': code,
                    'info': info
                }
        else:
            result = {
                'code': -1,
                'info': '数据格式不正确！'
            }

    return JsonResponse(result, safe=False)


def projectListInfo(request):
    result = {
        'code': -1,
        'info': '调用的方法错误，请使用GET方法查询！'
    }
    if request.method == 'GET':
        projectName = request.GET.get('projectName')
        resp2 = projectList.objects.filter(projectName=projectName).values("id")
        owningListID = resp2[0]['id']
        resp = moduleList.objects.filter(owningListID=owningListID).values("id", "moduleName",
                                                                           "updateTime",
                                                                           "createTime")
        respList = list(resp)
        user = request.session.get('username')
        resp2 = users.objects.filter(username=user).values("batch_check", "batch_del", "batch_run")
        batch_check = resp2[0]['batch_check']
        batch_del = resp2[0]['batch_del']
        batch_run = resp2[0]['batch_run']
        permit = {
            'batch_check': batch_check,
            'batch_del': batch_del,
            'batch_run': batch_run
        }
        for i in range(len(respList)):
            respList[i]['projectName'] = projectName
            respList[i]['updateTime'] = str(respList[i]['updateTime']).split('.')[0]
            respList[i]['createTime'] = str(respList[i]['createTime']).split('.')[0]
            CaseInfo = countCase.objects.filter(projectName=projectName,
                                                moduleName=respList[i]['moduleName']).values(
                "allcaseNum",
                "passcaseNum",
                "failcaseNum",
                "blockvaseNum")
            if (CaseInfo.count() == 0):
                allcaseNum = 0
                passcaseNum = 0
                failcaseNum = 0
                blockcaseNum = 0
            else:
                if (not CaseInfo[0]['allcaseNum']):
                    allcaseNum = 0
                else:
                    allcaseNum = CaseInfo[0]['allcaseNum']
                if (not CaseInfo[0]['passcaseNum']):
                    passcaseNum = 0
                else:
                    passcaseNum = CaseInfo[0]['passcaseNum']

                if (not CaseInfo[0]['failcaseNum']):
                    failcaseNum = 0
                else:
                    failcaseNum = CaseInfo[0]['failcaseNum']
                if (not CaseInfo[0]['blockvaseNum']):
                    blockcaseNum = 0
                else:
                    blockcaseNum = CaseInfo[0]['blockvaseNum']
            respList[i]['allcaseNum'] = allcaseNum
            respList[i]['passcaseNum'] = passcaseNum
            respList[i]['failcaseNum'] = failcaseNum
            respList[i]['blockcaseNum'] = blockcaseNum
        result = {
            'permit': permit,
            'data': respList,
            'code': 0,
            'info': 'success'
        }
        #
        # allList = projectList.objects.all()
        # json_list = []
        # for i in allList:
        #     json_dict = {}
        #     json_dict["id"] = i.id
        #     json_dict["projectName"] = i.projectName
        #     json_dict["updateTime"] = i.updateTime.strftime('%Y-%m-%d %H:%M:%S')
        #     json_dict["createTime"] = i.createTime.strftime('%Y-%m-%d %H:%M:%S')
        #     json_dict["host"] = i.host
        #     json_dict["moduleName"] = i.moduleName
        #     json_list.append(json_dict)
        # result = {
        #     'data': json_list,
        #     'code': 0,
        #     'info': 'success'
        # }
    return JsonResponse(result, safe=False)


def firstProjectListInfo(request):
    result = {
        'code': -1,
        'info': '调用的方法错误，请使用GET方法查询！'
    }
    if request.method == 'GET':
        resp = projectList.objects.values("id", "projectName", "createTime", "updateTime")
        json_list = []
        respList = list(resp)
        for i in range(len(respList)):
            json_dict = {}
            projectName = respList[i]['projectName']
            createTime = str(respList[i]['createTime']).split('.')[0]
            updateTime = str(respList[i]['updateTime']).split('.')[0]
            owningListID = respList[i]['id']
            totalModule = moduleList.objects.filter(owningListID=owningListID).count()
            if (moduleList.objects.filter(owningListID=owningListID).count() > 0):
                updateTime = str(
                    moduleList.objects.filter(owningListID=owningListID).order_by('-updateTime').values(
                        "updateTime")[
                        0][
                        'updateTime']).split('.')[0]
            json_dict["projectName"] = projectName
            json_dict["createTime"] = createTime
            json_dict["updateTime"] = updateTime
            json_dict["totalModule"] = totalModule
            json_list.append(json_dict)
        result = {
            'data': json_list,
            'code': 0,
            'info': 'success'
        }
    return JsonResponse(result, safe=False)


def projectListView(request):
    # form = projectForm()
    # return render(request, 'projectList.html', {'form': form})
    return render(request, 'projectList.html')


def firstProjectList(request):
    return render(request, 'firstProjectList.html')


def download(request):
    file = open('main/postfiles/template.xlsx', 'rb')
    response = FileResponse(file)
    response['Content-Type'] = 'application/octet-stream'
    response['Content-Disposition'] = 'attachment;filename="接口模板.xlsx"'
    return response


def uploadCase(request):
    if request.method == 'GET':
        id = request.GET["modelid"]
        modelname = moduleList.objects.filter(id=id).values_list("moduleName")[0][0]
        print modelname
        caseList = apiInfoTable.objects.filter(owningListID=id).values()
        filepath = r"main/postfiles/template.xls"
        saveexcel = mulExcel.mulExcel(filepath, 0)
        newWorkbook, newsheet = saveexcel.createExcel()
        if (len(caseList) > 0):
            for i in range(0, len(caseList)):
                casename = caseList[i]["apiName"]
                method = caseList[i]["method"]
                host = caseList[i]["host"]
                realhost = hostTags.objects.filter(id=int(host)).values_list("qa")[0][0]
                url = caseList[i]["url"]
                headers = caseList[i]["headers"]
                body = caseList[i]["body"]
                bodys, files, showflag = until.mul_bodyData(json.loads(body))
                t_id = caseList[i]["t_id"]
                depend_caseId = caseList[i]["depend_caseId"]
                depend_casedata = caseList[i]["depend_casedata"]
                assertinfo = caseList[i]["assertinfo"]
                isScreat = caseList[i]["isScreat"]
                isRedirect = caseList[i]["isRedirect"]
                caselist = [casename, method, realhost, url, headers, json.dumps(bodys), t_id,
                            depend_caseId,
                            depend_casedata, assertinfo, isScreat, isRedirect]
                print caselist
                saveexcel.writeRowData(newWorkbook, newsheet, i + 8, caselist, modelname)
        else:
            caselist = []
            print caseList
            filepath = r"main/postfiles/template.xls"
            saveexcel = mulExcel.mulExcel(filepath, 0)
            saveexcel.writeRowData(newWorkbook, newsheet, 8, caselist, modelname)
        file = open('main/postfiles/' + modelname + '.xls', 'rb')
        print file
        print modelname
        response = FileResponse(file)
        response['Content-Type'] = 'application/octet-stream'
        response['Content-Disposition'] = 'attachment;filename="%s.xls"' % (modelname)
        return response


def projectView(request):
    if request.method == 'GET':
        id = request.GET.get('id')
        # print id
    return HttpResponseRedirect('/projectList/')


def projectDelete(request):
    if request.method == 'GET':
        id = request.GET.get('id')
        if (apiInfoTable.objects.filter(owningListID=id).count() == 0):
            resp2 = moduleList.objects.filter(id=id).values("owningListID", "moduleName")
            projectID = resp2[0]['owningListID']
            moduleName = resp2[0]['moduleName']
            resp = projectList.objects.filter(id=projectID).values("projectName")
            projectName = resp[0]['projectName']
            countCase.objects.filter(projectName=projectName, moduleName=moduleName).delete()
            moduleList.objects.filter(id=id).delete()
            code = 0
            info = '删除成功！'
        else:
            code = -1
            info = '所选模块中还存在用例，请先删除用例，再删除模块！'
        result = {
            'code': code,
            'info': info
        }
    return JsonResponse(result, safe=False)


def firstProjectDelete(request):
    if request.method == 'GET':
        projectName = request.GET.get('projectName')
        if (projectList.objects.filter(projectName=projectName).count() == 1):
            countCase.objects.filter(projectName=projectName).delete()
            projectList.objects.filter(projectName=projectName).delete()
            schedule.objects.filter(projectname=projectName).delete()
            code = 0
            info = '删除成功！'
        else:
            code = -1
            info = '所选项目中还存在模块，请先删除模块，再删除项目！'
        result = {
            'code': code,
            'info': info
        }
    return JsonResponse(result, safe=False)


def projectBatchDelete(request):
    result = {}
    flag = True
    if request.method == 'POST':
        req = json.loads(request.body)["params"]
        idDelete = req['idDelete']
        for x in idDelete:
            if (apiInfoTable.objects.filter(owningListID=x[0]).count() != 0):
                flag = False
                code = -1
                info = '所选模块中还存在用例，请先删除用例，再删除模块！'
        if (flag):
            for x in idDelete:
                r1 = moduleList.objects.filter(id=x[0]).values("moduleName", "owningListID")
                owningListID = r1[0]['owningListID']
                moduleName = r1[0]['moduleName']
                r2 = projectList.objects.filter(id=owningListID).values("projectName")
                projectName = r2[0]['projectName']
                countCase.objects.filter(projectName=projectName, moduleName=moduleName).delete()
                moduleList.objects.filter(id=x[0]).delete()
                code = 0
                info = '删除成功！'
        result = {
            'code': code,
            'info': info
        }
    return JsonResponse(result, safe=False)


def projectEdit(request):
    if request.method == 'POST':
        id = request.POST.get('id')
        projectName = request.POST.get('projectName')
        moduleName = request.POST.get('moduleName')
        resp = moduleList.objects.filter(id=id).values("moduleName")
        if (resp[0]['moduleName'] == moduleName):
            code = -1
            info = '未做任何修改！'
            result = {
                'code': code,
                'info': info
            }
            return JsonResponse(result, safe=False)
        else:
            countCase.objects.filter(projectName=projectName,
                                     moduleName=resp[0]['moduleName']).update(moduleName=moduleName)
            edit = moduleList.objects.get(id=id)
            edit.moduleName = moduleName
            edit.save()
            code = 0
            info = '修改成功！'
            result = {
                'code': code,
                'info': info
            }
            return JsonResponse(result, safe=False)


def projectImport(request):
    code = -100
    info = '未知错误！'
    result = {'code': code,
              'info': info}
    if request.method == 'POST':
        projectName = request.POST.get('projectName')
        resp2 = projectList.objects.filter(projectName=projectName).values("id")
        owningListID = resp2[0]['id']
        moduleName = request.POST.get('moduleName')
        dtime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        if (moduleList.objects.filter(owningListID=owningListID, moduleName=moduleName).count() == 0):
            f = request.FILES['file']
            filename = f.name.split('.')[-1]
            if (filename == 'xlsx' or filename == 'xls'):
                # 将上传的xlsx表格先保存下来
                with open('main/postfiles/file.xlsx', 'wb+') as destination:
                    for chunk in f.chunks():
                        destination.write(chunk)
                # 打开excel文件
                data = xlrd.open_workbook(r'main/postfiles/file.xlsx')
                # 获取第一张工作表（通过索引的方式）
                table = data.sheets()[0]
                # 获取第一张工作表有效的行数
                nrows = table.nrows
                # 开始读取的行数
                srows = 8
                # 数据校验
                verification = True
                # 获取host存入host表
                ncols = table.ncols
                hostsList = table.col_values(2, start_rowx=srows, end_rowx=nrows)
                for i in hostsList:
                    hostTags.objects.get_or_create(qa=i)

                for i in range(srows, nrows):
                    # data_list用来存放数据
                    data_list = []
                    # 将table中第一行的数据读取并添加到data_list中
                    data_list.extend(table.row_values(i))
                    apiname = data_list[0]
                    method = data_list[1]
                    host = data_list[2]
                    url = data_list[3]
                    headers = data_list[4]
                    body = data_list[5]
                    t_id = data_list[6]
                    depend_caseId = data_list[7]
                    depend_casedata = data_list[8]
                    statuscode = data_list[9]
                    isSecret = data_list[10]
                    key_id = data_list[11]
                    secret_key = data_list[12]
                    isRedirect = data_list[13]
                    if (method != 'GET') and (method != 'POST'):
                        code = -12
                        info = '当前批量导入文件的method列存在数据不为GET或POST！'
                        verification = False
                        break
                    seen = set()
                    if apiname not in seen:
                        seen.add(apiname)
                    else:
                        code = -4
                        info = '当前批量导入文件的用例名称中存在重复！'
                        verification = False
                        break
                    if (t_id is None) or (t_id == ""):
                        verification = True
                    elif apiInfoTable.objects.filter(t_id=t_id).count() != 0:
                        code = -10
                        info = '当前批量导入文件的t_id与同一项目下已存在的t_id重复！'
                        verification = False
                        break
                    seen = set()
                    if t_id not in seen:
                        seen.add(t_id)
                    else:
                        code = -11
                        info = '当前批量导入文件的t_id中存在重复！'
                        verification = False
                        break
                    if (headers is None) or (headers == ''):
                        verification = True
                    else:
                        try:
                            json.loads(headers)
                        except ValueError:
                            code = -6
                            info = '当前批量导入文件的header列存在数据不符合json规范！'
                            verification = False
                            break
                    if (depend_casedata is None) or (depend_casedata == ''):
                        verification = True
                    else:
                        checkCode = checkFormat(depend_casedata)["code"]
                        if (checkCode != 0):
                            code = -10
                            info = '当前批量导入文件的depend_casedata列存在数据不符合规范！'
                            verification = False
                            break
                    if (body is None) or (body == ''):
                        verification = True
                    else:
                        try:
                            json.loads(body)
                        except ValueError:
                            code = -7
                            info = '当前批量导入文件的body列存在数据不符合json规范！'
                            verification = False
                            break
                    if (isSecret is None) or (isSecret == '') or (isSecret == False) or (
                            isSecret == True):
                        verification = True
                    else:
                        code = -6
                        info = '当前批量导入文件的isSecret列存在数据不为0或1！'
                        # print isSecret
                        verification = False
                        break
                    if (isRedirect is None) or (isRedirect == '') or (isRedirect == False) or (
                            isRedirect == True):
                        verification = True
                    else:
                        code = -7
                        info = '当前批量导入文件的isRedirect列存在数据不为0或1！'
                        verification = False
                        break
            else:
                code = -8
                verification = False
                info = '不支持.' + filename + '格式，请上传.xls或.xlsx格式的文件'
                result = {
                    'code': code,
                    'info': info
                }
            if (verification):
                inter = moduleList.objects.get_or_create(owningListID=owningListID,
                                                         moduleName=moduleName)

                counttable = countCase.objects.get_or_create(projectName=projectName,
                                                             moduleName=moduleName)
                moduleList.objects.filter(owningListID=owningListID, moduleName=moduleName).update(
                    updateTime=dtime,
                    createTime=dtime)

                listid = \
                    moduleList.objects.filter(owningListID=owningListID,
                                              moduleName=moduleName).values(
                        "id")[0]['id']
                for i in range(srows, nrows):
                    # data_list用来存放数据
                    data_list = []
                    # 将table中第一行的数据读取并添加到data_list中
                    data_list.extend(table.row_values(i))
                    apiname = data_list[0]
                    method = data_list[1]
                    tablehost = data_list[2]
                    host = hostTags.objects.filter(qa=tablehost).values("id")[0]['id']
                    url = data_list[3]
                    headers = data_list[4]
                    body_data = data_list[5]
                    t_id = data_list[6]
                    depend_caseId = data_list[7]
                    depend_casedata = data_list[8]
                    statuscode = data_list[9]
                    isSecret = data_list[10]
                    key_id = data_list[11]
                    secret_key = data_list[12]
                    isRedirect = data_list[13]

                    # print statuscode
                    user = request.session.get('username')
                    content_type = ""
                    # print("****headers***", headers)
                    if (headers is None) or (headers == '') or (headers == '{}'):
                        headers = '{}'
                    else:
                        headers = json.loads(headers)
                        try:
                            content_type = headers["Content-Type"]
                        except Exception as e:
                            content_type = ""
                        headers = json.dumps(headers)

                    body = {}
                    if (body_data is None) or (body_data == '') or (body_data == '{}'):
                        body = '{}'
                    else:
                        # body_data = json.loads(body_data)
                        body["datas"] = []
                        body["showflag"] = 3
                        body["datas"].append({"paramValue": str(body_data)})
                        body = json.dumps(body)
                    # print("****body***", body)
                    if (t_id is None) or (t_id == ''):
                        api_infos = {
                            'apiName': apiname,
                            'method': method,
                            'host': host,
                            'url': url,
                            'headers': headers,
                            'body': body,
                            'lastRunResult': 0,
                            'lastRunTime': None,
                            'creator': user,
                            'owningListID': int(listid),
                            'assertinfo': statuscode,
                            'secret_key': secret_key,
                            'key_id': key_id,
                            'isScreat': bool(isSecret),
                            'isRedirect': bool(isRedirect),
                            'depend_caseId': depend_caseId,
                            'depend_casedata': depend_casedata,
                        }
                    else:
                        api_infos = {
                            'apiName': apiname,
                            'method': method,
                            'host': host,
                            'url': url,
                            'headers': headers,
                            'body': body,
                            'lastRunResult': 0,
                            'lastRunTime': None,
                            'creator': user,
                            'owningListID': int(listid),
                            'assertinfo': statuscode,
                            'secret_key': secret_key,
                            'key_id': key_id,
                            'isScreat': bool(isSecret),
                            'isRedirect': bool(isRedirect),
                            't_id': t_id,
                            'depend_caseId': depend_caseId,
                            'depend_casedata': depend_casedata,
                        }

                    try:
                        apiInfoTable.objects.get_or_create(**api_infos)

                    except BaseException as e:
                        # print(" SQL Error: %s" % e)
                        code = -1
                        info = 'sql error！'
                code = 0
                info = '导入成功！'

            # 通过数据校验，导入数据
            # verification = False
            # code = '0'
            # info = 'test'
        else:
            f = request.FILES['file']
            filename = f.name.split('.')[-1]
            if (filename == 'xlsx' or filename == 'xls'):
                # 将上传的xlsx表格先保存下来
                with open('main/postfiles/file.xlsx', 'wb+') as destination:
                    for chunk in f.chunks():
                        destination.write(chunk)
                # 打开excel文件
                data = xlrd.open_workbook(r'main/postfiles/file.xlsx')
                # 获取第一张工作表（通过索引的方式）
                table = data.sheets()[0]
                # 获取第一张工作表有效的行数
                nrows = table.nrows
                # 开始读取的行数
                srows = 8
                # 数据校验
                verification = True
                # 获取host存入host表
                ncols = table.ncols
                hostsList = table.col_values(2, start_rowx=srows, end_rowx=nrows)
                for i in hostsList:
                    hostTags.objects.get_or_create(qa=i)

                for i in range(srows, nrows):
                    # data_list用来存放数据
                    data_list = []
                    # 将table中第一行的数据读取并添加到data_list中
                    data_list.extend(table.row_values(i))
                    apiname = data_list[0]
                    method = data_list[1]
                    host = data_list[2]
                    url = data_list[3]
                    headers = data_list[4]
                    body = data_list[5]
                    t_id = data_list[6]
                    depend_caseId = data_list[7]
                    depend_casedata = data_list[8]
                    statuscode = data_list[9]
                    isSecret = data_list[10]
                    key_id = data_list[11]
                    secret_key = data_list[12]
                    isRedirect = data_list[13]
                    if (apiname is None) or (apiname == ""):
                        code = -2
                        info = '名称不能为空！'
                        verification = False
                        break
                    if (method != 'GET') and (method != 'POST'):
                        code = -12
                        info = '当前批量导入文件的method列存在数据不为GET或POST！'
                        verification = False
                        break
                    seen = set()
                    if apiname not in seen:
                        seen.add(apiname)
                    else:
                        code = -4
                        info = '当前批量导入文件的用例名称中存在重复！'
                        verification = False
                        break
                    if (t_id is None) or (t_id == ""):
                        verification = True
                    elif apiInfoTable.objects.filter(t_id=t_id).count() != 0:
                        code = -10
                        info = '当前批量导入文件的t_id与同一项目下已存在的t_id重复！'
                        verification = False
                        break
                    seen = set()
                    if t_id not in seen:
                        seen.add(t_id)
                    else:
                        code = -11
                        info = '当前批量导入文件的t_id中存在重复！'
                        verification = False
                        break
                    if (headers is None) or (headers == ''):
                        verification = True
                    else:
                        try:
                            json.loads(headers)
                        except ValueError:
                            code = -6
                            info = '当前批量导入文件的header列存在数据不符合json规范！'
                            verification = False
                            break
                    if (depend_casedata is None) or (depend_casedata == ''):
                        verification = True
                    else:
                        checkCode = checkFormat(depend_casedata)["code"]
                        if (checkCode != 0):
                            code = -10
                            info = '当前批量导入文件的depend_casedata列存在数据不符合规范！'
                            verification = False
                            break
                    if (body is None) or (body == ''):
                        verification = True
                    else:
                        try:
                            json.loads(body)
                        except ValueError:
                            code = -7
                            info = '当前批量导入文件的body列存在数据不符合json规范！'
                            verification = False
                            break
                    if (isSecret is None) or (isSecret == '') or (isSecret == False) or (
                            isSecret == True):
                        verification = True
                    else:
                        code = -6
                        info = '当前批量导入文件的isSecret列存在数据不为0或1！'
                        # print isSecret
                        verification = False
                        break
                    if (isRedirect is None) or (isRedirect == '') or (isRedirect == False) or (
                            isRedirect == True):
                        verification = True
                    else:
                        code = -7
                        info = '当前批量导入文件的isRedirect列存在数据不为0或1！'
                        verification = False
                        break
            else:
                code = -8
                verification = False
                info = '不支持.' + filename + '格式，请上传.xls或.xlsx格式的文件'
                result = {
                    'code': code,
                    'info': info
                }
            if (verification):
                listid = \
                    moduleList.objects.filter(owningListID=owningListID,
                                              moduleName=moduleName).values(
                        "id")[0]['id']
                for i in range(srows, nrows):
                    # data_list用来存放数据
                    data_list = []
                    # 将table中第一行的数据读取并添加到data_list中
                    data_list.extend(table.row_values(i))
                    apiname = data_list[0]
                    method = data_list[1]
                    tablehost = data_list[2]
                    host = hostTags.objects.filter(qa=tablehost).values("id")[0]['id']
                    url = data_list[3]
                    headers = data_list[4]
                    body_data = data_list[5]
                    t_id = data_list[6]
                    depend_caseId = data_list[7]
                    depend_casedata = data_list[8]
                    statuscode = data_list[9]
                    isSecret = data_list[10]
                    key_id = data_list[11]
                    secret_key = data_list[12]
                    isRedirect = data_list[13]
                    user = request.session.get('username')
                    content_type = ""
                    # print("****headers***", headers)
                    if (headers is None) or (headers == '') or (headers == '{}'):
                        headers = '{}'
                    else:
                        headers = json.loads(headers)
                        try:
                            content_type = headers["Content-Type"]
                        except Exception as e:
                            content_type = ""
                        headers = json.dumps(headers)

                    body = {}
                    if (body_data is None) or (body_data == '') or (body_data == '{}'):
                        body = '{}'
                    else:
                        # body_data = json.loads(body_data)
                        body["datas"] = []
                        body["showflag"] = 3
                        body["datas"].append({"paramValue": str(body_data)})
                        body = json.dumps(body)
                    # print("****body***", body)
                    if (t_id is None) or (t_id == ''):
                        api_infos = {
                            'apiName': apiname,
                            'method': method,
                            'host': host,
                            'url': url,
                            'headers': headers,
                            'body': body,
                            'lastRunResult': 0,
                            'lastRunTime': None,
                            'creator': user,
                            'owningListID': int(listid),
                            'assertinfo': statuscode,
                            'secret_key': secret_key,
                            'key_id': key_id,
                            'isScreat': bool(isSecret),
                            'isRedirect': bool(isRedirect),
                            'depend_caseId': depend_caseId,
                            'depend_casedata': depend_casedata,
                        }
                    else:
                        api_infos = {
                            'apiName': apiname,
                            'method': method,
                            'host': host,
                            'url': url,
                            'headers': headers,
                            'body': body,
                            'lastRunResult': 0,
                            'lastRunTime': None,
                            'creator': user,
                            'owningListID': int(listid),
                            'assertinfo': statuscode,
                            'secret_key': secret_key,
                            'key_id': key_id,
                            'isScreat': bool(isSecret),
                            'isRedirect': bool(isRedirect),
                            't_id': t_id,
                            'depend_caseId': depend_caseId,
                            'depend_casedata': depend_casedata,
                        }

                    try:
                        apiInfoTable.objects.get_or_create(**api_infos)
                    except BaseException as e:
                        # print(" SQL Error: %s" % e)
                        code = -1
                        info = 'sql error！'
                code = 0
                info = '导入成功！'

    result = {
        'code': code,
        'info': info
    }

    return JsonResponse(result, safe=False)
