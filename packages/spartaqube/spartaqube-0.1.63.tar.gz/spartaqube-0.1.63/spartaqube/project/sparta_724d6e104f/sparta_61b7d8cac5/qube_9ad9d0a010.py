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
import project.sparta_76336d2b79.sparta_76426419cc.qube_7aa7c52dd2 as qube_7aa7c52dd2
from project.forms import ConnexionForm,RegistrationTestForm,RegistrationBaseForm,RegistrationForm,ResetPasswordForm,ResetPasswordChangeForm
from project.sparta_3bc15131c6.sparta_6d9c27d78c.qube_9777884b7b import sparta_34d9a3cc83
from project.sparta_3bc15131c6.sparta_6d9c27d78c import qube_9777884b7b as qube_9777884b7b
from project.sparta_eb89b25fe4.sparta_b5788bfd23 import qube_d0e0d84f29 as qube_d0e0d84f29
from project.models import LoginLocation,UserProfile
from project.logger_config import logger
def sparta_2c69fb966b():return{'bHasCompanyEE':-1}
def sparta_c609728124(request):B=request;A=qube_7aa7c52dd2.sparta_2ebbb966d2(B);A[_C]=qube_7aa7c52dd2.sparta_001e720e04();A['forbiddenEmail']=conf_settings.FORBIDDEN_EMAIL;return render(B,'dist/project/auth/banned.html',A)
@sparta_34d9a3cc83
def sparta_4938170d19(request):
	C=request;B='/';A=C.GET.get(_I)
	if A is not None:D=A.split(B);A=B.join(D[1:]);A=A.replace(B,'$@$')
	return sparta_e2942dd518(C,A)
def sparta_e8675c76ef(request,redirectUrl):return sparta_e2942dd518(request,redirectUrl)
def sparta_e2942dd518(request,redirectUrl):
	E=redirectUrl;A=request;logger.debug('Welcome to loginRedirectFunc')
	if A.user.is_authenticated:return redirect(_D)
	G=_J;H='Email or password incorrect'
	if A.method==_K:
		C=ConnexionForm(A.POST)
		if C.is_valid():
			I=C.cleaned_data[_F];J=C.cleaned_data[_L];F=authenticate(username=I,password=J)
			if F:
				if qube_9777884b7b.sparta_e1a9f0d045(F):return sparta_c609728124(A)
				login(A,F);K,L=qube_7aa7c52dd2.sparta_41bc7c40f5();LoginLocation.objects.create(user=F,hostname=K,ip=L,date_login=datetime.now())
				if E is not None:
					D=E.split('$@$');D=[A for A in D if len(A)>0]
					if len(D)>1:M=D[0];return redirect(reverse(M,args=D[1:]))
					return redirect(E)
				return redirect(_D)
			else:G=_A
		else:G=_A
	C=ConnexionForm();B=qube_7aa7c52dd2.sparta_2ebbb966d2(A);B.update(qube_7aa7c52dd2.sparta_d9ebbe99c6(A));B[_C]=qube_7aa7c52dd2.sparta_001e720e04();B[_G]=C;B[_H]=G;B['redirectUrl']=E;B[_B]=H;B.update(sparta_2c69fb966b());return render(A,'dist/project/auth/login.html',B)
def sparta_e0a701df5c(request):
	B='public@spartaqube.com';A=User.objects.filter(email=B).all()
	if A.count()>0:C=A[0];login(request,C)
	return redirect(_D)
@sparta_34d9a3cc83
def sparta_b508108d25(request):
	A=request
	if A.user.is_authenticated:return redirect(_D)
	E='';D=_J;F=qube_9777884b7b.sparta_96218a489b()
	if A.method==_K:
		if F:B=RegistrationForm(A.POST)
		else:B=RegistrationBaseForm(A.POST)
		if B.is_valid():
			I=B.cleaned_data;H=None
			if F:
				H=B.cleaned_data['code']
				if not qube_9777884b7b.sparta_df4e6ec93a(H):D=_A;E='Wrong guest code'
			if not D:
				J=A.META['HTTP_HOST'];G=qube_9777884b7b.sparta_bc44fad8f4(I,J)
				if int(G[_E])==1:K=G['userObj'];login(A,K);return redirect(_D)
				else:D=_A;E=G[_B]
		else:D=_A;E=B.errors.as_data()
	if F:B=RegistrationForm()
	else:B=RegistrationBaseForm()
	C=qube_7aa7c52dd2.sparta_2ebbb966d2(A);C.update(qube_7aa7c52dd2.sparta_d9ebbe99c6(A));C[_C]=qube_7aa7c52dd2.sparta_001e720e04();C[_G]=B;C[_H]=D;C[_B]=E;C.update(sparta_2c69fb966b());return render(A,'dist/project/auth/registration.html',C)
