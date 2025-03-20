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
import project.sparta_76336d2b79.sparta_76426419cc.qube_7aa7c52dd2 as qube_7aa7c52dd2
from project.sparta_3bc15131c6.sparta_6d9c27d78c.qube_9777884b7b import sparta_34d9a3cc83
from project.sparta_3bc15131c6.sparta_59738bc23c import qube_935d18f40e as qube_935d18f40e
from project.sparta_3bc15131c6.sparta_0d2990c769.qube_886837873c import sparta_235d77fd71
@csrf_exempt
@sparta_34d9a3cc83
@login_required(redirect_field_name='login')
def sparta_bbec059895(request):
	B=request
	if not conf_settings.IS_DEV_VIEW_ENABLED:A=qube_7aa7c52dd2.sparta_2ebbb966d2(B);return render(B,_D,A)
	qube_935d18f40e.sparta_0aeb474dfe();A=qube_7aa7c52dd2.sparta_2ebbb966d2(B);A[_E]=12;D=qube_7aa7c52dd2.sparta_86bdc57f92(B.user);A.update(D);A[_F]=_A
	def E(path):
		A=Path(path)
		if not A.exists():A.mkdir(parents=_A)
	F=sparta_235d77fd71();C=os.path.join(F,'developer');E(C);A[_G]=C;return render(B,'dist/project/developer/developer.html',A)
@csrf_exempt
def sparta_9bb4683b76(request,id):
	B=request
	if not conf_settings.IS_DEV_VIEW_ENABLED:A=qube_7aa7c52dd2.sparta_2ebbb966d2(B);return render(B,_D,A)
	if id is _B:C=B.GET.get('id')
	else:C=id
	D=False
	if C is _B:D=_A
	else:
		E=qube_935d18f40e.has_developer_access(C,B.user);G=E[_C]
		if G==-1:D=_A
	if D:return sparta_bbec059895(B)
	A=qube_7aa7c52dd2.sparta_2ebbb966d2(B);A[_E]=12;H=qube_7aa7c52dd2.sparta_86bdc57f92(B.user);A.update(H);A[_F]=_A;F=E[_H];A[_G]=F.project_path;A[_I]=0 if E[_C]==1 else 1;A[_J]=F.developer_id;A[_K]=F.name;A[_L]=B.user.is_anonymous;return render(B,'dist/project/developer/developerRun.html',A)
@csrf_exempt
@sparta_34d9a3cc83
@login_required(redirect_field_name='login')
def sparta_4f76f881b1(request,id):
	B=request
	if not conf_settings.IS_DEV_VIEW_ENABLED:A=qube_7aa7c52dd2.sparta_2ebbb966d2(B);return render(B,_D,A)
	if id is _B:C=B.GET.get('id')
	else:C=id
	D=False
	if C is _B:D=_A
	else:
		E=qube_935d18f40e.has_developer_access(C,B.user);G=E[_C]
		if G==-1:D=_A
	if D:return sparta_bbec059895(B)
	A=qube_7aa7c52dd2.sparta_2ebbb966d2(B);A[_E]=12;H=qube_7aa7c52dd2.sparta_86bdc57f92(B.user);A.update(H);A[_F]=_A;F=E[_H];A[_G]=F.project_path;A[_I]=0 if E[_C]==1 else 1;A[_J]=F.developer_id;A[_K]=F.name;A[_L]=B.user.is_anonymous;return render(B,'dist/project/developer/developerDetached.html',A)
def sparta_3b6b58c49e(request,project_path,file_name):A=project_path;A=unquote(A);return serve(request,file_name,document_root=A)