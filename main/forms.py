# -*- coding: utf-8 -*-
from django import forms
class UserForm(forms.Form):
    username = forms.CharField(label='用户名',max_length=100)
    password = forms.CharField(label='密_码',widget=forms.PasswordInput())
    password2 = forms.CharField(label='密_码2', widget=forms.PasswordInput())