_C='bCodeMirror'
_B='menuBar'
_A=True
import os,json,getpass,platform
from pathlib import Path
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
import project.sparta_76336d2b79.sparta_76426419cc.qube_7aa7c52dd2 as qube_7aa7c52dd2
from project.sparta_3bc15131c6.sparta_6d9c27d78c.qube_9777884b7b import sparta_34d9a3cc83
from project.sparta_3bc15131c6.sparta_1ec16518f2 import qube_e27ca60edf as qube_e27ca60edf
from project.sparta_3bc15131c6.sparta_bf064088d7 import qube_b54b4f1c5e as qube_b54b4f1c5e
from project.sparta_3bc15131c6.sparta_0d2990c769.qube_886837873c import sparta_235d77fd71
@csrf_exempt
@sparta_34d9a3cc83
@login_required(redirect_field_name='login')
def sparta_df66d68fc4(request):
	B=request;C=B.GET.get('edit')
	if C is None:C='-1'
	A=qube_7aa7c52dd2.sparta_2ebbb966d2(B);A[_B]=9;E=qube_7aa7c52dd2.sparta_86bdc57f92(B.user);A.update(E);A[_C]=_A;A['edit_chart_id']=C
	def F(path):
		A=Path(path)
		if not A.exists():A.mkdir(parents=_A)
	G=sparta_235d77fd71();D=os.path.join(G,'dashboard');F(D);A['default_project_path']=D;return render(B,'dist/project/dashboard/dashboard.html',A)
@csrf_exempt
def sparta_2e4971db34(request,id):
	A=request
	if id is None:B=A.GET.get('id')
	else:B=id
	return sparta_7369d50c38(A,B)
def sparta_7369d50c38(request,dashboard_id,session='-1'):
	G='res';E=dashboard_id;B=request;C=False
	if E is None:C=_A
	else:
		D=qube_b54b4f1c5e.has_dashboard_access(E,B.user);H=D[G]
		if H==-1:C=_A
	if C:return sparta_df66d68fc4(B)
	A=qube_7aa7c52dd2.sparta_2ebbb966d2(B);A[_B]=9;I=qube_7aa7c52dd2.sparta_86bdc57f92(B.user);A.update(I);A[_C]=_A;F=D['dashboard_obj'];A['b_require_password']=0 if D[G]==1 else 1;A['dashboard_id']=F.dashboard_id;A['dashboard_name']=F.name;A['bPublicUser']=B.user.is_anonymous;A['session']=str(session);return render(B,'dist/project/dashboard/dashboardRun.html',A)