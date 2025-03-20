_C='bCodeMirror'
_B='menuBar'
_A=True
import os,json,getpass,platform
from pathlib import Path
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
import project.sparta_d3863a192d.sparta_3c800a8540.qube_a8d0eb6c62 as qube_a8d0eb6c62
from project.sparta_6d49f7e4f5.sparta_03569db088.qube_9fc342787d import sparta_c7cbfbc284
from project.sparta_6d49f7e4f5.sparta_eed2ac8b74 import qube_f98e616a62 as qube_f98e616a62
from project.sparta_6d49f7e4f5.sparta_d35bb0bd9f import qube_18e798f08e as qube_18e798f08e
from project.sparta_6d49f7e4f5.sparta_bb74460757.qube_96ecfb2e32 import sparta_dac749eee2
@csrf_exempt
@sparta_c7cbfbc284
@login_required(redirect_field_name='login')
def sparta_7dd0f17b46(request):
	B=request;C=B.GET.get('edit')
	if C is None:C='-1'
	A=qube_a8d0eb6c62.sparta_b2f7a34b3f(B);A[_B]=9;E=qube_a8d0eb6c62.sparta_96fb1a678d(B.user);A.update(E);A[_C]=_A;A['edit_chart_id']=C
	def F(path):
		A=Path(path)
		if not A.exists():A.mkdir(parents=_A)
	G=sparta_dac749eee2();D=os.path.join(G,'dashboard');F(D);A['default_project_path']=D;return render(B,'dist/project/dashboard/dashboard.html',A)
@csrf_exempt
def sparta_ad96559d3a(request,id):
	A=request
	if id is None:B=A.GET.get('id')
	else:B=id
	return sparta_f4f7870272(A,B)
def sparta_f4f7870272(request,dashboard_id,session='-1'):
	G='res';E=dashboard_id;B=request;C=False
	if E is None:C=_A
	else:
		D=qube_18e798f08e.has_dashboard_access(E,B.user);H=D[G]
		if H==-1:C=_A
	if C:return sparta_7dd0f17b46(B)
	A=qube_a8d0eb6c62.sparta_b2f7a34b3f(B);A[_B]=9;I=qube_a8d0eb6c62.sparta_96fb1a678d(B.user);A.update(I);A[_C]=_A;F=D['dashboard_obj'];A['b_require_password']=0 if D[G]==1 else 1;A['dashboard_id']=F.dashboard_id;A['dashboard_name']=F.name;A['bPublicUser']=B.user.is_anonymous;A['session']=str(session);return render(B,'dist/project/dashboard/dashboardRun.html',A)