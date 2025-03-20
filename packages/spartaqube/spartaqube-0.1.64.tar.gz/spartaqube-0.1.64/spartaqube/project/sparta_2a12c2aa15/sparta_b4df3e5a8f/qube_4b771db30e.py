_O='Please send valid data'
_N='dist/project/auth/resetPasswordChange.html'
_M='captcha'
_L='password'
_K='POST'
_J=False
_I='login'
_H='error'
_G='form'
_F='email'
_E='res'
_D='home'
_C='manifest'
_B='errorMsg'
_A=True
import json,hashlib,uuid
from datetime import datetime
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.shortcuts import render,redirect
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings as conf_settings
from django.urls import reverse
import project.sparta_d3863a192d.sparta_3c800a8540.qube_a8d0eb6c62 as qube_a8d0eb6c62
from project.forms import ConnexionForm,RegistrationTestForm,RegistrationBaseForm,RegistrationForm,ResetPasswordForm,ResetPasswordChangeForm
from project.sparta_6d49f7e4f5.sparta_03569db088.qube_9fc342787d import sparta_c7cbfbc284
from project.sparta_6d49f7e4f5.sparta_03569db088 import qube_9fc342787d as qube_9fc342787d
from project.sparta_0175c9fe0b.sparta_2977907cbc import qube_d068200017 as qube_d068200017
from project.models import LoginLocation,UserProfile
from project.logger_config import logger
def sparta_8b3ecbf272():return{'bHasCompanyEE':-1}
def sparta_1332cf9e7c(request):B=request;A=qube_a8d0eb6c62.sparta_b2f7a34b3f(B);A[_C]=qube_a8d0eb6c62.sparta_7fff3ad18d();A['forbiddenEmail']=conf_settings.FORBIDDEN_EMAIL;return render(B,'dist/project/auth/banned.html',A)
@sparta_c7cbfbc284
def sparta_f49f970146(request):
	C=request;B='/';A=C.GET.get(_I)
	if A is not None:D=A.split(B);A=B.join(D[1:]);A=A.replace(B,'$@$')
	return sparta_b219918a05(C,A)
def sparta_3b2a48b236(request,redirectUrl):return sparta_b219918a05(request,redirectUrl)
def sparta_b219918a05(request,redirectUrl):
	E=redirectUrl;A=request;logger.debug('Welcome to loginRedirectFunc')
	if A.user.is_authenticated:return redirect(_D)
	G=_J;H='Email or password incorrect'
	if A.method==_K:
		C=ConnexionForm(A.POST)
		if C.is_valid():
			I=C.cleaned_data[_F];J=C.cleaned_data[_L];F=authenticate(username=I,password=J)
			if F:
				if qube_9fc342787d.sparta_c3133404b7(F):return sparta_1332cf9e7c(A)
				login(A,F);K,L=qube_a8d0eb6c62.sparta_1c71ff0f04();LoginLocation.objects.create(user=F,hostname=K,ip=L,date_login=datetime.now())
				if E is not None:
					D=E.split('$@$');D=[A for A in D if len(A)>0]
					if len(D)>1:M=D[0];return redirect(reverse(M,args=D[1:]))
					return redirect(E)
				return redirect(_D)
			else:G=_A
		else:G=_A
	C=ConnexionForm();B=qube_a8d0eb6c62.sparta_b2f7a34b3f(A);B.update(qube_a8d0eb6c62.sparta_0356a62beb(A));B[_C]=qube_a8d0eb6c62.sparta_7fff3ad18d();B[_G]=C;B[_H]=G;B['redirectUrl']=E;B[_B]=H;B.update(sparta_8b3ecbf272());return render(A,'dist/project/auth/login.html',B)
def sparta_660180e17e(request):
	B='public@spartaqube.com';A=User.objects.filter(email=B).all()
	if A.count()>0:C=A[0];login(request,C)
	return redirect(_D)
@sparta_c7cbfbc284
def sparta_023dc27df4(request):
	A=request
	if A.user.is_authenticated:return redirect(_D)
	E='';D=_J;F=qube_9fc342787d.sparta_ab765b8867()
	if A.method==_K:
		if F:B=RegistrationForm(A.POST)
		else:B=RegistrationBaseForm(A.POST)
		if B.is_valid():
			I=B.cleaned_data;H=None
			if F:
				H=B.cleaned_data['code']
				if not qube_9fc342787d.sparta_fe4451b67b(H):D=_A;E='Wrong guest code'
			if not D:
				J=A.META['HTTP_HOST'];G=qube_9fc342787d.sparta_91e23486ae(I,J)
				if int(G[_E])==1:K=G['userObj'];login(A,K);return redirect(_D)
				else:D=_A;E=G[_B]
		else:D=_A;E=B.errors.as_data()
	if F:B=RegistrationForm()
	else:B=RegistrationBaseForm()
	C=qube_a8d0eb6c62.sparta_b2f7a34b3f(A);C.update(qube_a8d0eb6c62.sparta_0356a62beb(A));C[_C]=qube_a8d0eb6c62.sparta_7fff3ad18d();C[_G]=B;C[_H]=D;C[_B]=E;C.update(sparta_8b3ecbf272());return render(A,'dist/project/auth/registration.html',C)
