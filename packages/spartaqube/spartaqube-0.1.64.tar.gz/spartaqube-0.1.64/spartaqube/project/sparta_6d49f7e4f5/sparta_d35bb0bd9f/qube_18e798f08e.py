_f='fullPath'
_e='thumbnail'
_d='static'
_c='previewImage'
_b='plotDBProgrammaticAttributes'
_a='itemId'
_Z='itemType'
_Y='gridConfig'
_X='dashboardSlug'
_W='isDashboardPublic'
_V='isDashboardExpose'
_U='dashboardDescription'
_T='mainIpynbFullPath'
_S='dashboardPassword'
_R='main_ipynb_fullpath'
_Q='json_data'
_P='is_public_dashboard'
_O='has_password'
_N='is_expose_dashboard'
_M='description'
_L='luminoLayout'
_K='hasDashboardPassword'
_J='dashboard'
_I='dashboardName'
_H='dashboard_id'
_G='dashboardId'
_F='errorMsg'
_E='dashboard_obj'
_D=False
_C=True
_B=None
_A='res'
import re,os,json,io,sys,base64,traceback,uuid
from django.db.models import Q
from django.utils.text import slugify
from datetime import datetime,timedelta
import pytz
UTC=pytz.utc
from project.models_spartaqube import Dashboard,DashboardShared,PlotDBChart,PlotDBPermission
from project.models import ShareRights
from project.sparta_6d49f7e4f5.sparta_c59310761b import qube_6ff33ab51c as qube_6ff33ab51c
from project.sparta_6d49f7e4f5.sparta_eed2ac8b74 import qube_a2a748f1f2 as qube_a2a748f1f2
from project.sparta_6d49f7e4f5.sparta_d0477f20f9.qube_c8e95923d2 import Connector as Connector
from project.sparta_6d49f7e4f5.sparta_eed2ac8b74.qube_f98e616a62 import sparta_984e2efb4d
from project.sparta_6d49f7e4f5.sparta_bb74460757.qube_74042b161e import sparta_9bd4d72961
from project.sparta_6d49f7e4f5.sparta_9baa585a8b import qube_547f95bdca as qube_547f95bdca
from project.sparta_6d49f7e4f5.sparta_bb74460757.qube_795f848f90 import sparta_cfece85c36
from project.sparta_6d49f7e4f5.sparta_93fbedec69 import qube_f2c5d89efa as qube_f2c5d89efa
from project.sparta_6d49f7e4f5.sparta_b607e9d9fc.qube_12d9a66acf import sparta_00b65c604c
from project.logger_config import logger
def sparta_366b4f8cf1(user_obj):
	A=qube_6ff33ab51c.sparta_03fbfe1583(user_obj)
	if len(A)>0:B=[A.user_group for A in A]
	else:B=[]
	return B
def sparta_778de77086(json_data,user_obj):
	K='%Y-%m-%d';J='Recently used';D=user_obj;F=sparta_366b4f8cf1(D)
	if len(F)>0:A=DashboardShared.objects.filter(Q(is_delete=0,user_group__in=F,dashboard__is_delete=0)|Q(is_delete=0,user=D,dashboard__is_delete=0))
	else:A=DashboardShared.objects.filter(is_delete=0,user=D,dashboard__is_delete=0)
	if A.count()>0:
		C=json_data.get('orderBy',J)
		if C==J:A=A.order_by('-dashboard__last_date_used')
		elif C=='Date desc':A=A.order_by('-dashboard__last_update')
		elif C=='Date asc':A=A.order_by('dashboard__last_update')
		elif C=='Name desc':A=A.order_by('-dashboard__name')
		elif C=='Name asc':A=A.order_by('dashboard__name')
	G=[]
	for E in A:
		B=E.dashboard;L=E.share_rights;H=_B
		try:H=str(B.last_update.strftime(K))
		except:pass
		I=_B
		try:I=str(B.date_created.strftime(K))
		except Exception as M:logger.debug(M)
		G.append({_H:B.dashboard_id,'name':B.name,'slug':B.slug,_M:B.description,_N:B.is_expose_dashboard,_O:B.has_password,_P:B.is_public_dashboard,'is_owner':E.is_owner,'has_write_rights':L.has_write_rights,'last_update':H,'date_created':I})
	return{_A:1,'dashboard_library':G}
