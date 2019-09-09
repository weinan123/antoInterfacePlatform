# -*- coding: utf-8 -*-
from django.shortcuts import render
from models import apiInfoTable, interfaceList
import time
import json
from django.http.response import JsonResponse
import requests
import sys
def configer(request):
    return render(request, 'configer.html')
