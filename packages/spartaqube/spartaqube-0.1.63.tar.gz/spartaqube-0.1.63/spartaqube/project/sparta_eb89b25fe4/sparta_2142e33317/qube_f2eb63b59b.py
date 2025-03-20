_E='Content-Disposition'
_D='utf-8'
_C='dashboardId'
_B='projectPath'
_A='jsonData'
import os,json,base64
from django.http import HttpResponse,Http404
from django.views.decorators.csrf import csrf_exempt
from project.sparta_3bc15131c6.sparta_00d4634adc import qube_966210bc8e as qube_966210bc8e
from project.sparta_3bc15131c6.sparta_00d4634adc import qube_d70bb96a2a as qube_d70bb96a2a
from project.sparta_3bc15131c6.sparta_bf064088d7 import qube_b54b4f1c5e as qube_b54b4f1c5e
from project.sparta_3bc15131c6.sparta_6d9c27d78c.qube_9777884b7b import sparta_a7a1f51ac1,sparta_20bcad3447
@csrf_exempt
def sparta_d654b7f355(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=qube_966210bc8e.sparta_d654b7f355(C,A.user);E=json.dumps(D);return HttpResponse(E)
@csrf_exempt
@sparta_a7a1f51ac1
def sparta_ca8928d2b6(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=qube_966210bc8e.sparta_ca8928d2b6(C,A.user);E=json.dumps(D);return HttpResponse(E)
@csrf_exempt
@sparta_a7a1f51ac1
def sparta_5e464714a0(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=qube_966210bc8e.sparta_5e464714a0(C,A.user);E=json.dumps(D);return HttpResponse(E)
@csrf_exempt
@sparta_a7a1f51ac1
def sparta_d5de2f9ff6(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=qube_966210bc8e.sparta_d5de2f9ff6(C,A.user);E=json.dumps(D);return HttpResponse(E)
@csrf_exempt
@sparta_a7a1f51ac1
@sparta_20bcad3447
def sparta_a272b20192(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=qube_966210bc8e.sparta_a272b20192(C,A.user);E=json.dumps(D);return HttpResponse(E)
@csrf_exempt
@sparta_a7a1f51ac1
def sparta_51a886914b(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=qube_966210bc8e.sparta_51a886914b(C,A.user);E=json.dumps(D);return HttpResponse(E)
@csrf_exempt
@sparta_a7a1f51ac1
def sparta_1aa6bbd752(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=qube_966210bc8e.sparta_1aa6bbd752(C,A.user);E=json.dumps(D);return HttpResponse(E)
@csrf_exempt
@sparta_a7a1f51ac1
def sparta_7c0d141553(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=qube_966210bc8e.sparta_7c0d141553(C,A.user);E=json.dumps(D);return HttpResponse(E)
@csrf_exempt
@sparta_a7a1f51ac1
def sparta_d1abe206e8(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=qube_966210bc8e.sparta_d1abe206e8(C,A.user);E=json.dumps(D);return HttpResponse(E)
@csrf_exempt
@sparta_a7a1f51ac1
def sparta_15c1fdacdc(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=qube_966210bc8e.sparta_15c1fdacdc(C,A.user);E=json.dumps(D);return HttpResponse(E)
@csrf_exempt
@sparta_a7a1f51ac1
def sparta_0c463953af(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=qube_966210bc8e.dashboard_project_explorer_delete_multiple_resources(C,A.user);E=json.dumps(D);return HttpResponse(E)
@csrf_exempt
@sparta_a7a1f51ac1
def sparta_f10ed80b9a(request):A=request;B=A.POST.dict();C=A.FILES;D=qube_966210bc8e.sparta_f10ed80b9a(B,A.user,C['files[]']);E=json.dumps(D);return HttpResponse(E)
def sparta_309143671b(path):
	A=path;A=os.path.normpath(A)
	if os.path.isfile(A):A=os.path.dirname(A)
	return os.path.basename(A)
def sparta_72128b0fee(path):A=path;A=os.path.normpath(A);return os.path.basename(A)
@csrf_exempt
@sparta_a7a1f51ac1
def sparta_4206b280db(request):
	E='pathResource';A=request;B=A.GET[E];B=base64.b64decode(B).decode(_D);F=A.GET[_B];G=A.GET[_C];H=sparta_72128b0fee(B);I={E:B,_C:G,_B:base64.b64decode(F).decode(_D)};C=qube_966210bc8e.sparta_014a3b6086(I,A.user)
	if C['res']==1:
		try:
			with open(C['fullPath'],'rb')as J:D=HttpResponse(J.read(),content_type='application/force-download');D[_E]='attachment; filename='+str(H);return D
		except Exception as K:pass
	raise Http404
@csrf_exempt
@sparta_a7a1f51ac1
def sparta_c2c508795c(request):
	D='attachment; filename={0}';B=request;E=B.GET[_C];F=B.GET[_B];G={_C:E,_B:base64.b64decode(F).decode(_D)};C=qube_966210bc8e.sparta_96a1d5b9ee(G,B.user)
	if C['res']==1:H=C['zip'];I=C['zipName'];A=HttpResponse();A.write(H.getvalue());A[_E]=D.format(f"{I}.zip")
	else:A=HttpResponse();J='Could not download the application, please try again';K='error.txt';A.write(J);A[_E]=D.format(K)
	return A
@csrf_exempt
@sparta_a7a1f51ac1
@sparta_20bcad3447
def sparta_e1053a671f(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=qube_d70bb96a2a.sparta_e1053a671f(C,A.user);E=json.dumps(D);return HttpResponse(E)
@csrf_exempt
@sparta_a7a1f51ac1
@sparta_20bcad3447
def sparta_d1d37335d8(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=qube_d70bb96a2a.sparta_d1d37335d8(C,A.user);E=json.dumps(D);return HttpResponse(E)
@csrf_exempt
@sparta_a7a1f51ac1
@sparta_20bcad3447
def sparta_7326f77f9f(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=qube_d70bb96a2a.sparta_7326f77f9f(C,A.user);E=json.dumps(D);return HttpResponse(E)
@csrf_exempt
@sparta_a7a1f51ac1
@sparta_20bcad3447
def sparta_4fdb5a74fe(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=qube_d70bb96a2a.sparta_4fdb5a74fe(C,A.user);E=json.dumps(D);return HttpResponse(E)
@csrf_exempt
@sparta_a7a1f51ac1
@sparta_20bcad3447
def sparta_65e01b91fd(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=qube_d70bb96a2a.sparta_65e01b91fd(C,A.user);E=json.dumps(D);return HttpResponse(E)
@csrf_exempt
@sparta_a7a1f51ac1
@sparta_20bcad3447
def sparta_2059baaa39(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=qube_d70bb96a2a.sparta_2059baaa39(C,A.user);E=json.dumps(D);return HttpResponse(E)
@csrf_exempt
@sparta_a7a1f51ac1
@sparta_20bcad3447
def sparta_ac2fa6c638(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=qube_d70bb96a2a.sparta_ac2fa6c638(C,A.user);E=json.dumps(D);return HttpResponse(E)
@csrf_exempt
@sparta_a7a1f51ac1
@sparta_20bcad3447
def sparta_140d6def9c(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=qube_d70bb96a2a.sparta_140d6def9c(C,A.user);E=json.dumps(D);return HttpResponse(E)
@csrf_exempt
@sparta_a7a1f51ac1
@sparta_20bcad3447
def sparta_cc55b55457(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=qube_d70bb96a2a.sparta_cc55b55457(C,A.user);E=json.dumps(D);return HttpResponse(E)
@csrf_exempt
@sparta_a7a1f51ac1
@sparta_20bcad3447
def sparta_e46db117be(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=qube_d70bb96a2a.sparta_e46db117be(C,A.user);E=json.dumps(D);return HttpResponse(E)
@csrf_exempt
@sparta_a7a1f51ac1
@sparta_20bcad3447
def sparta_c134ee8ea6(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=qube_d70bb96a2a.sparta_c134ee8ea6(C,A.user);E=json.dumps(D);return HttpResponse(E)
@csrf_exempt
@sparta_a7a1f51ac1
@sparta_20bcad3447
def sparta_2faee59bed(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=qube_d70bb96a2a.sparta_2faee59bed(C,A.user);E=json.dumps(D);return HttpResponse(E)
@csrf_exempt
@sparta_a7a1f51ac1
@sparta_20bcad3447
def sparta_bae1dad41a(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=qube_d70bb96a2a.sparta_bae1dad41a(C,A.user);E=json.dumps(D);return HttpResponse(E)
@csrf_exempt
@sparta_a7a1f51ac1
@sparta_20bcad3447
def sparta_33dfb5849e(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=qube_d70bb96a2a.sparta_33dfb5849e(C,A.user);E=json.dumps(D);return HttpResponse(E)