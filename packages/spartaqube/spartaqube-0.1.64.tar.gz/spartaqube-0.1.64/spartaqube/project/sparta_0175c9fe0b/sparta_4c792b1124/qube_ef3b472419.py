import json,base64
from django.http import HttpResponse,Http404
from django.views.decorators.csrf import csrf_exempt
from project.sparta_6d49f7e4f5.sparta_d5335b6e48 import qube_818293f3be as qube_818293f3be
from project.sparta_6d49f7e4f5.sparta_03569db088.qube_9fc342787d import sparta_7a6dbbc232,sparta_bd2ba699ab
@csrf_exempt
@sparta_7a6dbbc232
def sparta_2902446992(request):A=request;B=json.loads(A.body);C=json.loads(B['jsonData']);D=qube_818293f3be.sparta_2902446992(C,A.user);E=json.dumps(D);return HttpResponse(E)