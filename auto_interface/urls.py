"""auto_interface URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from main import views as main
from main import apiinfo, report
from main import projectList, configer, usepermit, cookiesManage, caseList, projectConf

urlpatterns = [
    url(r'^$', main.index),
    url(r'^index/$', main.index),
    url(r'^login/$', main.login),
    url(r'^logout/$', main.logout, ),
    url(r'^projectList/$', projectList.projectListView),
    url(r'^firstProjectList/$', projectList.firstProjectList),
    url(r'^addProjectList/$', projectList.addProjectList),
    url(r'^addProject/$', projectList.addProject),
    url(r'^addCase/$', caseList.addCase),
    url(r'^caseAPIInfo/$', caseList.caseAPIInfo),
    url(r'^submitAPI/$', caseList.submitAPI),
    url(r'^caseDelete/$', caseList.caseDelete),
    url(r'^caseBatchDelete/$', caseList.caseBatchDelete),
    url(r'^getUserCookieList/$', caseList.getUserCookieList),
    url(r'^caseBatchRun/$', caseList.caseBatchRun),
    url(r'^runCase/$', caseList.runCase),
    url(r'^modifyCase/$', caseList.modifyCase),
    url(r'^getCaseAPIInfo/$', caseList.getCaseAPIInfo),
    url(r'^caseInfo/$', caseList.caseInfo),
    url(r'^projectListInfo/$', projectList.projectListInfo),
    url(r'^download/$', projectList.download),
    url(r'^projectDelete/$', projectList.projectDelete),
    url(r'^firstProjectDelete/$', projectList.firstProjectDelete),
    url(r'^projectImport/$', projectList.projectImport),
    url(r'^firstProjectListInfo/$', projectList.firstProjectListInfo),
    url(r'^projectBatchDelete/$', projectList.projectBatchDelete),
    url(r'^projectEdit/$', projectList.projectEdit),
    url(r'^singleInterface/$', main.singleInterface),
    url(r'^sendRequest/$', main.sendRequest),
    url(r'^apidelete/$', apiinfo.apidel),
    url(r'^batchdel/$', apiinfo.batchdel),
    url(r'^runsingle/$', apiinfo.runsingle),
    url(r'^batchrun/$', apiinfo.batchrun),
    url(r'^newCase/$', main.newCase),
    url(r'^getProjectList/$', main.getProjectList),
    url(r'^getapiInfos/$', apiinfo.getapiInfos),
    url(r'^singleInterface/editor/$', main.singleInterface),
    url(r'^returnAuthorization/$', main.returnAuthorization),
    url(r'^getchartData/$', main.getchartData),
    url(r'^pararmsFiles/$', main.pararmsFiles),
    url(r'^configer/$', configer.configer),
    url(r'^getAllcase/$', configer.getAllcase),
    url(r'^saveConfigData/$', configer.saveConfigData),
    url(r'^getConfiginitData/$', configer.getConfiginitData),
    url(r'^batchReports/$', report.batchReports),
    url(r'^reportList/$', report.getReportList),
    url(r'^reportDelete/$', report.reportDelete),
    url(r'^reportbatchdel/$', report.reportbatchDelete),
    url(r'^singleInterface/addapi/$', main.singleInterface),
    url(r'^apiCases/$', apiinfo.apiCases),
    url(r'^apiAllCases/$', apiinfo.getAllCases),
    url(r'^projectInfos/$', apiinfo.getProjInfos),
    url(r'^viewreport/$', report.viewReport),
    url(r'^getprojectCase/$', configer.getprojectCase),
    url(r'^userPermit/$', usepermit.userpermit),
    url(r'^getUserData/$', usepermit.getUserData),
    url(r'^getUserLevel/$', usepermit.getUserLevel),
    url(r'^viewapiInfos/$', apiinfo.getapiInfos),
    url(r'^delUserData/$', usepermit.delUserData),
    url(r'^saveUserData/$', usepermit.saveUserData),
    url(r'^getUserData/$', usepermit.getUserData),
    url(r'^getPermission/$', apiinfo.getPermission),
    url(r'^getProjectInfos/$', apiinfo.getProjectInfos),
    url(r'^uploadCase/$', projectList.uploadCase),
    url(r'^getCookies/$', cookiesManage.getCookies),
    url(r'^getCookieList/$', cookiesManage.getCookieList),
    url(r'^delCookies/$', cookiesManage.delCookies),
    url(r'^saveOrUpdateData/$', apiinfo.saveOrUpdateData),
    url(r'^projectconfiger/$', projectConf.projectconfiger),
    url(r'^getScheduleinitData/$', projectConf.getScheduleinitData),
    url(r'^saveProConf/$', projectConf.saveProConf),

]
