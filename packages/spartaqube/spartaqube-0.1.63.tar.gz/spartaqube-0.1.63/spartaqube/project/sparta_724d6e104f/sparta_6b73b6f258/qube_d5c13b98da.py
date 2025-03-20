import os,json,getpass,platform
from pathlib import Path
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings as conf_settings
import project.sparta_76336d2b79.sparta_76426419cc.qube_7aa7c52dd2 as qube_7aa7c52dd2
from project.sparta_3bc15131c6.sparta_6d9c27d78c.qube_9777884b7b import sparta_34d9a3cc83
from project.sparta_3bc15131c6.sparta_1ec16518f2 import qube_e27ca60edf as qube_e27ca60edf
from project.sparta_3bc15131c6.sparta_bf064088d7 import qube_b54b4f1c5e as qube_b54b4f1c5e
def sparta_9761ee48b4():
	A=platform.system()
	if A=='Windows':return'windows'
	elif A=='Linux':return'linux'
	elif A=='Darwin':return'mac'
	else:return
@csrf_exempt
@sparta_34d9a3cc83
@login_required(redirect_field_name='login')
def sparta_048bfd3960(request):
	E='template';D='developer';B=request
	if not conf_settings.IS_DEV_VIEW_ENABLED:A=qube_7aa7c52dd2.sparta_2ebbb966d2(B);return render(B,'dist/project/homepage/homepage.html',A)
	A=qube_7aa7c52dd2.sparta_2ebbb966d2(B);A['menuBar']=12;F=qube_7aa7c52dd2.sparta_86bdc57f92(B.user);A.update(F);A['bCodeMirror']=True;G=os.path.dirname(__file__);C=os.path.dirname(os.path.dirname(G));H=os.path.join(C,'static');I=os.path.join(H,'js',D,E,'frontend');A['frontend_path']=I;J=os.path.dirname(C);K=os.path.join(J,'django_app_template',D,E,'backend');A['backend_path']=K;return render(B,'dist/project/developer/developerExamples.html',A)