_U='token_reset'
_T='Invalid captcha'
_S='Passwords must be the same'
_R='new_password_confirm'
_Q='Password must be at least 5 characters'
_P='Please put the same passwords'
_O='The current password is not correct'
_N='oldPassword'
_M='passwordConfirm'
_L='password'
_K='Invalid email'
_J='Invalid spartaqube admin password'
_I='new_password'
_H='admin'
_G=None
_F='email'
_E='captcha'
_D='utf-8'
_C='message'
_B='errorMsg'
_A='res'
import os,json,uuid,base64,random,string
from datetime import datetime
import hashlib,requests,hashlib
from cryptography.fernet import Fernet
from random import randint
import pytz
UTC=pytz.utc
from django.contrib.auth.models import User
from django.http import HttpRequest
from django.contrib.auth.hashers import make_password
from django.conf import settings as conf_settings
from django.contrib.auth import login
from project.models import UserProfile,Avatar,contactUS,SpartaQubeCode
from project.sparta_3bc15131c6.sparta_9ae55c1626 import qube_9cdb8768cf as qube_9cdb8768cf
from project.sparta_3bc15131c6.sparta_c3609a6c34.qube_ccb6832bf6 import Email as Email
from project.sparta_76336d2b79.sparta_76426419cc.qube_7aa7c52dd2 import sparta_c96270d2bf,sparta_3cbe079586,sparta_1a5afb296b
from project.sparta_3bc15131c6.sparta_6d9c27d78c.qube_9777884b7b import sparta_a9edf67525
from project.logger_config import logger
def sparta_c596ab8467(json_data,user_obj):
	B=user_obj;A=json_data;D=A['messageContactUs'];E=A['titleContactUs'];G=A[_E];H=datetime.now();contactUS.objects.create(message=D,title=E,user=B,date_created=H);I={_C:D,'title':E,_E:G,_F:B.email,'first_name':B.first_name,'last_name':B.last_name};F=dict();F['jsonData']=json.dumps(I);J={'http':os.environ.get('http_proxy',_G),'https':os.environ.get('https_proxy',_G)};C=requests.post(f"{conf_settings.SPARTAQUBE_WEBSITE}/contact-us-app",data=json.dumps(F),proxies=J)
	if C.status_code==200:
		try:logger.debug('response.text');logger.debug(C.text);A=json.loads(C.text);return A
		except Exception as K:return{_A:-1,_B:str(K)}
	L={_A:-1,_B:'An unexpected error occurred, please check your internet connection and try again'};return L
def sparta_fec571ba10(message,typeCase=0,companyName=_G):
	D='Type';B=companyName;C=User.objects.filter(is_staff=True)
	if C.count()>0:
		E=C[0];A=Email(E.username,[conf_settings.CONTACT_US_EMAIL],'Contact US','Contact US new message')
		if B is not _G:A.addOneRow('Company',B);A.addLineSeparator()
		A.addOneRow('Message',message);A.addLineSeparator()
		if int(typeCase)==0:A.addOneRow(D,'General question')
		else:A.addOneRow(D,'Report Bug')
		A.send()
def sparta_c93fc22eae(json_data,userObj):
	C=json_data;A=userObj;D=C[_L];E=C[_M];F=C[_N]
	if len(D)>4:
		if D==E:
			if A.check_password(F):G=make_password(D);A.password=G;A.save();B={_A:1,'userObj':A}
			else:B={_A:-1,_C:_O}
		else:B={_A:-1,_C:_P}
	else:B={_A:-1,_C:_Q}
	return B
def sparta_7aa6d4ac0c(json_data,userObj):
	B=json_data;C=B[_L];D=B[_M];E=B[_N]
	if len(C)>4:
		if C==D:
			if userObj.check_password(E):A={_A:1}
			else:A={_A:-1,_C:_O}
		else:A={_A:-1,_C:_P}
	else:A={_A:-1,_C:_Q}
	return A
