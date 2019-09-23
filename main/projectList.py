# -*- coding: utf-8 -*-
import xlrd
from django.shortcuts import render, redirect
import json, time
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from main.models import *
from forms import UserForm, projectForm
from django.contrib import auth
from django.contrib.auth.models import User
from django import forms
import re


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
            if (interfaceList.objects.filter(projectName=form.cleaned_data['projectName'],
                                             moduleName=form.cleaned_data['moduleName']).count() == 0):
                inter = interfaceList.objects.create(projectName=form.cleaned_data['projectName'],
                                                     moduleName=form.cleaned_data['moduleName'],
                                                     host=form.cleaned_data['host'])

                counttable = countCase.objects.create(projectName=form.cleaned_data['projectName'],
                                                      moduleName=form.cleaned_data['moduleName'], )
                counttable.save()
                inter.save()
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


def projectListInfo(request):
    # resp = interfaceList.objects.values("id", "projectName", "host", "moduleName", "updateTime", "createTime")
    # respList = list(resp)
    # for i in range(len(respList)):
    #     respList[i]['updateTime'] = str(respList[i]['updateTime']).split('.')[0]
    # for i in range(len(respList)):
    #     respList[i]['createTime'] = str(respList[i]['createTime']).split('.')[0]
    # result = {
    #     'data': respList,
    #     'code': 0,
    #     'info': 'success'
    # }
    #
    result = {
        'code': -1,
        'info': '调用的方法错误，请使用GET方法查询！'
    }
    if request.method == 'GET':
        resp = interfaceList.objects.values("id", "projectName", "host", "moduleName", "updateTime", "createTime")
        respList = list(resp)
        for i in range(len(respList)):
            respList[i]['updateTime'] = str(respList[i]['updateTime']).split('.')[0]
        for i in range(len(respList)):
            respList[i]['createTime'] = str(respList[i]['createTime']).split('.')[0]
        result = {
            'data': respList,
            'code': 0,
            'info': 'success'
        }
        #
        # allList = interfaceList.objects.all()
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


def projectList(request):
    # form = projectForm()
    # return render(request, 'projectList.html', {'form': form})
    return render(request, 'projectList.html')


def projectView(request):
    if request.method == 'GET':
        id = request.GET.get('id')
        print id
    return HttpResponseRedirect('/projectList/')


def projectDelete(request):
    if request.method == 'GET':
        id = request.GET.get('id')
        if (apiInfoTable.objects.filter(owningListID=id).count() == 0):
            sss = interfaceList.objects.filter(id=id).values_list("projectName", "moduleName")
            print sss[0][0]
            countCase.objects.filter(projectName=sss[0][0], moduleName=sss[0][1]).delete()
            interfaceList.objects.filter(id=id).delete()
            code = 0
            info = '删除成功！'
        else:
            code = -1
            info = '所选项目中还存在用例，请先删除用例，再删除项目！'
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
            if (apiInfoTable.objects.filter(owningListID=x[0]).count() == 0):
                continue
            else:
                flag = False
                code = -1
                info = '所选项目中还存在用例，请先删除用例，再删除项目！'
        for x in idDelete:
            if (flag):
                interfaceList.objects.filter(id=x[0]).delete()
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
        host = request.POST.get('host')
        edit = interfaceList.objects.get(id=id)
        edit.projectName = projectName
        edit.moduleName = moduleName
        edit.host = host
        edit.save()
        return HttpResponseRedirect('/projectList/')


# def projectSort(request):
#     if request.method == 'GET':
#         id = request.GET.get('id')
#         interfaceList.objects.filter(id=id).delete()
#     return HttpResponseRedirect('/projectList/')


