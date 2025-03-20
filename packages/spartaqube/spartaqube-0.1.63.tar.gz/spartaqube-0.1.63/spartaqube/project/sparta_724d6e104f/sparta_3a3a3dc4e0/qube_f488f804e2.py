from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from project.sparta_3bc15131c6.sparta_6d9c27d78c.qube_9777884b7b import sparta_34d9a3cc83
from project.sparta_3bc15131c6.sparta_6514c6274c import qube_1ed3f2decd as qube_1ed3f2decd
from project.models import UserProfile
import project.sparta_76336d2b79.sparta_76426419cc.qube_7aa7c52dd2 as qube_7aa7c52dd2
@sparta_34d9a3cc83
@login_required(redirect_field_name='login')
def sparta_2d58849c7d(request):
	E='avatarImg';B=request;A=qube_7aa7c52dd2.sparta_2ebbb966d2(B);A['menuBar']=-1;F=qube_7aa7c52dd2.sparta_86bdc57f92(B.user);A.update(F);A[E]='';C=UserProfile.objects.filter(user=B.user)
	if C.count()>0:
		D=C[0];G=D.avatar
		if G is not None:H=D.avatar.image64;A[E]=H
	A['bInvertIcon']=0;return render(B,'dist/project/helpCenter/helpCenter.html',A)
@sparta_34d9a3cc83
@login_required(redirect_field_name='login')
def sparta_aa752b1249(request):
	A=request;B=UserProfile.objects.filter(user=A.user)
	if B.count()>0:C=B[0];C.has_open_tickets=False;C.save()
	return sparta_2d58849c7d(A)