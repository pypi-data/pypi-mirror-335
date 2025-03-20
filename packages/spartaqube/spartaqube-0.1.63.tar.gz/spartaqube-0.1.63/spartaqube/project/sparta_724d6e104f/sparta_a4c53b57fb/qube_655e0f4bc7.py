from urllib.parse import urlparse,urlunparse
from django.contrib.auth.decorators import login_required
from django.conf import settings as conf_settings
from django.shortcuts import render
import project.sparta_76336d2b79.sparta_76426419cc.qube_7aa7c52dd2 as qube_7aa7c52dd2
from project.models import UserProfile
from project.sparta_3bc15131c6.sparta_6d9c27d78c.qube_9777884b7b import sparta_34d9a3cc83
from project.sparta_724d6e104f.sparta_61b7d8cac5.qube_9ad9d0a010 import sparta_2c69fb966b
@sparta_34d9a3cc83
@login_required(redirect_field_name='login')
def sparta_aefb62e9ab(request,idSection=1):
	B=request;D=UserProfile.objects.get(user=B.user);E=D.avatar
	if E is not None:E=D.avatar.avatar
	C=urlparse(conf_settings.URL_TERMS)
	if not C.scheme:C=urlunparse(C._replace(scheme='http'))
	F={'item':1,'idSection':idSection,'userProfil':D,'avatar':E,'url_terms':C};A=qube_7aa7c52dd2.sparta_2ebbb966d2(B);A.update(qube_7aa7c52dd2.sparta_86bdc57f92(B.user));A.update(F);G='';A['accessKey']=G;A['menuBar']=4;A.update(sparta_2c69fb966b());return render(B,'dist/project/auth/settings.html',A)