# def projectImport(request):
#     Flag = Flag2 = True
#     if request.method == 'POST':
#         f = request.FILES['file']
#         for line in f.readlines():  # 依次读取每行
#             line = line.strip()  # 去掉每行头尾空白
#             if not len(line) or line.startswith('#'):  # 判断是否是空行或注释行
#                 continue  # 跳过
#             matchObj = re.match(r'(GET|POST) (https|http)://(.*?)/(.*) ', line, re.M | re.I)
#             if matchObj:
#                 if (Flag):
#                     Flag = False
#                     method = matchObj.group(1)
#                     protocol = matchObj.group(2)
#                     host = matchObj.group(2) + r'://' + matchObj.group(3)
#                     url = r'/' + matchObj.group(4)
#                     print "method : ", method
#                     print "protocol : ", protocol
#                     print "host : ", host
#                     print "url : ", url
#             matchObj2 = re.match(r'Content-Type: (.*?);(.*)', line, re.M | re.I)
#             if matchObj2:
#                 if (Flag2):
#                     Flag2 = False
#                     header = '{"Content-Type": "' + matchObj2.group(1) + '"}'  # {"Content-Type": "application/json"}
#                     print "header : ", header
#             matchObj3 = re.finditer(r'".+?":".+?"', line, re.M | re.I)
#             if matchObj3:
#                 for match in matchObj3:
#                     print (match.group())
#                     json = re.finditer(r'".+?"', match.group())
#                     for jsonMatch in json:
#                         print jsonMatch.group()
#
#         # with open('main/upload/file.txt', 'wb+') as destination:
#         #     for chunk in f.chunks():
#         #         destination.write(chunk)
#     return HttpResponseRedirect('/projectList/')

# 导入Excel表格数据
def projectImport(request):
    result = {}
    if request.method == 'POST':
        projectName = request.POST.get('projectName')
        moduleName = request.POST.get('moduleName')
        host = request.POST.get('host')
        print 'projectName:' + projectName
        print 'moduleName:' + moduleName
        print 'host:' + host
        inter = interfaceList.objects.create(projectName=projectName,
                                             moduleName=moduleName,
                                             host=host)

        counttable = countCase.objects.create(projectName=projectName,
                                              moduleName=moduleName)
        counttable.save()
        inter.save()

        listid = \
            interfaceList.objects.filter(projectName=projectName, moduleName=moduleName, host=host).values("id")[0][
                'id']
        f = request.FILES['file']
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
        # 数据校验
        verification = True
        for i in range(1, nrows):
            # data_list用来存放数据
            data_list = []
            # 将table中第一行的数据读取并添加到data_list中
            data_list.extend(table.row_values(i))
            apiname = data_list[0]
            method = data_list[1]
            url = data_list[2]
            headers = data_list[4]
            body = data_list[5]
            if (apiname == "") or (apiname is None):
                code = -2
                info = '名称不能为空！'
                verification = False
                break
            if (interfaceList.objects.filter(projectName=projectName,
                                             moduleName=moduleName).count() == 0):
                code = -3
                info = '当前批量导入文件的模块名称与同一项目下已存在的模块重复！'
                verification = False
                break
            seen = set()
            if apiname not in seen:
                seen.add(apiname)
            else:
                code = -4
                info = '当前批量导入文件的模块名称中存在重复！'
                verification = False
                break
        # 通过数据校验，导入数据
        if (verification):
            for i in range(1, nrows):
                # data_list用来存放数据
                data_list = []
                # 将table中第一行的数据读取并添加到data_list中
                data_list.extend(table.row_values(i))
                apiname = data_list[0]
                method = data_list[1]
                url = data_list[2]
                headers = data_list[4]
                body = data_list[5]
                user = request.session.get('username')
                api_infos = {
                    'apiName': apiname,
                    'method': method,
                    'url': url,
                    'headers': headers,
                    'body': body,
                    'lastRunResult': 0,
                    'lastRunTime': None,
                    'creator': user,
                    'owningListID': int(listid)
                }
                try:
                    s = apiInfoTable.objects.create(**api_infos)
                    s.save()
                except BaseException as e:
                    print(" SQL Error: %s" % e)
                    code = -1
                    info = 'sql error！'
            code = 0
            info = '导入成功！'
            result = {
                'code': code,
                'info': info
            }
        return JsonResponse(result, safe=False)