def sparta_d68e4c0245(json_data,user_obj):
	E=json_data;C=user_obj;logger.debug(_Q);logger.debug(E);D=E[_G];G=E.get('modalPassword',_B)
	if not C.is_anonymous:
		F=Dashboard.objects.filter(dashboard_id__startswith=D,is_delete=_D).all()
		if F.count()==1:
			A=F[F.count()-1];D=A.dashboard_id;B=has_dashboard_access(D,C,password_dashboard=G)
			if B[_A]!=1:return{_A:B[_A],_F:B[_F]}
		else:return{_A:-1,_F:'Dashboard not found...'}
	else:
		B=has_dashboard_access(D,C,password_dashboard=G)
		if B[_A]!=1:return{_A:B[_A],_F:B.get(_F,'You do not have access to this dashboard')}
		A=B[_E]
	if not C.is_anonymous:
		I=DashboardShared.objects.filter(is_owner=_C,dashboard=A,user=C)
		if I.count()>0:J=datetime.now().astimezone(UTC);A.last_date_used=J;A.save()
	H=dict()
	if A.plot_db_programmatic_attributes is not _B:H=json.loads(A.plot_db_programmatic_attributes)
	return{_A:1,_J:{'basic':{_H:A.dashboard_id,'name':A.name,'slug':A.slug,_M:A.description,_N:A.is_expose_dashboard,_P:A.is_public_dashboard,_O:A.has_password,'dashboard_venv':A.dashboard_venv,'project_path':A.project_path},'lumino':{'main_ipynb_filename':os.path.basename(A.main_ipynb_fullpath),_R:A.main_ipynb_fullpath,'lumino_layout':A.lumino_layout,'notebook_cells':qube_f2c5d89efa.sparta_6860f183c1(A.main_ipynb_fullpath)},'grid_config':json.loads(A.grid_config),'plot_db_programmatic_attributes':H}}
def sparta_b0a3ffafad(json_data,user_obj):
	J=user_obj;A=json_data;R=A['isNewDashboard']
	if not R:return sparta_b57ea39759(A,J)
	C=datetime.now().astimezone(UTC);K=str(uuid.uuid4());H=A[_K];E=_B
	if H:E=A[_S];E=qube_a2a748f1f2.sparta_50840022e6(E)
	S=A[_L];L=A[_T];T=A[_I];U=A[_U];D=A['projectPath'];D=sparta_cfece85c36(D);V=A[_V];W=A[_W];H=A[_K];X=A.get('dashboardVenv',_B);B=A[_X]
	if len(B)==0:B=A[_I]
	M=slugify(B);B=M;N=1
	while Dashboard.objects.filter(slug=B).exists():B=f"{M}-{N}";N+=1
	O=A[_Y];F=[]
	for(g,Y)in O.items():
		for P in Y:
			if P[_Z]==1:F.append(P[_a])
	F=list(set(F));Z=A[_b];I=_B;G=A.get(_c,_B)
	if G is not _B:
		try:
			G=G.split(',')[1];a=base64.b64decode(G);b=os.path.dirname(__file__);D=os.path.dirname(os.path.dirname(os.path.dirname(b)));Q=os.path.join(D,_d,_e,_J);os.makedirs(Q,exist_ok=_C);I=str(uuid.uuid4());c=os.path.join(Q,f"{I}.png")
			with open(c,'wb')as d:d.write(a)
		except:pass
	logger.debug('SAVE DASHBOARD dashboard_notebook');logger.debug(_R);logger.debug(L);e=Dashboard.objects.create(dashboard_id=K,name=T,slug=B,description=U,is_expose_dashboard=V,is_public_dashboard=W,has_password=H,password_e=E,lumino_layout=S,project_path=D,dashboard_venv=X,main_ipynb_fullpath=L,grid_config=json.dumps(O),plot_db_programmatic_attributes=json.dumps(Z),plot_db_dependencies=json.dumps(F),thumbnail_path=I,date_created=C,last_update=C,last_date_used=C,spartaqube_version=sparta_00b65c604c());f=ShareRights.objects.create(is_admin=_C,has_write_rights=_C,has_reshare_rights=_C,last_update=C);DashboardShared.objects.create(dashboard=e,user=J,share_rights=f,is_owner=_C,date_created=C);return{_A:1,_H:K}
