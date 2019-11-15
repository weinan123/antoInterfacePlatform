# -*- coding: utf-8 -*-
from django.shortcuts import render
from models import reports
from django.http.response import JsonResponse
import json, os


def projectconfiger(request):
    return render(request, "projectConfiger.html")