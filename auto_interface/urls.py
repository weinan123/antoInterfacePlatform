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
from main import views  as main
from main import apiinfo
from main import projectList

urlpatterns = [
    url(r'^$', main.index),
    url(r'^index/$', main.index),
    url(r'^login/$', main.login),
    url(r'^logout/$', main.logout, ),
    url(r'^register/$', main.register),
    url(r'^projectList/$', projectList.projectList),
    url(r'^addProjectList/$', projectList.addProjectList),
    url(r'^projectListInfo/$', projectList.projectListInfo),
    url(r'^projectView/$', projectList.projectView),
    url(r'^projectDelete/$', projectList.projectDelete),
    url(r'^projectEdit/$', projectList.projectEdit),
    url(r'^singleInterface/$', main.singleInterface),
    url(r'^getRequest/$', main.getRequest),
    url(r'^apiInfo/$', apiinfo.allinfo),
    url(r'^apiInfopage/$', apiinfo.allinfopage),
    url(r'^addApi/$', apiinfo.addApi),
    url(r'^apidelete/$', apiinfo.apidel),

]
