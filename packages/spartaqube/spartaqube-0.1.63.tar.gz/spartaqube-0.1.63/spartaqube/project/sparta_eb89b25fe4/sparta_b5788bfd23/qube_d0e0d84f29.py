_C='isAuth'
_B='jsonData'
_A='res'
import json
from django.contrib.auth import logout
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from project.sparta_3bc15131c6.sparta_6d9c27d78c import qube_9777884b7b as qube_9777884b7b
from project.sparta_76336d2b79.sparta_76426419cc.qube_7aa7c52dd2 import sparta_c96270d2bf
from project.logger_config import logger
@csrf_exempt
def sparta_bc44fad8f4(request):A=json.loads(request.body);B=json.loads(A[_B]);return qube_9777884b7b.sparta_bc44fad8f4(B)
@csrf_exempt
def sparta_d1d1747fab(request):logout(request);A={_A:1};B=json.dumps(A);return HttpResponse(B)
@csrf_exempt
def sparta_f6fe1d5551(request):
	if request.user.is_authenticated:A=1
	else:A=0
	B={_A:1,_C:A};C=json.dumps(B);return HttpResponse(C)
def sparta_cd4682fac6(request):
	B=request;from django.contrib.auth import authenticate as F,login;from django.contrib.auth.models import User as C;G=json.loads(B.body);D=json.loads(G[_B]);H=D['email'];I=D['password'];E=0
	try:
		A=C.objects.get(email=H);A=F(B,username=A.username,password=I)
		if A is not None:login(B,A);E=1
	except C.DoesNotExist:pass
	J={_A:1,_C:E};K=json.dumps(J);return HttpResponse(K)