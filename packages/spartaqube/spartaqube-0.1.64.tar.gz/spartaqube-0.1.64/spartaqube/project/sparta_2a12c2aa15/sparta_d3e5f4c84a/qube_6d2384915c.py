_A='menuBar'
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
from project.sparta_6d49f7e4f5.sparta_5adaec37f1 import qube_512fd42fef as qube_512fd42fef
from project.sparta_6d49f7e4f5.sparta_93fbedec69 import qube_f2c5d89efa as qube_f2c5d89efa
from project.sparta_6d49f7e4f5.sparta_bb74460757.qube_96ecfb2e32 import sparta_dac749eee2
@csrf_exempt
@sparta_c7cbfbc284
@login_required(redirect_field_name='login')
def sparta_baeac5fbfe(request):A=request;B=qube_a8d0eb6c62.sparta_b2f7a34b3f(A);B[_A]=-1;C=qube_a8d0eb6c62.sparta_96fb1a678d(A.user);B.update(C);return render(A,'dist/project/homepage/homepage.html',B)
@csrf_exempt
@sparta_c7cbfbc284
@login_required(redirect_field_name='login')
def sparta_d317c007a7(request,kernel_manager_uuid):
	D=kernel_manager_uuid;C=True;B=request;E=False
	if D is None:E=C
	else:
		F=qube_512fd42fef.sparta_c2cb610c53(B.user,D)
		if F is None:E=C
	if E:return sparta_baeac5fbfe(B)
	def H(path):
		A=Path(path)
		if not A.exists():A.mkdir(parents=C)
	K=sparta_dac749eee2();G=os.path.join(K,'kernel');H(G);I=os.path.join(G,D);H(I);J=os.path.join(I,'main.ipynb')
	if not os.path.exists(J):
		L=qube_f2c5d89efa.sparta_e1c349b9a0()
		with open(J,'w')as M:M.write(json.dumps(L))
	A=qube_a8d0eb6c62.sparta_b2f7a34b3f(B);A['default_project_path']=G;A[_A]=-1;N=qube_a8d0eb6c62.sparta_96fb1a678d(B.user);A.update(N);A['kernel_name']=F.name;A['kernelManagerUUID']=F.kernel_manager_uuid;A['bCodeMirror']=C;A['bPublicUser']=B.user.is_anonymous;return render(B,'dist/project/sqKernelNotebook/sqKernelNotebook.html',A)