def sparta_8e69596250(lumino_dict,entrypoint_full_path):
	B=entrypoint_full_path;A=lumino_dict;C=A['type']
	if C=='split-area':
		D=A['children']
		for E in D:return sparta_8e69596250(E,B)
	else:
		F=A['widgets']
		for G in F:
			if sparta_cfece85c36(G[_f])==B:return _C
	return _D
def sparta_b57ea39759(json_data,user_obj):
	H=user_obj;B=json_data;M=datetime.now().astimezone(UTC);I=B[_G];J=Dashboard.objects.filter(dashboard_id__startswith=I,is_delete=_D).all()
	if J.count()==1:
		A=J[J.count()-1];I=A.dashboard_id;N=sparta_366b4f8cf1(H)
		if len(N)>0:K=DashboardShared.objects.filter(Q(is_delete=0,user_group__in=N,dashboard__is_delete=0,dashboard=A)|Q(is_delete=0,user=H,dashboard__is_delete=0,dashboard=A))
		else:K=DashboardShared.objects.filter(is_delete=0,user=H,dashboard__is_delete=0,dashboard=A)
		O=_D
		if K.count()>0:
			W=K[0];P=W.share_rights
			if P.is_admin or P.has_write_rights:O=_C
		if O:
			L=B[_L];i=B[_T];X=B[_I];Y=B[_U];Z=B[_V];a=B[_W];b=B[_K];C=B[_X]
			if A.slug!=C:
				if len(C)==0:C=B[_I]
				R=slugify(C);C=R;S=1
				while Dashboard.objects.filter(slug=C).exists():C=f"{R}-{S}";S+=1
			T=B[_Y];D=[]
			for(j,c)in T.items():
				for U in c:
					if U[_Z]==1:D.append(U[_a])
			D=list(set(D));E=_B;F=B.get(_c,_B)
			if F is not _B:
				F=F.split(',')[1];d=base64.b64decode(F)
				try:
					e=os.path.dirname(__file__);f=os.path.dirname(os.path.dirname(os.path.dirname(e)));V=os.path.join(f,_d,_e,_J);os.makedirs(V,exist_ok=_C)
					if A.thumbnail_path is _B:E=str(uuid.uuid4())
					else:E=A.thumbnail_path
					g=os.path.join(V,f"{E}.png")
					with open(g,'wb')as h:h.write(d)
				except:pass
			logger.debug('lumino_layout_dump');logger.debug(L);logger.debug(type(L));A.name=X;A.description=Y;A.slug=C;A.is_expose_dashboard=Z;A.is_public_dashboard=a;A.thumbnail_path=E;A.lumino_layout=L;A.grid_config=json.dumps(T);A.plot_db_programmatic_attributes=json.dumps(B[_b]);A.plot_db_dependencies=json.dumps(D);A.last_update=M;A.last_date_used=M
			if b:
				G=B[_S]
				if len(G)>0:G=qube_a2a748f1f2.sparta_50840022e6(G);A.password_e=G;A.has_password=_C
			else:A.has_password=_D
			A.save()
	return{_A:1,_H:I}
def sparta_b77cea4b8e(json_data,user_obj):
	E=json_data;B=user_obj;F=E[_G];C=Dashboard.objects.filter(dashboard_id__startswith=F,is_delete=_D).all()
	if C.count()==1:
		A=C[C.count()-1];F=A.dashboard_id;G=sparta_366b4f8cf1(B)
		if len(G)>0:D=DashboardShared.objects.filter(Q(is_delete=0,user_group__in=G,dashboard__is_delete=0,dashboard=A)|Q(is_delete=0,user=B,dashboard__is_delete=0,dashboard=A))
		else:D=DashboardShared.objects.filter(is_delete=0,user=B,dashboard__is_delete=0,dashboard=A)
		H=_D
		if D.count()>0:
			J=D[0];I=J.share_rights
			if I.is_admin or I.has_write_rights:H=_C
		if H:K=E[_L];A.lumino_layout=K;A.save()
	return{_A:1}
