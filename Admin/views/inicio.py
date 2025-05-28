from django.shortcuts import render, redirect
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
import json
from django.contrib.auth.models import User

def inicio(request):
    return render(request, 'admin/inicio.html')


