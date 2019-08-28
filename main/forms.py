# -*- coding: utf-8 -*-
from django import forms


class UserForm(forms.Form):
    username = forms.CharField(label='用户名', max_length=100)
    password = forms.CharField(label='密_码', widget=forms.PasswordInput())
    password2 = forms.CharField(label='密_码2', widget=forms.PasswordInput())


class projectForm(forms.Form):
    projectName = forms.CharField(max_length=50, label='项目名称')
    moduleName = forms.CharField(max_length=50, label='模块名称')
    host = forms.CharField(max_length=50, label='域名地址')