def sparta_70add62f0b(json_data,user_obj):
	C=user_obj;B=json_data;logger.debug(_Q);logger.debug(B);F=B[_G];D=Dashboard.objects.filter(dashboard_id__startswith=F,is_delete=_D).all()
	if D.count()==1:
		A=D[D.count()-1];F=A.dashboard_id;G=sparta_366b4f8cf1(C)
		if len(G)>0:E=DashboardShared.objects.filter(Q(is_delete=0,user_group__in=G,dashboard__is_delete=0,dashboard=A)|Q(is_delete=0,user=C,dashboard__is_delete=0,dashboard=A))
		else:E=DashboardShared.objects.filter(is_delete=0,user=C,dashboard__is_delete=0,dashboard=A)
		H=_D
		if E.count()>0:
			J=E[0];I=J.share_rights
			if I.is_admin or I.has_write_rights:H=_C
		if H:K=sparta_cfece85c36(B[_f]);A.main_ipynb_fullpath=K;A.save()
	return{_A:1}
def sparta_2ceb46c972(json_data,user_obj):
	A=user_obj;G=json_data[_G];B=Dashboard.objects.filter(dashboard_id=G,is_delete=_D).all()
	if B.count()>0:
		C=B[B.count()-1];E=sparta_366b4f8cf1(A)
		if len(E)>0:D=DashboardShared.objects.filter(Q(is_delete=0,user_group__in=E,dashboard__is_delete=0,dashboard=C)|Q(is_delete=0,user=A,dashboard__is_delete=0,dashboard=C))
		else:D=DashboardShared.objects.filter(is_delete=0,user=A,dashboard__is_delete=0,dashboard=C)
		if D.count()>0:F=D[0];F.is_delete=_C;F.save()
	return{_A:1}
def has_dashboard_access(dashboard_id,user_obj,password_dashboard=_B):
	I='Invalid password';G=password_dashboard;F=dashboard_id;B=user_obj;logger.debug('dashboard_id > '+str(F));logger.debug('password_dashboard > '+str(G));C=Dashboard.objects.filter(dashboard_id__startswith=F,is_delete=_D).all();H=_D
	if C.count()==1:H=_C
	else:
		J=F;C=Dashboard.objects.filter(slug__startswith=J,is_delete=_D).all()
		if C.count()==1:H=_C
	if H:
		A=C[C.count()-1]
		if not B.is_anonymous:
			D=sparta_366b4f8cf1(B)
			if len(D)>0:E=DashboardShared.objects.filter(Q(is_delete=0,user_group__in=D,dashboard__is_delete=0,dashboard=A)|Q(is_delete=0,user=B,dashboard__is_delete=0,dashboard=A))
			else:E=DashboardShared.objects.filter(is_delete=0,user=B,dashboard__is_delete=0,dashboard=A)
			if E.count()>0:return{_A:1,_E:A}
		K=A.has_password
		if A.is_expose_dashboard:
			if A.is_public_dashboard:
				if not K:return{_A:1,_E:A}
				elif G is _B:return{_A:2,_F:'Require password',_E:A}
				else:
					try:
						if qube_a2a748f1f2.sparta_bb4d8efa9a(A.password_e)==G:return{_A:1,_E:A}
						else:return{_A:3,_F:I,_E:A}
					except Exception as L:return{_A:3,_F:I,_E:A}
			elif B.is_authenticated:
				D=sparta_366b4f8cf1(B)
				if len(D)>0:E=DashboardShared.objects.filter(Q(is_delete=0,user_group__in=D,dashboard__is_delete=0,dashboard=A)|Q(is_delete=0,user=B,dashboard__is_delete=0,dashboard=A))
				else:E=DashboardShared.objects.filter(is_delete=0,user=B,dashboard__is_delete=0,dashboard=A)
				if E.count()>0:return{_A:1,_E:A}
			else:return{_A:-1}
	return{_A:-1}
def sparta_a9c1c1cd2d(json_data,user_obj):A=sparta_984e2efb4d(json_data,user_obj);return A
def has_plot_db_access(dashboard_id,plot_db_id,user_obj,dashboard_password):
	A=plot_db_id;B=has_dashboard_access(dashboard_id,user_obj,password_dashboard=dashboard_password)
	if B[_A]==1:
		F=B[_E];G=json.loads(F.plot_db_dependencies)
		if A in G:
			C=PlotDBChart.objects.filter(plot_chart_id__startswith=A,is_delete=_D).all()
			if C.count()>0:D=C[0];E=str(uuid.uuid4());H=datetime.now().astimezone(UTC);PlotDBPermission.objects.create(plot_db_chart=D,token=E,date_created=H);return{_A:1,'plot_db_chart_obj':D,'token_permission':E}
	return{_A:-1}