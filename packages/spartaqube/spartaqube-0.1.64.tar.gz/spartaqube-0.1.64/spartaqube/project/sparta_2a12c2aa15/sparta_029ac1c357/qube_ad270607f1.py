_L='bPublicUser'
_K='developer_name'
_J='developer_id'
_I='b_require_password'
_H='developer_obj'
_G='default_project_path'
_F='bCodeMirror'
_E='menuBar'
_D='dist/project/homepage/homepage.html'
_C='res'
_B=None
_A=True
import os,json,getpass,platform
from pathlib import Path
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.static import serve
from django.http import FileResponse,Http404
from urllib.parse import unquote
from django.conf import settings as conf_settings
import project.sparta_d3863a192d.sparta_3c800a8540.qube_a8d0eb6c62 as qube_a8d0eb6c62
from project.sparta_6d49f7e4f5.sparta_03569db088.qube_9fc342787d import sparta_c7cbfbc284
from project.sparta_6d49f7e4f5.sparta_42532fb0ac import qube_c79bed5901 as qube_c79bed5901
from project.sparta_6d49f7e4f5.sparta_bb74460757.qube_96ecfb2e32 import sparta_dac749eee2
@csrf_exempt
@sparta_c7cbfbc284
@login_required(redirect_field_name='login')
def sparta_e533df7ec4(request):
	B=request
	if not conf_settings.IS_DEV_VIEW_ENABLED:A=qube_a8d0eb6c62.sparta_b2f7a34b3f(B);return render(B,_D,A)
	qube_c79bed5901.sparta_ed0c0bedcc();A=qube_a8d0eb6c62.sparta_b2f7a34b3f(B);A[_E]=12;D=qube_a8d0eb6c62.sparta_96fb1a678d(B.user);A.update(D);A[_F]=_A
	def E(path):
		A=Path(path)
		if not A.exists():A.mkdir(parents=_A)
	F=sparta_dac749eee2();C=os.path.join(F,'developer');E(C);A[_G]=C;return render(B,'dist/project/developer/developer.html',A)
@csrf_exempt
def sparta_07b24a166f(request,id):
	B=request
	if not conf_settings.IS_DEV_VIEW_ENABLED:A=qube_a8d0eb6c62.sparta_b2f7a34b3f(B);return render(B,_D,A)
	if id is _B:C=B.GET.get('id')
	else:C=id
	D=False
	if C is _B:D=_A
	else:
		E=qube_c79bed5901.has_developer_access(C,B.user);G=E[_C]
		if G==-1:D=_A
	if D:return sparta_e533df7ec4(B)
	A=qube_a8d0eb6c62.sparta_b2f7a34b3f(B);A[_E]=12;H=qube_a8d0eb6c62.sparta_96fb1a678d(B.user);A.update(H);A[_F]=_A;F=E[_H];A[_G]=F.project_path;A[_I]=0 if E[_C]==1 else 1;A[_J]=F.developer_id;A[_K]=F.name;A[_L]=B.user.is_anonymous;return render(B,'dist/project/developer/developerRun.html',A)
@csrf_exempt
@sparta_c7cbfbc284
@login_required(redirect_field_name='login')
def sparta_9a06366e84(request,id):
	B=request
	if not conf_settings.IS_DEV_VIEW_ENABLED:A=qube_a8d0eb6c62.sparta_b2f7a34b3f(B);return render(B,_D,A)
	if id is _B:C=B.GET.get('id')
	else:C=id
	D=False
	if C is _B:D=_A
	else:
		E=qube_c79bed5901.has_developer_access(C,B.user);G=E[_C]
		if G==-1:D=_A
	if D:return sparta_e533df7ec4(B)
	A=qube_a8d0eb6c62.sparta_b2f7a34b3f(B);A[_E]=12;H=qube_a8d0eb6c62.sparta_96fb1a678d(B.user);A.update(H);A[_F]=_A;F=E[_H];A[_G]=F.project_path;A[_I]=0 if E[_C]==1 else 1;A[_J]=F.developer_id;A[_K]=F.name;A[_L]=B.user.is_anonymous;return render(B,'dist/project/developer/developerDetached.html',A)
def sparta_0492407589(request,project_path,file_name):A=project_path;A=unquote(A);return serve(request,file_name,document_root=A)