_A='jsonData'
import json,inspect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.forms.models import model_to_dict
from django.http import HttpResponse
from django.shortcuts import render,redirect
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings as conf_settings
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.hashers import make_password
from project.sparta_6d49f7e4f5.sparta_6ce82cdb9c import qube_a4fbfc3357 as qube_a4fbfc3357
from project.sparta_6d49f7e4f5.sparta_03569db088.qube_9fc342787d import sparta_7a6dbbc232
def sparta_9330b3c4a0(request):A={'res':1};B=json.dumps(A);return HttpResponse(B)
@csrf_exempt
@sparta_7a6dbbc232
def sparta_55c27bc53f(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=qube_a4fbfc3357.sparta_55c27bc53f(C,A.user);E=json.dumps(D);return HttpResponse(E)
@csrf_exempt
@sparta_7a6dbbc232
def sparta_b054b9bbd7(request):
	C='userObj';B=request;D=json.loads(B.body);E=json.loads(D[_A]);F=B.user;A=qube_a4fbfc3357.sparta_b054b9bbd7(E,F)
	if A['res']==1:
		if C in list(A.keys()):login(B,A[C]);A.pop(C,None)
	G=json.dumps(A);return HttpResponse(G)
@csrf_exempt
@sparta_7a6dbbc232
def sparta_c15e131c96(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=A.user;E=qube_a4fbfc3357.sparta_c15e131c96(C,D);F=json.dumps(E);return HttpResponse(F)
@csrf_exempt
@sparta_7a6dbbc232
def sparta_0fdf4d70b8(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=qube_a4fbfc3357.sparta_0fdf4d70b8(C,A.user);E=json.dumps(D);return HttpResponse(E)
@csrf_exempt
@sparta_7a6dbbc232
def sparta_9487fa5355(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=qube_a4fbfc3357.sparta_9487fa5355(C,A.user);E=json.dumps(D);return HttpResponse(E)
@csrf_exempt
@sparta_7a6dbbc232
def sparta_dcb938f8df(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=qube_a4fbfc3357.sparta_dcb938f8df(C,A.user);E=json.dumps(D);return HttpResponse(E)
@csrf_exempt
def sparta_7592c8db48(request):A=json.loads(request.body);B=json.loads(A[_A]);C=qube_a4fbfc3357.token_reset_password_worker(B);D=json.dumps(C);return HttpResponse(D)
@csrf_exempt
@sparta_7a6dbbc232
def sparta_b824334dbc(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=qube_a4fbfc3357.network_master_reset_password(C,A.user);E=json.dumps(D);return HttpResponse(E)
@csrf_exempt
def sparta_c031fa549f(request):A=json.loads(request.body);B=json.loads(A[_A]);C=qube_a4fbfc3357.sparta_c031fa549f(B);D=json.dumps(C);return HttpResponse(D)
@csrf_exempt
def sparta_917a122841(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=qube_a4fbfc3357.sparta_917a122841(A,C);E=json.dumps(D);return HttpResponse(E)