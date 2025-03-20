from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from project.sparta_6d49f7e4f5.sparta_03569db088.qube_9fc342787d import sparta_c7cbfbc284
from project.sparta_6d49f7e4f5.sparta_e11bc941ea import qube_9f89a97474 as qube_9f89a97474
from project.models import UserProfile
import project.sparta_d3863a192d.sparta_3c800a8540.qube_a8d0eb6c62 as qube_a8d0eb6c62
@sparta_c7cbfbc284
@login_required(redirect_field_name='login')
def sparta_d0b787be05(request):
	E='avatarImg';B=request;A=qube_a8d0eb6c62.sparta_b2f7a34b3f(B);A['menuBar']=-1;F=qube_a8d0eb6c62.sparta_96fb1a678d(B.user);A.update(F);A[E]='';C=UserProfile.objects.filter(user=B.user)
	if C.count()>0:
		D=C[0];G=D.avatar
		if G is not None:H=D.avatar.image64;A[E]=H
	A['bInvertIcon']=0;return render(B,'dist/project/helpCenter/helpCenter.html',A)
@sparta_c7cbfbc284
@login_required(redirect_field_name='login')
def sparta_73a9a0103b(request):
	A=request;B=UserProfile.objects.filter(user=A.user)
	if B.count()>0:C=B[0];C.has_open_tickets=False;C.save()
	return sparta_d0b787be05(A)