def sparta_1534400bf3(request):A=request;B=qube_a8d0eb6c62.sparta_b2f7a34b3f(A);B[_C]=qube_a8d0eb6c62.sparta_7fff3ad18d();return render(A,'dist/project/auth/registrationPending.html',B)
def sparta_e469892078(request,token):
	A=request;B=qube_9fc342787d.sparta_a3bb619b1d(token)
	if int(B[_E])==1:C=B['user'];login(A,C);return redirect(_D)
	D=qube_a8d0eb6c62.sparta_b2f7a34b3f(A);D[_C]=qube_a8d0eb6c62.sparta_7fff3ad18d();return redirect(_I)
def sparta_d4729ecc2d(request):logout(request);return redirect(_I)
def sparta_4df6f48fdb(request):
	A=request;from project.models import PlotDBChartShared as C,PlotDBChart;B='cypress_tests@gmail.com';print('Destroy cypress user');D=C.objects.filter(user__email=B).all()
	for E in D:E.delete()
	if A.user.is_authenticated:
		if A.user.email==B:A.user.delete()
	logout(A);return redirect(_I)
def sparta_7ca3ed8b56(request):A={_E:-100,_B:'You are not logged...'};B=json.dumps(A);return HttpResponse(B)
@csrf_exempt
def sparta_660dd100f1(request):
	A=request;E='';F=_J
	if A.method==_K:
		B=ResetPasswordForm(A.POST)
		if B.is_valid():
			H=B.cleaned_data[_F];I=B.cleaned_data[_M];G=qube_9fc342787d.sparta_660dd100f1(H.lower(),I)
			try:
				if int(G[_E])==1:C=qube_a8d0eb6c62.sparta_b2f7a34b3f(A);C.update(qube_a8d0eb6c62.sparta_0356a62beb(A));B=ResetPasswordChangeForm(A.POST);C[_C]=qube_a8d0eb6c62.sparta_7fff3ad18d();C[_G]=B;C[_F]=H;C[_H]=F;C[_B]=E;return render(A,_N,C)
				elif int(G[_E])==-1:E=G[_B];F=_A
			except Exception as J:logger.debug('exception ');logger.debug(J);E='Could not send reset email, please try again';F=_A
		else:E=_O;F=_A
	else:B=ResetPasswordForm()
	D=qube_a8d0eb6c62.sparta_b2f7a34b3f(A);D.update(qube_a8d0eb6c62.sparta_0356a62beb(A));D[_C]=qube_a8d0eb6c62.sparta_7fff3ad18d();D[_G]=B;D[_H]=F;D[_B]=E;D.update(sparta_8b3ecbf272());return render(A,'dist/project/auth/resetPassword.html',D)
@csrf_exempt
def sparta_6aea53e6e5(request):
	D=request;E='';B=_J
	if D.method==_K:
		C=ResetPasswordChangeForm(D.POST)
		if C.is_valid():
			I=C.cleaned_data['token'];F=C.cleaned_data[_L];J=C.cleaned_data['password_confirmation'];K=C.cleaned_data[_M];G=C.cleaned_data[_F].lower()
			if len(F)<6:E='Your password must be at least 6 characters';B=_A
			if F!=J:E='The two passwords must be identical...';B=_A
			if not B:
				H=qube_9fc342787d.sparta_6aea53e6e5(K,I,G.lower(),F)
				try:
					if int(H[_E])==1:L=User.objects.get(username=G);login(D,L);return redirect(_D)
					else:E=H[_B];B=_A
				except Exception as M:E='Could not change your password, please try again';B=_A
		else:E=_O;B=_A
	else:return redirect('reset-password')
	A=qube_a8d0eb6c62.sparta_b2f7a34b3f(D);A.update(qube_a8d0eb6c62.sparta_0356a62beb(D));A[_C]=qube_a8d0eb6c62.sparta_7fff3ad18d();A[_G]=C;A[_H]=B;A[_B]=E;A[_F]=G;A.update(sparta_8b3ecbf272());return render(D,_N,A)