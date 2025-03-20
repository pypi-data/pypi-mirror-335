_C='isAuth'
_B='jsonData'
_A='res'
import json
from django.contrib.auth import logout
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from project.sparta_6d49f7e4f5.sparta_03569db088 import qube_9fc342787d as qube_9fc342787d
from project.sparta_d3863a192d.sparta_3c800a8540.qube_a8d0eb6c62 import sparta_c8b38dec53
from project.logger_config import logger
@csrf_exempt
def sparta_91e23486ae(request):A=json.loads(request.body);B=json.loads(A[_B]);return qube_9fc342787d.sparta_91e23486ae(B)
@csrf_exempt
def sparta_4c91d0a3a5(request):logout(request);A={_A:1};B=json.dumps(A);return HttpResponse(B)
@csrf_exempt
def sparta_47e0f5248f(request):
	if request.user.is_authenticated:A=1
	else:A=0
	B={_A:1,_C:A};C=json.dumps(B);return HttpResponse(C)
def sparta_8b57a527f8(request):
	B=request;from django.contrib.auth import authenticate as F,login;from django.contrib.auth.models import User as C;G=json.loads(B.body);D=json.loads(G[_B]);H=D['email'];I=D['password'];E=0
	try:
		A=C.objects.get(email=H);A=F(B,username=A.username,password=I)
		if A is not None:login(B,A);E=1
	except C.DoesNotExist:pass
	J={_A:1,_C:E};K=json.dumps(J);return HttpResponse(K)