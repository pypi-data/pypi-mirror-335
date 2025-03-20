import os,json,getpass,platform
from pathlib import Path
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings as conf_settings
import project.sparta_d3863a192d.sparta_3c800a8540.qube_a8d0eb6c62 as qube_a8d0eb6c62
from project.sparta_6d49f7e4f5.sparta_03569db088.qube_9fc342787d import sparta_c7cbfbc284
from project.sparta_6d49f7e4f5.sparta_eed2ac8b74 import qube_f98e616a62 as qube_f98e616a62
from project.sparta_6d49f7e4f5.sparta_d35bb0bd9f import qube_18e798f08e as qube_18e798f08e
def sparta_8bbeb975f6():
	A=platform.system()
	if A=='Windows':return'windows'
	elif A=='Linux':return'linux'
	elif A=='Darwin':return'mac'
	else:return
@csrf_exempt
@sparta_c7cbfbc284
@login_required(redirect_field_name='login')
def sparta_07a14f1bb8(request):
	E='template';D='developer';B=request
	if not conf_settings.IS_DEV_VIEW_ENABLED:A=qube_a8d0eb6c62.sparta_b2f7a34b3f(B);return render(B,'dist/project/homepage/homepage.html',A)
	A=qube_a8d0eb6c62.sparta_b2f7a34b3f(B);A['menuBar']=12;F=qube_a8d0eb6c62.sparta_96fb1a678d(B.user);A.update(F);A['bCodeMirror']=True;G=os.path.dirname(__file__);C=os.path.dirname(os.path.dirname(G));H=os.path.join(C,'static');I=os.path.join(H,'js',D,E,'frontend');A['frontend_path']=I;J=os.path.dirname(C);K=os.path.join(J,'django_app_template',D,E,'backend');A['backend_path']=K;return render(B,'dist/project/developer/developerExamples.html',A)