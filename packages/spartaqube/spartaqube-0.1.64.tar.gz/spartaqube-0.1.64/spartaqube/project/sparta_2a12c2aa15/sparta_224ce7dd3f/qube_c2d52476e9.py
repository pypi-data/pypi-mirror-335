from urllib.parse import urlparse,urlunparse
from django.contrib.auth.decorators import login_required
from django.conf import settings as conf_settings
from django.shortcuts import render
import project.sparta_d3863a192d.sparta_3c800a8540.qube_a8d0eb6c62 as qube_a8d0eb6c62
from project.models import UserProfile
from project.sparta_6d49f7e4f5.sparta_03569db088.qube_9fc342787d import sparta_c7cbfbc284
from project.sparta_2a12c2aa15.sparta_b4df3e5a8f.qube_4b771db30e import sparta_8b3ecbf272
@sparta_c7cbfbc284
@login_required(redirect_field_name='login')
def sparta_c761dc321f(request,idSection=1):
	B=request;D=UserProfile.objects.get(user=B.user);E=D.avatar
	if E is not None:E=D.avatar.avatar
	C=urlparse(conf_settings.URL_TERMS)
	if not C.scheme:C=urlunparse(C._replace(scheme='http'))
	F={'item':1,'idSection':idSection,'userProfil':D,'avatar':E,'url_terms':C};A=qube_a8d0eb6c62.sparta_b2f7a34b3f(B);A.update(qube_a8d0eb6c62.sparta_96fb1a678d(B.user));A.update(F);G='';A['accessKey']=G;A['menuBar']=4;A.update(sparta_8b3ecbf272());return render(B,'dist/project/auth/settings.html',A)