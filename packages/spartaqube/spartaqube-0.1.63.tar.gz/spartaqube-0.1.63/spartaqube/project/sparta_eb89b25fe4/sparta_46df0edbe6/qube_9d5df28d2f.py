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
from project.sparta_3bc15131c6.sparta_64f7a746d4 import qube_aaf194d9a2 as qube_aaf194d9a2
from project.sparta_3bc15131c6.sparta_6d9c27d78c.qube_9777884b7b import sparta_a7a1f51ac1
def sparta_badb89b7cb(request):A={'res':1};B=json.dumps(A);return HttpResponse(B)
@csrf_exempt
@sparta_a7a1f51ac1
def sparta_c596ab8467(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=qube_aaf194d9a2.sparta_c596ab8467(C,A.user);E=json.dumps(D);return HttpResponse(E)
@csrf_exempt
@sparta_a7a1f51ac1
def sparta_c93fc22eae(request):
	C='userObj';B=request;D=json.loads(B.body);E=json.loads(D[_A]);F=B.user;A=qube_aaf194d9a2.sparta_c93fc22eae(E,F)
	if A['res']==1:
		if C in list(A.keys()):login(B,A[C]);A.pop(C,None)
	G=json.dumps(A);return HttpResponse(G)
@csrf_exempt
@sparta_a7a1f51ac1
def sparta_44da6d7eae(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=A.user;E=qube_aaf194d9a2.sparta_44da6d7eae(C,D);F=json.dumps(E);return HttpResponse(F)
@csrf_exempt
@sparta_a7a1f51ac1
def sparta_c360c54302(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=qube_aaf194d9a2.sparta_c360c54302(C,A.user);E=json.dumps(D);return HttpResponse(E)
@csrf_exempt
@sparta_a7a1f51ac1
def sparta_6213cddc9a(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=qube_aaf194d9a2.sparta_6213cddc9a(C,A.user);E=json.dumps(D);return HttpResponse(E)
@csrf_exempt
@sparta_a7a1f51ac1
def sparta_9e0c500a7f(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=qube_aaf194d9a2.sparta_9e0c500a7f(C,A.user);E=json.dumps(D);return HttpResponse(E)
@csrf_exempt
def sparta_a9737b69eb(request):A=json.loads(request.body);B=json.loads(A[_A]);C=qube_aaf194d9a2.token_reset_password_worker(B);D=json.dumps(C);return HttpResponse(D)
@csrf_exempt
@sparta_a7a1f51ac1
def sparta_0caa79d930(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=qube_aaf194d9a2.network_master_reset_password(C,A.user);E=json.dumps(D);return HttpResponse(E)
@csrf_exempt
def sparta_d44b5b903b(request):A=json.loads(request.body);B=json.loads(A[_A]);C=qube_aaf194d9a2.sparta_d44b5b903b(B);D=json.dumps(C);return HttpResponse(D)
@csrf_exempt
def sparta_9d36b96926(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=qube_aaf194d9a2.sparta_9d36b96926(A,C);E=json.dumps(D);return HttpResponse(E)