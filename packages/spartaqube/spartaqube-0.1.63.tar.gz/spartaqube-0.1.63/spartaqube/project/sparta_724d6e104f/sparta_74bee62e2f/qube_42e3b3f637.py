_A='menuBar'
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
from project.sparta_3bc15131c6.sparta_e0bb3dc4e4 import qube_9d39f4b22f as qube_9d39f4b22f
from project.sparta_3bc15131c6.sparta_00d4634adc import qube_55479fa538 as qube_55479fa538
from project.sparta_3bc15131c6.sparta_0d2990c769.qube_886837873c import sparta_235d77fd71
@csrf_exempt
@sparta_34d9a3cc83
@login_required(redirect_field_name='login')
def sparta_8a72f21335(request):A=request;B=qube_7aa7c52dd2.sparta_2ebbb966d2(A);B[_A]=-1;C=qube_7aa7c52dd2.sparta_86bdc57f92(A.user);B.update(C);return render(A,'dist/project/homepage/homepage.html',B)
@csrf_exempt
@sparta_34d9a3cc83
@login_required(redirect_field_name='login')
def sparta_899c404206(request,kernel_manager_uuid):
	D=kernel_manager_uuid;C=True;B=request;E=False
	if D is None:E=C
	else:
		F=qube_9d39f4b22f.sparta_88e68c3ab9(B.user,D)
		if F is None:E=C
	if E:return sparta_8a72f21335(B)
	def H(path):
		A=Path(path)
		if not A.exists():A.mkdir(parents=C)
	K=sparta_235d77fd71();G=os.path.join(K,'kernel');H(G);I=os.path.join(G,D);H(I);J=os.path.join(I,'main.ipynb')
	if not os.path.exists(J):
		L=qube_55479fa538.sparta_0e68608e35()
		with open(J,'w')as M:M.write(json.dumps(L))
	A=qube_7aa7c52dd2.sparta_2ebbb966d2(B);A['default_project_path']=G;A[_A]=-1;N=qube_7aa7c52dd2.sparta_86bdc57f92(B.user);A.update(N);A['kernel_name']=F.name;A['kernelManagerUUID']=F.kernel_manager_uuid;A['bCodeMirror']=C;A['bPublicUser']=B.user.is_anonymous;return render(B,'dist/project/sqKernelNotebook/sqKernelNotebook.html',A)