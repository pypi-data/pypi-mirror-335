_K='bPublicUser'
_J='notebook_name'
_I='notebook_id'
_H='b_require_password'
_G='notebook_obj'
_F='default_project_path'
_E='bCodeMirror'
_D='menuBar'
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
import project.sparta_d3863a192d.sparta_3c800a8540.qube_a8d0eb6c62 as qube_a8d0eb6c62
from project.sparta_6d49f7e4f5.sparta_03569db088.qube_9fc342787d import sparta_c7cbfbc284
from project.sparta_6d49f7e4f5.sparta_f346ee3364 import qube_713337071c as qube_713337071c
from project.sparta_6d49f7e4f5.sparta_bb74460757.qube_96ecfb2e32 import sparta_dac749eee2
@csrf_exempt
@sparta_c7cbfbc284
@login_required(redirect_field_name='login')
def sparta_6fb42f08a0(request):
	B=request;A=qube_a8d0eb6c62.sparta_b2f7a34b3f(B);A[_D]=13;D=qube_a8d0eb6c62.sparta_96fb1a678d(B.user);A.update(D);A[_E]=_A
	def E(path):
		A=Path(path)
		if not A.exists():A.mkdir(parents=_A)
	F=sparta_dac749eee2();C=os.path.join(F,'notebook');E(C);A[_F]=C;return render(B,'dist/project/notebook/notebook.html',A)
@csrf_exempt
def sparta_d0370eb088(request,id):
	B=request
	if id is _B:C=B.GET.get('id')
	else:C=id
	D=False
	if C is _B:D=_A
	else:
		E=qube_713337071c.sparta_93e3fdd3de(C,B.user);G=E[_C]
		if G==-1:D=_A
	if D:return sparta_6fb42f08a0(B)
	A=qube_a8d0eb6c62.sparta_b2f7a34b3f(B);A[_D]=12;H=qube_a8d0eb6c62.sparta_96fb1a678d(B.user);A.update(H);A[_E]=_A;F=E[_G];A[_F]=F.project_path;A[_H]=0 if E[_C]==1 else 1;A[_I]=F.notebook_id;A[_J]=F.name;A[_K]=B.user.is_anonymous;return render(B,'dist/project/notebook/notebookRun.html',A)
@csrf_exempt
@sparta_c7cbfbc284
@login_required(redirect_field_name='login')
def sparta_d9285b1df3(request,id):
	B=request
	if id is _B:C=B.GET.get('id')
	else:C=id
	D=False
	if C is _B:D=_A
	else:
		E=qube_713337071c.sparta_93e3fdd3de(C,B.user);G=E[_C]
		if G==-1:D=_A
	if D:return sparta_6fb42f08a0(B)
	A=qube_a8d0eb6c62.sparta_b2f7a34b3f(B);A[_D]=12;H=qube_a8d0eb6c62.sparta_96fb1a678d(B.user);A.update(H);A[_E]=_A;F=E[_G];A[_F]=F.project_path;A[_H]=0 if E[_C]==1 else 1;A[_I]=F.notebook_id;A[_J]=F.name;A[_K]=B.user.is_anonymous;return render(B,'dist/project/notebook/notebookDetached.html',A)