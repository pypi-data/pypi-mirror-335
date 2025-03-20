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
import project.sparta_76336d2b79.sparta_76426419cc.qube_7aa7c52dd2 as qube_7aa7c52dd2
from project.sparta_3bc15131c6.sparta_6d9c27d78c.qube_9777884b7b import sparta_34d9a3cc83
from project.sparta_3bc15131c6.sparta_b8050354d7 import qube_2eeaed24d7 as qube_2eeaed24d7
from project.sparta_3bc15131c6.sparta_0d2990c769.qube_886837873c import sparta_235d77fd71
@csrf_exempt
@sparta_34d9a3cc83
@login_required(redirect_field_name='login')
def sparta_b226b1f479(request):
	B=request;A=qube_7aa7c52dd2.sparta_2ebbb966d2(B);A[_D]=13;D=qube_7aa7c52dd2.sparta_86bdc57f92(B.user);A.update(D);A[_E]=_A
	def E(path):
		A=Path(path)
		if not A.exists():A.mkdir(parents=_A)
	F=sparta_235d77fd71();C=os.path.join(F,'notebook');E(C);A[_F]=C;return render(B,'dist/project/notebook/notebook.html',A)
@csrf_exempt
def sparta_635e75804a(request,id):
	B=request
	if id is _B:C=B.GET.get('id')
	else:C=id
	D=False
	if C is _B:D=_A
	else:
		E=qube_2eeaed24d7.sparta_64424211ef(C,B.user);G=E[_C]
		if G==-1:D=_A
	if D:return sparta_b226b1f479(B)
	A=qube_7aa7c52dd2.sparta_2ebbb966d2(B);A[_D]=12;H=qube_7aa7c52dd2.sparta_86bdc57f92(B.user);A.update(H);A[_E]=_A;F=E[_G];A[_F]=F.project_path;A[_H]=0 if E[_C]==1 else 1;A[_I]=F.notebook_id;A[_J]=F.name;A[_K]=B.user.is_anonymous;return render(B,'dist/project/notebook/notebookRun.html',A)
@csrf_exempt
@sparta_34d9a3cc83
@login_required(redirect_field_name='login')
def sparta_a7c699399b(request,id):
	B=request
	if id is _B:C=B.GET.get('id')
	else:C=id
	D=False
	if C is _B:D=_A
	else:
		E=qube_2eeaed24d7.sparta_64424211ef(C,B.user);G=E[_C]
		if G==-1:D=_A
	if D:return sparta_b226b1f479(B)
	A=qube_7aa7c52dd2.sparta_2ebbb966d2(B);A[_D]=12;H=qube_7aa7c52dd2.sparta_86bdc57f92(B.user);A.update(H);A[_E]=_A;F=E[_G];A[_F]=F.project_path;A[_H]=0 if E[_C]==1 else 1;A[_I]=F.notebook_id;A[_J]=F.name;A[_K]=B.user.is_anonymous;return render(B,'dist/project/notebook/notebookDetached.html',A)