def sparta_07b7dd610b(request):A=request;B=qube_7aa7c52dd2.sparta_2ebbb966d2(A);B[_C]=qube_7aa7c52dd2.sparta_001e720e04();return render(A,'dist/project/auth/registrationPending.html',B)
def sparta_cc14ee0781(request,token):
	A=request;B=qube_9777884b7b.sparta_e6511726ca(token)
	if int(B[_E])==1:C=B['user'];login(A,C);return redirect(_D)
	D=qube_7aa7c52dd2.sparta_2ebbb966d2(A);D[_C]=qube_7aa7c52dd2.sparta_001e720e04();return redirect(_I)
def sparta_07013b9185(request):logout(request);return redirect(_I)
def sparta_5d48ddcd19(request):
	A=request;from project.models import PlotDBChartShared as C,PlotDBChart;B='cypress_tests@gmail.com';print('Destroy cypress user');D=C.objects.filter(user__email=B).all()
	for E in D:E.delete()
	if A.user.is_authenticated:
		if A.user.email==B:A.user.delete()
	logout(A);return redirect(_I)
def sparta_b1be893f6b(request):A={_E:-100,_B:'You are not logged...'};B=json.dumps(A);return HttpResponse(B)
@csrf_exempt
def sparta_551b0181cd(request):
	A=request;E='';F=_J
	if A.method==_K:
		B=ResetPasswordForm(A.POST)
		if B.is_valid():
			H=B.cleaned_data[_F];I=B.cleaned_data[_M];G=qube_9777884b7b.sparta_551b0181cd(H.lower(),I)
			try:
				if int(G[_E])==1:C=qube_7aa7c52dd2.sparta_2ebbb966d2(A);C.update(qube_7aa7c52dd2.sparta_d9ebbe99c6(A));B=ResetPasswordChangeForm(A.POST);C[_C]=qube_7aa7c52dd2.sparta_001e720e04();C[_G]=B;C[_F]=H;C[_H]=F;C[_B]=E;return render(A,_N,C)
				elif int(G[_E])==-1:E=G[_B];F=_A
			except Exception as J:logger.debug('exception ');logger.debug(J);E='Could not send reset email, please try again';F=_A
		else:E=_O;F=_A
	else:B=ResetPasswordForm()
	D=qube_7aa7c52dd2.sparta_2ebbb966d2(A);D.update(qube_7aa7c52dd2.sparta_d9ebbe99c6(A));D[_C]=qube_7aa7c52dd2.sparta_001e720e04();D[_G]=B;D[_H]=F;D[_B]=E;D.update(sparta_2c69fb966b());return render(A,'dist/project/auth/resetPassword.html',D)
@csrf_exempt
def sparta_522d10c7a6(request):
	D=request;E='';B=_J
	if D.method==_K:
		C=ResetPasswordChangeForm(D.POST)
		if C.is_valid():
			I=C.cleaned_data['token'];F=C.cleaned_data[_L];J=C.cleaned_data['password_confirmation'];K=C.cleaned_data[_M];G=C.cleaned_data[_F].lower()
			if len(F)<6:E='Your password must be at least 6 characters';B=_A
			if F!=J:E='The two passwords must be identical...';B=_A
			if not B:
				H=qube_9777884b7b.sparta_522d10c7a6(K,I,G.lower(),F)
				try:
					if int(H[_E])==1:L=User.objects.get(username=G);login(D,L);return redirect(_D)
					else:E=H[_B];B=_A
				except Exception as M:E='Could not change your password, please try again';B=_A
		else:E=_O;B=_A
	else:return redirect('reset-password')
	A=qube_7aa7c52dd2.sparta_2ebbb966d2(D);A.update(qube_7aa7c52dd2.sparta_d9ebbe99c6(D));A[_C]=qube_7aa7c52dd2.sparta_001e720e04();A[_G]=C;A[_H]=B;A[_B]=E;A[_F]=G;A.update(sparta_2c69fb966b());return render(D,_N,A)