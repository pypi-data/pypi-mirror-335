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
from project.sparta_3bc15131c6.sparta_9d237043e8 import qube_8b965784c7 as qube_8b965784c7
from project.sparta_3bc15131c6.sparta_9d237043e8 import qube_100ba84e1d as qube_100ba84e1d
from project.sparta_3bc15131c6.sparta_0d2990c769 import qube_48c282f85d as qube_48c282f85d
from project.sparta_3bc15131c6.sparta_6d9c27d78c.qube_9777884b7b import sparta_a7a1f51ac1
@csrf_exempt
@sparta_a7a1f51ac1
def sparta_7ac82e50b2(request):
	D='files[]';A=request;E=A.POST.dict();B=A.FILES
	if D in B:C=qube_8b965784c7.sparta_6acd351024(E,A.user,B[D])
	else:C={_D:1}
	F=json.dumps(C);return HttpResponse(F)
@csrf_exempt
@sparta_a7a1f51ac1
def sparta_66ae480114(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=qube_8b965784c7.sparta_1070f930c9(C,A.user);E=json.dumps(D);return HttpResponse(E)
@csrf_exempt
@sparta_a7a1f51ac1
def sparta_346dd76d4e(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=qube_8b965784c7.sparta_3a03ad39a1(C,A.user);E=json.dumps(D);return HttpResponse(E)
@csrf_exempt
@sparta_a7a1f51ac1
def sparta_3acedc53fd(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=qube_8b965784c7.sparta_065b06176d(C,A.user);E=json.dumps(D);return HttpResponse(E)
@csrf_exempt
@sparta_a7a1f51ac1
def sparta_b1a6ca16ae(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=qube_100ba84e1d.sparta_636346aaa6(C,A.user);E=json.dumps(D);return HttpResponse(E)
@csrf_exempt
@sparta_a7a1f51ac1
def sparta_6dfbb35c7b(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=qube_8b965784c7.sparta_a89369d351(C,A.user);E=json.dumps(D);return HttpResponse(E)
@csrf_exempt
@sparta_a7a1f51ac1
def sparta_4973136b72(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=qube_8b965784c7.sparta_cab38ee843(C,A.user);E=json.dumps(D);return HttpResponse(E)
@csrf_exempt
@sparta_a7a1f51ac1
def sparta_e8e3033c2e(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=qube_8b965784c7.sparta_36fcf5c36e(C,A.user);E=json.dumps(D);return HttpResponse(E)
@csrf_exempt
@sparta_a7a1f51ac1
def sparta_b5a2068a77(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=qube_8b965784c7.sparta_db55e9d081(C,A.user);E=json.dumps(D);return HttpResponse(E)
@csrf_exempt
@sparta_a7a1f51ac1
def sparta_92832a599e(request):
	F='filePath';E='fileName';A=request;B=A.GET[E];G=A.GET[F];H=A.GET[_B];I=A.GET[_E];J={E:B,F:G,_E:I,_B:base64.b64decode(H).decode(_G)};C=qube_8b965784c7.sparta_014a3b6086(J,A.user)
	if C[_D]==1:
		try:
			with open(C['fullPath'],'rb')as K:D=HttpResponse(K.read(),content_type='application/force-download');D[_C]='attachment; filename='+str(B);return D
		except Exception as L:pass
	raise Http404
@csrf_exempt
@sparta_a7a1f51ac1
def sparta_52083e8a9c(request):
	E='folderName';B=request;F=B.GET[_B];D=B.GET[E];G={_B:base64.b64decode(F).decode(_G),E:D};C=qube_8b965784c7.sparta_f26f00cefc(G,B.user)
	if C[_D]==1:H=C['zip'];I=C[_H];A=HttpResponse();A.write(H.getvalue());A[_C]=_F.format(f"{I}.zip")
	else:A=HttpResponse();J=f"Could not download the folder {D}, please try again";K=_I;A.write(J);A[_C]=_F.format(K)
	return A
@csrf_exempt
@sparta_a7a1f51ac1
def sparta_f9682ad048(request):
	B=request;D=B.GET[_E];E=B.GET[_B];F={_E:D,_B:base64.b64decode(E).decode(_G)};C=qube_8b965784c7.sparta_96a1d5b9ee(F,B.user)
	if C[_D]==1:G=C['zip'];H=C[_H];A=HttpResponse();A.write(G.getvalue());A[_C]=_F.format(f"{H}.zip")
	else:A=HttpResponse();I='Could not download the application, please try again';J=_I;A.write(I);A[_C]=_F.format(J)
	return A