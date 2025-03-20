_A='jsonData'
import json
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings as conf_settings
from project.models import UserProfile
from project.sparta_3bc15131c6.sparta_15cb0bb44d import qube_8e8424253e as qube_8e8424253e
from project.sparta_3bc15131c6.sparta_6514c6274c import qube_1ed3f2decd as qube_1ed3f2decd
from project.sparta_3bc15131c6.sparta_6d9c27d78c.qube_9777884b7b import sparta_a7a1f51ac1
@csrf_exempt
@sparta_a7a1f51ac1
def sparta_52ce380875(request):
	B=request;I=json.loads(B.body);C=json.loads(I[_A]);A=B.user;D=0;E=UserProfile.objects.filter(user=A)
	if E.count()>0:
		F=E[0]
		if F.has_open_tickets:
			C['userId']=F.user_profile_id;G=qube_1ed3f2decd.sparta_61e96a803c(A)
			if G['res']==1:D=int(G['nbNotifications'])
	H=qube_8e8424253e.sparta_52ce380875(C,A);H['nbNotificationsHelpCenter']=D;J=json.dumps(H);return HttpResponse(J)
@csrf_exempt
@sparta_a7a1f51ac1
def sparta_6dd771b1cc(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=qube_8e8424253e.sparta_02ac7054af(C,A.user);E=json.dumps(D);return HttpResponse(E)