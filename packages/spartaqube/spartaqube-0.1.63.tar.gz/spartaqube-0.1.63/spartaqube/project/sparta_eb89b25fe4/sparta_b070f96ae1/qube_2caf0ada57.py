import json,base64
from django.http import HttpResponse,Http404
from django.views.decorators.csrf import csrf_exempt
from project.sparta_3bc15131c6.sparta_dcbe38b1c7 import qube_9640f1970b as qube_9640f1970b
from project.sparta_3bc15131c6.sparta_6d9c27d78c.qube_9777884b7b import sparta_a7a1f51ac1,sparta_83a7ae791c
@csrf_exempt
@sparta_a7a1f51ac1
def sparta_ffe02c5538(request):A=request;B=json.loads(A.body);C=json.loads(B['jsonData']);D=qube_9640f1970b.sparta_ffe02c5538(C,A.user);E=json.dumps(D);return HttpResponse(E)