# -*- coding: utf-8 -*-
from django.shortcuts import render


def batchReports(request):
    return render(request, "reports.html")