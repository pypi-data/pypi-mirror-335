_E='Content-Disposition'
_D='utf-8'
_C='dashboardId'
_B='projectPath'
_A='jsonData'
import os,json,base64
from django.http import HttpResponse,Http404
from django.views.decorators.csrf import csrf_exempt
from project.sparta_6d49f7e4f5.sparta_93fbedec69 import qube_029182269b as qube_029182269b
from project.sparta_6d49f7e4f5.sparta_93fbedec69 import qube_44d243048c as qube_44d243048c
from project.sparta_6d49f7e4f5.sparta_d35bb0bd9f import qube_18e798f08e as qube_18e798f08e
from project.sparta_6d49f7e4f5.sparta_03569db088.qube_9fc342787d import sparta_7a6dbbc232,sparta_52d37e03fb
@csrf_exempt
def sparta_897dc54071(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=qube_029182269b.sparta_897dc54071(C,A.user);E=json.dumps(D);return HttpResponse(E)
@csrf_exempt
@sparta_7a6dbbc232
def sparta_c994301ce7(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=qube_029182269b.sparta_c994301ce7(C,A.user);E=json.dumps(D);return HttpResponse(E)
@csrf_exempt
@sparta_7a6dbbc232
def sparta_8fe5c1e571(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=qube_029182269b.sparta_8fe5c1e571(C,A.user);E=json.dumps(D);return HttpResponse(E)
@csrf_exempt
@sparta_7a6dbbc232
def sparta_9a511a2d9e(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=qube_029182269b.sparta_9a511a2d9e(C,A.user);E=json.dumps(D);return HttpResponse(E)
@csrf_exempt
@sparta_7a6dbbc232
@sparta_52d37e03fb
def sparta_12d4428936(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=qube_029182269b.sparta_12d4428936(C,A.user);E=json.dumps(D);return HttpResponse(E)
@csrf_exempt
@sparta_7a6dbbc232
def sparta_98a51f28e5(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=qube_029182269b.sparta_98a51f28e5(C,A.user);E=json.dumps(D);return HttpResponse(E)
@csrf_exempt
@sparta_7a6dbbc232
def sparta_a65575fdf4(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=qube_029182269b.sparta_a65575fdf4(C,A.user);E=json.dumps(D);return HttpResponse(E)
@csrf_exempt
@sparta_7a6dbbc232
def sparta_89df7af16a(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=qube_029182269b.sparta_89df7af16a(C,A.user);E=json.dumps(D);return HttpResponse(E)
@csrf_exempt
@sparta_7a6dbbc232
def sparta_38737834ec(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=qube_029182269b.sparta_38737834ec(C,A.user);E=json.dumps(D);return HttpResponse(E)
@csrf_exempt
@sparta_7a6dbbc232
def sparta_0aac3e6ca2(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=qube_029182269b.sparta_0aac3e6ca2(C,A.user);E=json.dumps(D);return HttpResponse(E)
@csrf_exempt
@sparta_7a6dbbc232
def sparta_25fa50abdb(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=qube_029182269b.dashboard_project_explorer_delete_multiple_resources(C,A.user);E=json.dumps(D);return HttpResponse(E)
@csrf_exempt
@sparta_7a6dbbc232
def sparta_9a807e9753(request):A=request;B=A.POST.dict();C=A.FILES;D=qube_029182269b.sparta_9a807e9753(B,A.user,C['files[]']);E=json.dumps(D);return HttpResponse(E)
def sparta_0a0f8a0d2e(path):
	A=path;A=os.path.normpath(A)
	if os.path.isfile(A):A=os.path.dirname(A)
	return os.path.basename(A)
def sparta_6c3cd095bf(path):A=path;A=os.path.normpath(A);return os.path.basename(A)
@csrf_exempt
@sparta_7a6dbbc232
def sparta_18ec647ec7(request):
	E='pathResource';A=request;B=A.GET[E];B=base64.b64decode(B).decode(_D);F=A.GET[_B];G=A.GET[_C];H=sparta_6c3cd095bf(B);I={E:B,_C:G,_B:base64.b64decode(F).decode(_D)};C=qube_029182269b.sparta_05eb96beda(I,A.user)
	if C['res']==1:
		try:
			with open(C['fullPath'],'rb')as J:D=HttpResponse(J.read(),content_type='application/force-download');D[_E]='attachment; filename='+str(H);return D
		except Exception as K:pass
	raise Http404
@csrf_exempt
@sparta_7a6dbbc232
def sparta_3aeef116cb(request):
	D='attachment; filename={0}';B=request;E=B.GET[_C];F=B.GET[_B];G={_C:E,_B:base64.b64decode(F).decode(_D)};C=qube_029182269b.sparta_da93193950(G,B.user)
	if C['res']==1:H=C['zip'];I=C['zipName'];A=HttpResponse();A.write(H.getvalue());A[_E]=D.format(f"{I}.zip")
	else:A=HttpResponse();J='Could not download the application, please try again';K='error.txt';A.write(J);A[_E]=D.format(K)
	return A
@csrf_exempt
@sparta_7a6dbbc232
@sparta_52d37e03fb
def sparta_b9ae4ab7a8(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=qube_44d243048c.sparta_b9ae4ab7a8(C,A.user);E=json.dumps(D);return HttpResponse(E)
@csrf_exempt
@sparta_7a6dbbc232
@sparta_52d37e03fb
def sparta_a2c7339f85(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=qube_44d243048c.sparta_a2c7339f85(C,A.user);E=json.dumps(D);return HttpResponse(E)
@csrf_exempt
@sparta_7a6dbbc232
@sparta_52d37e03fb
def sparta_dd82382944(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=qube_44d243048c.sparta_dd82382944(C,A.user);E=json.dumps(D);return HttpResponse(E)
@csrf_exempt
@sparta_7a6dbbc232
@sparta_52d37e03fb
def sparta_96b8ff4957(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=qube_44d243048c.sparta_96b8ff4957(C,A.user);E=json.dumps(D);return HttpResponse(E)
@csrf_exempt
@sparta_7a6dbbc232
@sparta_52d37e03fb
def sparta_70dcdba7bc(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=qube_44d243048c.sparta_70dcdba7bc(C,A.user);E=json.dumps(D);return HttpResponse(E)
@csrf_exempt
@sparta_7a6dbbc232
@sparta_52d37e03fb
def sparta_c56d1eccec(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=qube_44d243048c.sparta_c56d1eccec(C,A.user);E=json.dumps(D);return HttpResponse(E)
@csrf_exempt
@sparta_7a6dbbc232
@sparta_52d37e03fb
def sparta_423f25e0b2(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=qube_44d243048c.sparta_423f25e0b2(C,A.user);E=json.dumps(D);return HttpResponse(E)
@csrf_exempt
@sparta_7a6dbbc232
@sparta_52d37e03fb
def sparta_9cf6873229(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=qube_44d243048c.sparta_9cf6873229(C,A.user);E=json.dumps(D);return HttpResponse(E)
@csrf_exempt
@sparta_7a6dbbc232
@sparta_52d37e03fb
def sparta_f089c56e9e(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=qube_44d243048c.sparta_f089c56e9e(C,A.user);E=json.dumps(D);return HttpResponse(E)
@csrf_exempt
@sparta_7a6dbbc232
@sparta_52d37e03fb
def sparta_388ed114be(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=qube_44d243048c.sparta_388ed114be(C,A.user);E=json.dumps(D);return HttpResponse(E)
@csrf_exempt
@sparta_7a6dbbc232
@sparta_52d37e03fb
def sparta_e22c688723(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=qube_44d243048c.sparta_e22c688723(C,A.user);E=json.dumps(D);return HttpResponse(E)
@csrf_exempt
@sparta_7a6dbbc232
@sparta_52d37e03fb
def sparta_83be851876(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=qube_44d243048c.sparta_83be851876(C,A.user);E=json.dumps(D);return HttpResponse(E)
@csrf_exempt
@sparta_7a6dbbc232
@sparta_52d37e03fb
def sparta_cc62f31a80(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=qube_44d243048c.sparta_cc62f31a80(C,A.user);E=json.dumps(D);return HttpResponse(E)
@csrf_exempt
@sparta_7a6dbbc232
@sparta_52d37e03fb
def sparta_083ed1c93d(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=qube_44d243048c.sparta_083ed1c93d(C,A.user);E=json.dumps(D);return HttpResponse(E)