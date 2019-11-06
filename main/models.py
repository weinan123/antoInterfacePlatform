#!/usr/bin/env  python
# --*--coding:utf-8 --*--

from django.db import models


class projectList(models.Model):
    """
    项目表
    """
    projectName = models.CharField(max_length=50, verbose_name='项目名称')
    updateTime = models.DateTimeField(auto_now=True, verbose_name='最近修改时间')
    createTime = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

class moduleList(models.Model):
    """
    模块表
    """
    owningListID = models.IntegerField(blank=False, null=False, verbose_name='所属项目')
    moduleName = models.CharField(max_length=50, verbose_name='模块名称')
    updateTime = models.DateTimeField(auto_now=True, verbose_name='最近修改时间')
    createTime = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

class hostTags(models.Model):
    """
    host
    """

    qa = models.CharField(max_length=50, verbose_name='QA')
    stage = models.CharField(max_length=50, verbose_name='STAGE')
    live = models.CharField(max_length=50, verbose_name='live')
    dev = models.CharField(max_length=50, verbose_name='DEV')
class apiInfoTable(models.Model):
    apiID = models.AutoField(max_length=4, primary_key=True)
    apiName = models.CharField(max_length=100, null=False, error_messages={'required': '名称不能为空'})
    lastRunResult = models.IntegerField(null=True, blank=True,default=0)
    lastRunTime = models.DateTimeField(null=True, blank=True)
    creator = models.CharField(max_length=20, null=False)
    owningListID = models.IntegerField(blank=True,null=True,)
    method = models.CharField(max_length=10)
    host = models.TextField(null=True, blank=True)
    url = models.URLField(null=True,blank=True)
    headers = models.TextField(null=True,blank=True)
    body = models.TextField(null=True,blank=True)
    assertinfo = models.CharField(max_length=200, blank=True)
    secret_key = models.CharField(max_length=200, blank=True, null=True,)
    key_id = models.CharField(max_length=200, blank=True, null=True,)
    isScreat = models.BooleanField(default=False)
    isRedirect = models.BooleanField(default=False)
    t_id = models.CharField(max_length=200, blank=True,null=True, unique=True)
    depend_caseId = models.CharField(max_length=200, null=True,blank=True)
    depend_casedata = models.CharField(max_length=200, null=True, blank=True)
    response = models.TextField(null=True, blank=True)


class countCase(models.Model):
    pmID = models.AutoField(max_length=4,primary_key=True)
    allcaseNum = models.IntegerField(blank=True,null=True,)
    passcaseNum = models.IntegerField(blank=True,null=True,)
    failcaseNum = models.IntegerField(blank=True,null=True,)
    blockvaseNum = models.IntegerField(blank=True,null=True,)
    projectName = models.CharField(max_length=50, verbose_name='项目名称',blank=True)
    moduleName = models.CharField(max_length=50, verbose_name='模块名称',blank=True)
    update = models.DateTimeField(auto_now_add=True, verbose_name='更新时间',blank=True)

class reports(models.Model):
    report_runName = models.CharField(max_length=200)
    startTime = models.DateTimeField(null=True, blank=True)
    endTime = models.DateTimeField(null=True, blank=True)
    totalNum = models.IntegerField()
    successNum = models.IntegerField()
    failNum = models.IntegerField()
    errorNum = models.IntegerField()
    executor = models.CharField(max_length=50)
    report_localName = models.CharField(max_length=200)

class users(models.Model):
    username = models.CharField(max_length=200,null=True)
    department = models.CharField(max_length=100,null=True,default='测试工程师')
    depart_lever = models.IntegerField(default=3)
    group = models.CharField(max_length=50,null=True)
    batch_check = models.BooleanField(default=True)
    batch_run = models.BooleanField(default=False)
    batch_del = models.BooleanField(default=False)
    configer_permit = models.BooleanField(default=False)

class department(models.Model):
    depart_lever = models.IntegerField()
    depart_name = models.CharField(max_length=50)



