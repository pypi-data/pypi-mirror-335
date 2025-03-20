_A='jsonData'
import json
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings as conf_settings
from project.models import UserProfile
from project.sparta_6d49f7e4f5.sparta_761fd1bf33 import qube_e7f0922c1e as qube_e7f0922c1e
from project.sparta_6d49f7e4f5.sparta_e11bc941ea import qube_9f89a97474 as qube_9f89a97474
from project.sparta_6d49f7e4f5.sparta_03569db088.qube_9fc342787d import sparta_7a6dbbc232
@csrf_exempt
@sparta_7a6dbbc232
def sparta_aeacc0e972(request):
	B=request;I=json.loads(B.body);C=json.loads(I[_A]);A=B.user;D=0;E=UserProfile.objects.filter(user=A)
	if E.count()>0:
		F=E[0]
		if F.has_open_tickets:
			C['userId']=F.user_profile_id;G=qube_9f89a97474.sparta_9ca25db761(A)
			if G['res']==1:D=int(G['nbNotifications'])
	H=qube_e7f0922c1e.sparta_aeacc0e972(C,A);H['nbNotificationsHelpCenter']=D;J=json.dumps(H);return HttpResponse(J)
@csrf_exempt
@sparta_7a6dbbc232
def sparta_cc6fdaa788(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=qube_e7f0922c1e.sparta_05f45497f3(C,A.user);E=json.dumps(D);return HttpResponse(E)