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
    updateTime = models.DateTimeField(auto_now=True, verbose_name='最近修改时间')
    createTime = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    def __unicode__(self):
        return self.projectName

    def __str__(self):
        return self.projectName

    class Meta:
        verbose_name = '项目'
        verbose_name_plural = '项目'
