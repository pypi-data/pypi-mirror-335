_O='serialized_data'
_N='has_access'
_M='plot_name'
_L='plot_chart_id'
_K='dist/project/plot-db/plotDB.html'
_J='edit_chart_id'
_I='edit'
_H='plot_db_chart_obj'
_G=False
_F='login'
_E='-1'
_D='bCodeMirror'
_C='menuBar'
_B=None
_A=True
import json,base64
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
import project.sparta_d3863a192d.sparta_3c800a8540.qube_a8d0eb6c62 as qube_a8d0eb6c62
from project.sparta_6d49f7e4f5.sparta_03569db088.qube_9fc342787d import sparta_c7cbfbc284
from project.sparta_6d49f7e4f5.sparta_eed2ac8b74 import qube_f98e616a62 as qube_f98e616a62
from project.sparta_6d49f7e4f5.sparta_d35bb0bd9f import qube_18e798f08e as qube_18e798f08e
@csrf_exempt
@sparta_c7cbfbc284
@login_required(redirect_field_name=_F)
def sparta_3641dce7b5(request):
	B=request;C=B.GET.get(_I)
	if C is _B:C=_E
	A=qube_a8d0eb6c62.sparta_b2f7a34b3f(B);A[_C]=7;D=qube_a8d0eb6c62.sparta_96fb1a678d(B.user);A.update(D);A[_D]=_A;A[_J]=C;return render(B,_K,A)
@csrf_exempt
@sparta_c7cbfbc284
@login_required(redirect_field_name=_F)
def sparta_bc19e0bf6f(request):
	B=request;C=B.GET.get(_I)
	if C is _B:C=_E
	A=qube_a8d0eb6c62.sparta_b2f7a34b3f(B);A[_C]=10;D=qube_a8d0eb6c62.sparta_96fb1a678d(B.user);A.update(D);A[_D]=_A;A[_J]=C;return render(B,_K,A)
@csrf_exempt
@sparta_c7cbfbc284
@login_required(redirect_field_name=_F)
def sparta_6c9eec6d01(request):
	B=request;C=B.GET.get(_I)
	if C is _B:C=_E
	A=qube_a8d0eb6c62.sparta_b2f7a34b3f(B);A[_C]=11;D=qube_a8d0eb6c62.sparta_96fb1a678d(B.user);A.update(D);A[_D]=_A;A[_J]=C;return render(B,_K,A)
@csrf_exempt
@sparta_c7cbfbc284
@login_required(redirect_field_name=_F)
def sparta_0958fa4a40(request):
	A=request;C=A.GET.get('id');D=_G
	if C is _B:D=_A
	else:E=qube_f98e616a62.sparta_ca3307d6b0(C,A.user);D=not E[_N]
	if D:return sparta_3641dce7b5(A)
	B=qube_a8d0eb6c62.sparta_b2f7a34b3f(A);B[_C]=7;F=qube_a8d0eb6c62.sparta_96fb1a678d(A.user);B.update(F);B[_D]=_A;B[_L]=C;G=E[_H];B[_M]=G.name;return render(A,'dist/project/plot-db/plotFull.html',B)
@csrf_exempt
@sparta_c7cbfbc284
def sparta_a23ed436ee(request,id,api_token_id=_B):
	A=request
	if id is _B:B=A.GET.get('id')
	else:B=id
	return plot_widget_func(A,B)
@csrf_exempt
@sparta_c7cbfbc284
def sparta_cdb4bc050d(request,dashboard_id,id,password):
	A=request
	if id is _B:B=A.GET.get('id')
	else:B=id
	C=base64.b64decode(password).decode();return plot_widget_func(A,B,dashboard_id=dashboard_id,dashboard_password=C)
@csrf_exempt
@sparta_c7cbfbc284
def sparta_4fd1c79776(request,widget_id,session_id,api_token_id):return plot_widget_func(request,widget_id,session_id)
def plot_widget_func(request,plot_chart_id,session=_E,dashboard_id=_E,token_permission='',dashboard_password=_B):
	K='token_permission';I=dashboard_id;H=plot_chart_id;G='res';E=token_permission;D=request;C=_G
	if H is _B:C=_A
	else:
		B=qube_f98e616a62.sparta_cfe7faed62(H,D.user);F=B[G]
		if F==-1:C=_A
	if C:
		if I!=_E:
			B=qube_18e798f08e.has_plot_db_access(I,H,D.user,dashboard_password);F=B[G]
			if F==1:E=B[K];C=_G
	if C:
		if len(E)>0:
			B=qube_f98e616a62.sparta_7cbd0158c5(E);F=B[G]
			if F==1:C=_G
	if C:return sparta_3641dce7b5(D)
	A=qube_a8d0eb6c62.sparta_b2f7a34b3f(D);A[_C]=7;L=qube_a8d0eb6c62.sparta_96fb1a678d(D.user);A.update(L);A[_D]=_A;J=B[_H];A['b_require_password']=0 if B[G]==1 else 1;A[_L]=J.plot_chart_id;A[_M]=J.name;A['session']=str(session);A['is_dashboard_widget']=1 if I!=_E else 0;A['is_token']=1 if len(E)>0 else 0;A[K]=str(E);return render(D,'dist/project/plot-db/widgets.html',A)
@csrf_exempt
def sparta_0c3bad999e(request,token):return plot_widget_func(request,plot_chart_id=_B,token_permission=token)
@csrf_exempt
@sparta_c7cbfbc284
def sparta_c79e8cd7c3(request):B=request;A=qube_a8d0eb6c62.sparta_b2f7a34b3f(B);A[_C]=7;C=qube_a8d0eb6c62.sparta_96fb1a678d(B.user);A.update(C);A[_D]=_A;A[_O]=B.POST.get('data');return render(B,'dist/project/plot-db/plotGUI.html',A)
@csrf_exempt
@sparta_c7cbfbc284
@login_required(redirect_field_name=_F)
def sparta_e5425a535b(request,id):
	K=',\n    ';B=request;C=id;F=_G
	if C is _B:F=_A
	else:G=qube_f98e616a62.sparta_ca3307d6b0(C,B.user);F=not G[_N]
	if F:return sparta_3641dce7b5(B)
	L=qube_f98e616a62.sparta_bf6fdc1e59(G[_H]);D='';H=0
	for(E,I)in L.items():
		if H>0:D+=K
		if I==1:D+=f"{E}=input_{E}"
		else:M=str(K.join([f"input_{E}_{A}"for A in range(I)]));D+=f"{E}=[{M}]"
		H+=1
	J=f"'{C}'";N=f"\n    {J}\n";O=f"Spartaqube().get_widget({N})";P=f"\n    {J},\n    {D}\n";Q=f"Spartaqube().plot({P})";A=qube_a8d0eb6c62.sparta_b2f7a34b3f(B);A[_C]=7;R=qube_a8d0eb6c62.sparta_96fb1a678d(B.user);A.update(R);A[_D]=_A;A[_L]=C;S=G[_H];A[_M]=S.name;A['plot_data_cmd']=O;A['plot_data_cmd_inputs']=Q;return render(B,'dist/project/plot-db/plotGUISaved.html',A)
@csrf_exempt
@sparta_c7cbfbc284
def sparta_52eb31e329(request,json_vars_html):B=request;A=qube_a8d0eb6c62.sparta_b2f7a34b3f(B);A[_C]=7;C=qube_a8d0eb6c62.sparta_96fb1a678d(B.user);A.update(C);A[_D]=_A;A.update(json.loads(json_vars_html));A[_O]=B.POST.get('data');return render(B,'dist/project/plot-db/plotAPI.html',A)