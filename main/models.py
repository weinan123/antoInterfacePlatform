#!/usr/bin/env  python
# --*--coding:utf-8 --*--

from django.db import models


class interfaceList(models.Model):
    """
    项目表
    """
    projectType = (
        ('Web', 'Web'),
        ('App', 'App')
    )
    projectName = models.CharField(max_length=50, verbose_name='项目名称')
    moduleName = models.CharField(max_length=50, verbose_name='模块名称')
    host = models.CharField(max_length=50, verbose_name='域名地址')
    updateTime = models.DateTimeField(auto_now=True, verbose_name='最近修改时间')
    createTime = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    def __unicode__(self):
        return self.projectName

    def __str__(self):
        return self.projectName

    class Meta:
        verbose_name = '项目'
        verbose_name_plural = '项目'


class apiInfoTable(models.Model):
    apiID = models.AutoField(max_length=4, primary_key=True)
    apiName = models.CharField(max_length=100, null=False, error_messages={'required': '名称不能为空'})
    lastRunResult = models.IntegerField(null=True, blank=True,default=0)
    lastRunTime = models.DateTimeField(null=True, blank=True)
    creator = models.CharField(max_length=20, null=False)
    owningListID = models.IntegerField(blank=True,null=True,)
    method = models.CharField(max_length=10)
    url = models.URLField(blank=True)
    headers = models.TextField(blank=True)
    body = models.TextField(blank=True)
    assertinfo = models.CharField(max_length=200, blank=True)
    files = models.TextField(blank=True)
    secret_key = models.CharField(max_length=200, blank=True)
    key_id = models.CharField(max_length=200, blank=True)
    isScreat = models.BooleanField(default=False)
    isRedirect = models.BooleanField(default=False)


class countCase(models.Model):
    pmID = models.AutoField(max_length=4,primary_key=True)
    allcaseNum = models.IntegerField(blank=True,null=True,)
    passcaseNum = models.IntegerField(blank=True,null=True,)
    failcaseNum = models.IntegerField(blank=True,null=True,)
    blockvaseNum = models.IntegerField(blank=True,null=True,)
    projectName = models.CharField(max_length=50, verbose_name='项目名称',blank=True)
    moduleName = models.CharField(max_length=50, verbose_name='模块名称',blank=True)
    update = models.DateTimeField(auto_now_add=True, verbose_name='更新时间',blank=True)