def sparta_44da6d7eae(json_data,userObj):
	D=json_data;F=D['old_spartaqube_code'];G=D['new_spartaqube_code']
	if not sparta_a9edf67525(F):return{_A:-1,_B:'Invalid current code'}
	A=hashlib.md5(G.encode(_D)).hexdigest();A=base64.b64encode(A.encode(_D));A=A.decode(_D);B=datetime.now().astimezone(UTC);E=SpartaQubeCode.objects.all()
	if E.count()==0:SpartaQubeCode.objects.create(spartaqube_code=A,date_created=B,last_update=B)
	else:C=E[0];C.spartaqube_code=A;C.last_update=B;C.save()
	return{_A:1}
def sparta_c360c54302(json_data,userObj):A=userObj;C=json_data['base64image'];K=hashlib.sha256((str(A.id)+'_'+A.email+str(datetime.now())).encode(_D)).hexdigest();D,E=C.split(';base64,');F,L=D.split('/');G=F.split(':')[-1];B=UserProfile.objects.get(user=A);H=datetime.now();I=Avatar.objects.create(avatar=G,image64=E,date_created=H);B.avatar=I;B.save();J={_A:1};return J
def sparta_6213cddc9a(json_data,userObj):B=json_data['bDarkTheme'];A=UserProfile.objects.get(user=userObj);A.is_dark_theme=B;A.save();C={_A:1};return C
def sparta_9e0c500a7f(json_data,userObj):
	C='fontSizePx';A=json_data;D=A['theme'];B=UserProfile.objects.get(user=userObj);B.editor_theme=D
	if C in A:
		try:B.font_size=float(A[C])
		except:pass
	B.save();E={_A:1};return E
def sparta_9abc7afdbb():B='spartaqube-reset-password';A=B.encode(_D);A=hashlib.md5(A).hexdigest();A=base64.b64encode(A.encode(_D));return A.decode(_D)
def sparta_d44b5b903b(json_data):
	A=json_data;C=A[_F];E=A[_H];B=A[_I];F=A[_R]
	if not sparta_1a5afb296b(E):return{_A:-1,_B:_J}
	if not User.objects.filter(username=C).exists():return{_A:-1,_B:_K}
	if B!=F:return{_A:-1,_B:_S}
	D=User.objects.filter(username=C).all()[0];G=make_password(B);D.password=G;D.save();return{_A:1,_I:B}
def sparta_aac14b9052(json_data):
	A=json_data;E=A[_E];B=A[_F];F=A[_H];G=sparta_c96270d2bf(E)
	if G[_A]!=1:return{_A:-1,_B:_T}
	if not sparta_3cbe079586(F):return{_A:-1,_B:_J}
	if not User.objects.filter(username=B).exists():return{_A:-1,_B:_K}
	H=User.objects.filter(username=B).all()[0];C=db_functions.get_user_profile_obj(H);D=''.join(random.choice(string.ascii_uppercase+string.digits)for A in range(5));C.token_reset_password=D;C.save();return{_A:1,_U:D}
def sparta_9d36b96926(request,json_data):
	A=json_data;F=A[_E];D=A[_F];G=A[_H];H=A[_U];E=A[_I];I=A[_R];J=sparta_c96270d2bf(F)
	if J[_A]!=1:return{_A:-1,_B:_T}
	if not sparta_3cbe079586(G):return{_A:-1,_B:_J}
	if not User.objects.filter(username=D).exists():return{_A:-1,_B:_K}
	if E!=I:return{_A:-1,_B:_S}
	B=User.objects.filter(username=D).all()[0];C=db_functions.get_user_profile_obj(B)
	if C.token_reset_password!=H:return{_A:-1,_B:'Invalid reset token'}
	C.token_reset_password='';C.save();K=make_password(E);B.password=K;B.save();login(request,B);return{_A:1}