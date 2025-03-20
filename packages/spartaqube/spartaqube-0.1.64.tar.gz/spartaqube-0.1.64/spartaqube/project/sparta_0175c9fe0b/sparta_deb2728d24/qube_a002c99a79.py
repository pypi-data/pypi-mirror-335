_I='error.txt'
_H='zipName'
_G='utf-8'
_F='attachment; filename={0}'
_E='appId'
_D='res'
_C='Content-Disposition'
_B='projectPath'
_A='jsonData'
import json,base64
from django.http import HttpResponse,Http404
from django.views.decorators.csrf import csrf_exempt
from project.sparta_6d49f7e4f5.sparta_6dd228cb73 import qube_b51aa9d54d as qube_b51aa9d54d
from project.sparta_6d49f7e4f5.sparta_6dd228cb73 import qube_e04f100d0b as qube_e04f100d0b
from project.sparta_6d49f7e4f5.sparta_bb74460757 import qube_795f848f90 as qube_795f848f90
from project.sparta_6d49f7e4f5.sparta_03569db088.qube_9fc342787d import sparta_7a6dbbc232
@csrf_exempt
@sparta_7a6dbbc232
def sparta_f3b2e4ec5e(request):
	D='files[]';A=request;E=A.POST.dict();B=A.FILES
	if D in B:C=qube_b51aa9d54d.sparta_2e399aac1b(E,A.user,B[D])
	else:C={_D:1}
	F=json.dumps(C);return HttpResponse(F)
@csrf_exempt
@sparta_7a6dbbc232
def sparta_063fd650db(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=qube_b51aa9d54d.sparta_b78044e02e(C,A.user);E=json.dumps(D);return HttpResponse(E)
@csrf_exempt
@sparta_7a6dbbc232
def sparta_3e24bdb119(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=qube_b51aa9d54d.sparta_9541b2afd1(C,A.user);E=json.dumps(D);return HttpResponse(E)
@csrf_exempt
@sparta_7a6dbbc232
def sparta_e13b85e256(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=qube_b51aa9d54d.sparta_244304365f(C,A.user);E=json.dumps(D);return HttpResponse(E)
@csrf_exempt
@sparta_7a6dbbc232
def sparta_0fe9a30b7f(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=qube_e04f100d0b.sparta_1cd0b83713(C,A.user);E=json.dumps(D);return HttpResponse(E)
@csrf_exempt
@sparta_7a6dbbc232
def sparta_85fa3f11ab(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=qube_b51aa9d54d.sparta_4c6919e31e(C,A.user);E=json.dumps(D);return HttpResponse(E)
@csrf_exempt
@sparta_7a6dbbc232
def sparta_835fcbf8a0(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=qube_b51aa9d54d.sparta_21ba8bc7bc(C,A.user);E=json.dumps(D);return HttpResponse(E)
@csrf_exempt
@sparta_7a6dbbc232
def sparta_1029ac619c(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=qube_b51aa9d54d.sparta_32c9d4c77a(C,A.user);E=json.dumps(D);return HttpResponse(E)
@csrf_exempt
@sparta_7a6dbbc232
def sparta_ebdf3f66a1(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=qube_b51aa9d54d.sparta_9d9050967d(C,A.user);E=json.dumps(D);return HttpResponse(E)
@csrf_exempt
@sparta_7a6dbbc232
def sparta_65d4ad5dcd(request):
	F='filePath';E='fileName';A=request;B=A.GET[E];G=A.GET[F];H=A.GET[_B];I=A.GET[_E];J={E:B,F:G,_E:I,_B:base64.b64decode(H).decode(_G)};C=qube_b51aa9d54d.sparta_05eb96beda(J,A.user)
	if C[_D]==1:
		try:
			with open(C['fullPath'],'rb')as K:D=HttpResponse(K.read(),content_type='application/force-download');D[_C]='attachment; filename='+str(B);return D
		except Exception as L:pass
	raise Http404
@csrf_exempt
@sparta_7a6dbbc232
def sparta_fb5b0d0c30(request):
	E='folderName';B=request;F=B.GET[_B];D=B.GET[E];G={_B:base64.b64decode(F).decode(_G),E:D};C=qube_b51aa9d54d.sparta_bf1a5c5a19(G,B.user)
	if C[_D]==1:H=C['zip'];I=C[_H];A=HttpResponse();A.write(H.getvalue());A[_C]=_F.format(f"{I}.zip")
	else:A=HttpResponse();J=f"Could not download the folder {D}, please try again";K=_I;A.write(J);A[_C]=_F.format(K)
	return A
@csrf_exempt
@sparta_7a6dbbc232
def sparta_b295948717(request):
	B=request;D=B.GET[_E];E=B.GET[_B];F={_E:D,_B:base64.b64decode(E).decode(_G)};C=qube_b51aa9d54d.sparta_da93193950(F,B.user)
	if C[_D]==1:G=C['zip'];H=C[_H];A=HttpResponse();A.write(G.getvalue());A[_C]=_F.format(f"{H}.zip")
	else:A=HttpResponse();I='Could not download the application, please try again';J=_I;A.write(I);A[_C]=_F.format(J)
	return A