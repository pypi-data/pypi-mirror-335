_AZ='yAxisDataArr'
_AY='xAxisDataArr'
_AX='widget_id'
_AW='code_editor_notebook_cells'
_AV='chart_config'
_AU='chart_params'
_AT='plot_library'
_AS='has_write_rights'
_AR='chartConfigDict'
_AQ='chartParams'
_AP='dataSourceArr'
_AO='typeChart'
_AN='thumbnail'
_AM='previewImage'
_AL='json_data'
_AK='is_create_connector'
_AJ='Name desc'
_AI='Date desc'
_AH='shadedBackgroundArr'
_AG='radiusBubbleArr'
_AF='labelsArr'
_AE='labels'
_AD='column'
_AC='datasets'
_AB='Invalid password'
_AA='data_source_list'
_A9='date_created'
_A8='last_update'
_A7='is_static_data'
_A6='is_expose_widget'
_A5='bExposeAsWidget'
_A4='plotDes'
_A3='bStaticDataPlot'
_A2='codeEditorNotebookCells'
_A1='split'
_A0='query_filter'
_z='error'
_y='success'
_x='is_owner'
_w='is_public_widget'
_v='has_widget_password'
_u='bPublicWidget'
_t='plotName'
_s='widgetPassword'
_r='columns'
_q='input'
_p='bApplyFilter'
_o='trusted_connection'
_n='lib_dir'
_m='organization'
_l='token'
_k='password'
_j='Recently used'
_i='has_access'
_h='type_chart'
_g='You do not have the rights to access this connector'
_f='py_code_processing'
_e='redis_db'
_d='socket_url'
_c='json_url'
_b='read_only'
_a='csv_delimiter'
_Z='csv_path'
_Y='database_path'
_X='library_arctic'
_W='keyspace'
_V='oracle_service_name'
_U='driver'
_T='database'
_S='user'
_R='port'
_Q='host'
_P='%Y-%m-%d'
_O='table_name'
_N='db_engine'
_M='bWidgetPassword'
_L='description'
_K='plot_db_chart_obj'
_J='name'
_I='dynamic_inputs'
_H='connector_id'
_G='plot_chart_id'
_F='data'
_E='errorMsg'
_D=False
_C=True
_B=None
_A='res'
import re,os,json,io,sys,base64,asyncio,subprocess,traceback,tinykernel,cloudpickle,uuid,pandas as pd
from subprocess import PIPE
from django.db.models import Q
from django.utils.text import slugify
from datetime import datetime,timedelta
from pathlib import Path
import pytz
UTC=pytz.utc
from spartaqube_app.path_mapper_obf import sparta_ab2d4b6ec5
from project.models_spartaqube import DBConnector,DBConnectorUserShared,PlotDBChart,PlotDBChartShared,PlotDBPermission,CodeEditorNotebook,NewPlotApiVariables
from project.models import ShareRights
from project.sparta_3bc15131c6.sparta_6156be0aab import qube_c9db55e3c2 as qube_c9db55e3c2
from project.sparta_3bc15131c6.sparta_21301ca379 import qube_85e301a8bd
from project.sparta_3bc15131c6.sparta_1ec16518f2 import qube_e3b4c78a63 as qube_e3b4c78a63
from project.sparta_3bc15131c6.sparta_21301ca379.qube_a2478f1fd1 import Connector as Connector
from project.sparta_3bc15131c6.sparta_0d2990c769.qube_48c282f85d import convert_to_dataframe,convert_dataframe_to_json,sparta_b0cac1454c
from project.sparta_3bc15131c6.sparta_0577602ad9.qube_47927cfb13 import sparta_c4aba70c92
from project.logger_config import logger
INPUTS_KEYS=['xAxisArr','yAxisArr',_AF,_AG,'rangesAxisArr','measuresAxisArr','markersAxisArr','ohlcvArr',_AH]
def sparta_2aa24d038e(user_obj):from project.sparta_3bc15131c6.sparta_ef73db400d.qube_a300615bb6 import sparta_00fc6ac630 as A;return A(user_obj)
def sparta_7d8d6d46a2(user_obj):
	A=qube_c9db55e3c2.sparta_e2c6ddbe2b(user_obj)
	if len(A)>0:B=[A.user_group for A in A]
	else:B=[]
	return B
def sparta_bd7cdb3cef(json_data,user_obj):
	D=user_obj;E=sparta_7d8d6d46a2(D)
	if len(E)>0:B=DBConnectorUserShared.objects.filter(Q(is_delete=0,user_group__in=E,db_connector__is_delete=0)|Q(is_delete=0,user=D,db_connector__is_delete=0))
	else:B=DBConnectorUserShared.objects.filter(is_delete=0,user=D,db_connector__is_delete=0)
	F=[]
	if B.count()>0:
		C=json_data.get('orderBy',_j)
		if C==_j:B=B.order_by('-db_connector__last_date_used')
		elif C==_AI:B=B.order_by('-db_connector__last_update')
		elif C=='Date asc':B=B.order_by('db_connector__last_update')
		elif C==_AJ:B=B.order_by('-db_connector__name')
		elif C=='Name asc':B=B.order_by('db_connector__name')
		elif C=='Type':B=B.order_by('db_connector__db_engine')
		for G in B:
			A=G.db_connector;H=[]
			try:H=json.loads(A.dynamic_inputs)
			except:pass
			F.append({_H:A.connector_id,_Q:A.host,_R:A.port,_S:A.user,_T:A.database,_U:A.driver,_V:A.oracle_service_name,_W:A.keyspace,_X:A.library_arctic,_Y:A.database_path,_Z:A.csv_path,_a:A.csv_delimiter,_b:A.read_only,_c:A.json_url,_d:A.socket_url,_e:A.redis_db,_I:H,_f:A.py_code_processing,_N:A.db_engine,_J:A.name,_L:A.description,_x:G.is_owner})
	return{_A:1,'db_connectors':F}
def sparta_a199e22d72():return{_A:1,'available_engines':qube_85e301a8bd.sparta_a199e22d72()}
def sparta_08f875670d(json_data,user_obj):
	C=json_data[_H];A=DBConnector.objects.filter(connector_id=C,is_delete=_D).all()
	if A.count()>0:B=A[A.count()-1];D=datetime.now().astimezone(UTC);B.last_date_used=D;B.save()
	return{_A:1}
def sparta_56cf9d7ae3(json_data):
	A=json_data;C='';B=Connector(db_engine=A[_N]);B.init_with_params(host=A[_Q],port=A[_R],user=A[_S],password=A[_k],database=A[_T],oracle_service_name=A[_V],csv_path=A[_Z],csv_delimiter=A[_a],keyspace=A[_W],library_arctic=A[_X],database_path=A[_Y],read_only=A[_b],json_url=A[_c],socket_url=A[_d],redis_db=A.get(_e,_B),token=A.get(_l,_B),organization=A.get(_m,_B),lib_dir=A.get(_n,_B),driver=A.get(_U,_B),trusted_connection=A.get(_o,_B),dynamic_inputs=A[_I],py_code_processing=A[_f]);D=B.test_connection()
	if not D:C=B.get_error_msg_test_connection()
	return{_A:1,'is_connector_working':D,_E:C}
def sparta_35b003b8a6(json_data):
	A=json_data;B=1;C='';D='';E=_B
	try:F=Connector(db_engine=A[_N]);F.init_with_params(host=A[_Q],port=A[_R],user=A[_S],password=A[_k],database=A[_T],oracle_service_name=A[_V],csv_path=A[_Z],csv_delimiter=A[_a],keyspace=A[_W],library_arctic=A[_X],database_path=A[_Y],read_only=A[_b],json_url=A[_c],socket_url=A[_d],redis_db=A[_e],token=A.get(_l,''),organization=A.get(_m,''),lib_dir=A.get(_n,''),driver=A.get(_U,''),trusted_connection=A.get(_o,_C),dynamic_inputs=A[_I],py_code_processing=A[_f]);H,D=F.preview_output_connector_bowler();G=io.StringIO();sys.stdout=G;print(H);E=G.getvalue();sys.stdout=sys.__stdout__
	except Exception as I:C=str(I);B=-1
	return{_A:B,'preview_json':E,'print_buffer_content':D,_E:C}
def sparta_ba8bf8bec8(json_data,user_obj):A=json_data;B=datetime.now().astimezone(UTC);C=str(uuid.uuid4());D=DBConnector.objects.create(connector_id=C,host=A[_Q],port=A[_R],user=A[_S],password_e=qube_85e301a8bd.sparta_0db65b9c7e(A[_k]),database=A[_T],oracle_service_name=A[_V],keyspace=A[_W],library_arctic=A[_X],database_path=A[_Y],csv_path=A[_Z],csv_delimiter=A[_a],read_only=A[_b],json_url=A[_c],socket_url=A[_d],redis_db=A[_e],token=A[_l],organization=A[_m],lib_dir=A[_n],driver=A[_U],trusted_connection=A[_o],dynamic_inputs=json.dumps(A[_I]),py_code_processing=A[_f],db_engine=A[_N],name=A[_J],description=A[_L],date_created=B,last_update=B,last_date_used=B);E=ShareRights.objects.create(is_admin=_C,has_write_rights=_C,has_reshare_rights=_C,last_update=B);DBConnectorUserShared.objects.create(db_connector=D,user=user_obj,date_created=B,share_rights=E,is_owner=_C);return{_A:1}
def sparta_e0854ae644(json_data,user_obj):
	C=user_obj;B=json_data;logger.debug('update connector');logger.debug(B);I=B[_H];D=DBConnector.objects.filter(connector_id=I,is_delete=_D).all()
	if D.count()>0:
		A=D[D.count()-1];F=sparta_7d8d6d46a2(C)
		if len(F)>0:E=DBConnectorUserShared.objects.filter(Q(is_delete=0,user_group__in=F,db_connector__is_delete=0,db_connector=A)|Q(is_delete=0,user=C,db_connector__is_delete=0,db_connector=A))
		else:E=DBConnectorUserShared.objects.filter(is_delete=0,user=C,db_connector__is_delete=0,db_connector=A)
		if E.count()>0:
			J=E[0];G=J.share_rights
			if G.is_admin or G.has_write_rights:H=datetime.now().astimezone(UTC);A.host=B[_Q];A.port=B[_R];A.user=B[_S];A.password_e=qube_85e301a8bd.sparta_0db65b9c7e(B[_k]);A.database=B[_T];A.oracle_service_name=B[_V];A.keyspace=B[_W];A.library_arctic=B[_X];A.database_path=B[_Y];A.csv_path=B[_Z];A.csv_delimiter=B[_a];A.read_only=B[_b];A.json_url=B[_c];A.socket_url=B[_d];A.redis_db=B[_e];A.token=B.get(_l,'');A.organization=B.get(_m,'');A.lib_dir=B.get(_n,'');A.driver=B.get(_U,'');A.trusted_connection=B.get(_o,_C);A.dynamic_inputs=json.dumps(B[_I]);A.py_code_processing=B[_f];A.db_engine=B[_N];A.name=B[_J];A.description=B[_L];A.last_update=H;A.last_date_used=H;A.save()
	return{_A:1}
def sparta_bc3414a13b(json_data,user_obj):
	B=user_obj;F=json_data[_H];C=DBConnector.objects.filter(connector_id=F,is_delete=_D).all()
	if C.count()>0:
		A=C[C.count()-1];E=sparta_7d8d6d46a2(B)
		if len(E)>0:D=DBConnectorUserShared.objects.filter(Q(is_delete=0,user_group__in=E,db_connector__is_delete=0,db_connector=A)|Q(is_delete=0,user=B,db_connector__is_delete=0,db_connector=A))
		else:D=DBConnectorUserShared.objects.filter(is_delete=0,user=B,db_connector__is_delete=0,db_connector=A)
		if D.count()>0:
			G=D[0];H=G.share_rights
			if H.is_admin:A.is_delete=_C;A.save()
	return{_A:1}
def sparta_bad15a7062(package_name):
	A=subprocess.Popen([sys.executable,'-m','pip','install',package_name],stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=_C);B,C=A.communicate()
	if A.returncode==0:return{_y:_C,'output':B}
	else:return{_y:_D,_z:C}
def sparta_0958c68d65(json_data,user_obj):
	B=_D;C=[];D=json_data['pip_cmds']
	for E in D:
		A=sparta_bad15a7062(E)
		if A[_y]:logger.debug('Installation succeeded:',A['output'])
		else:logger.debug('Installation failed:',A[_z]);B=_C;C.append(A[_z])
	return{_A:1,'has_error':B,'errors':C}
def sparta_e241d10f47(connector_id,user_obj):
	B=user_obj;C=DBConnector.objects.filter(connector_id__startswith=connector_id,is_delete=_D).all()
	if C.count()==1:
		A=C[0];D=sparta_7d8d6d46a2(B)
		if len(D)>0:E=DBConnectorUserShared.objects.filter(Q(is_delete=0,user_group__in=D,db_connector__is_delete=0,db_connector=A)|Q(is_delete=0,user=B,db_connector__is_delete=0,db_connector=A))
		else:E=DBConnectorUserShared.objects.filter(is_delete=0,user=B,db_connector__is_delete=0,db_connector=A)
		if E.count()>0:return A
class DotDict(dict):
	def __getattr__(A,name):return A.get(name,_B)
	def __setattr__(A,name,value):A[name]=value
	def __delattr__(A,name):del A[name]
def sparta_77fb8813d6(obj):
	A=obj
	if isinstance(A,dict):
		B=DotDict()
		for(C,D)in A.items():B[C]=sparta_77fb8813d6(D)
		return B
	elif isinstance(A,list):return[sparta_77fb8813d6(A)for A in A]
	else:return A
def sparta_14229cf97f(json_data,user_obj):
	B=json_data;D=B.get(_AK,_D)
	if D:A=sparta_77fb8813d6(B)
	else:
		E=B[_H];A=sparta_e241d10f47(E,user_obj)
		if A is _B:return{_A:-1,_E:_g}
	C=Connector(db_engine=A.db_engine);C.init_with_model(A);F=C.get_available_tables();G=C.get_available_views();return{_A:1,'tables_explorer':F,'views_explorer':G}
def sparta_3fd59cb075(json_data,user_obj):
	A=json_data;G=A[_H];E=A[_O];H=int(A.get(_p,'0'))==1;B=[];C=sparta_e241d10f47(G,user_obj)
	if C is _B:return{_A:-1,_E:_g}
	D=Connector(db_engine=C.db_engine);D.init_with_model(C)
	if H:
		I=A[_A0]
		try:F=D.get_data_table_query(I,E)
		except Exception as J:logger.debug(traceback.format_exc());return{_A:-1,_E:str(J)}
		K=list(K.columns)
		for(L,M)in zip(F.columns,F.dtypes):N={_J:L,'type':str(M)};B.append(N)
	else:B=D.get_table_columns(E)
	return{_A:1,'table_columns':B}
def sparta_6f45fcde4d(json_data,db_connector_obj):
	B=db_connector_obj
	if B.db_engine is not _B:
		if B.db_engine in['json_api','python','wss_api']:
			A=B.dynamic_inputs
			if A is not _B:
				try:A=json.loads(A)
				except:A=[]
			C=json_data.get(_I,[]);E=[A[_q]for A in A]
			for D in A:
				if D[_q]not in E:C.append(D)
			B.dynamic_inputs=json.dumps(C)
def sparta_402787c56f(json_data,user_obj):
	A=json_data;print(_AL);print(A);H=A.get(_AK,_D);I=A[_H];C=A.get(_O,_B);F=int(A.get(_p,'0'))==1;G=int(A.get('previewTopMod','0'))==0
	if H:D=sparta_77fb8813d6(A)
	else:
		D=sparta_e241d10f47(I,user_obj)
		if D is _B:return{_A:-1,_E:_g}
	sparta_6f45fcde4d(A,D);B=Connector(db_engine=D.db_engine);B.init_with_model(D)
	if F is not _B:
		if F:
			J=A[_A0]
			try:E=B.get_data_table_query(J,C)
			except Exception as K:logger.debug(traceback.format_exc());return{_A:-1,_E:str(K)}
		elif G:E=B.get_data_table_top(C)
		else:E=B.get_data_table(C)
	elif G:E=B.get_data_table_top(C)
	else:E=B.get_data_table(C)
	return{_A:1,_F:convert_dataframe_to_json(E)}
def sparta_e99966351e(json_data,user_obj):
	A=json_data;F=A[_H];D=A.get(_O,'');G=int(A.get(_p,'0'))==1;K=A.get(_N,_B);B=sparta_e241d10f47(F,user_obj)
	if B is _B:return{_A:-1,_E:_g}
	sparta_6f45fcde4d(A,B);C=Connector(db_engine=B.db_engine);C.init_with_model(B)
	if G:
		H=A[_A0]
		try:E=C.get_data_table_query(H,D)
		except Exception as I:logger.debug(traceback.format_exc());return{_A:-1,_E:str(I)}
	else:E=C.get_data_table(D)
	J=E.describe();return{_A:1,_F:J.to_json(orient=_A1)}
def sparta_28fc3573c9(json_data,user_obj):
	C=json_data
	def E(df):A=df;return pd.DataFrame({_J:A.columns,'non-nulls':len(A)-A.isnull().sum().values,'nulls':A.isnull().sum().values,'type':A.dtypes.values})
	A=json.loads(C[_F]);F=int(C['mode']);D=pd.DataFrame(data=A[_F],columns=A[_r],index=A['index']);B=''
	if F==1:G=E(D);B=G.to_html()
	else:H=D.describe();B=H.to_html()
	return{_A:1,'table':B}
def sparta_3cd40661ad(json_data,user_obj):
	A=json_data;D=A[_H];F=A.get(_O,_B);G=int(A.get(_p,'0'))==1;B=sparta_e241d10f47(D,user_obj)
	if B is _B:return{_A:-1,_E:_g}
	sparta_6f45fcde4d(A,B);C=Connector(db_engine=B.db_engine);C.init_with_model(B);E=C.get_db_connector().get_wss_structure();return{_A:1,_F:convert_dataframe_to_json(E)}
def sparta_55ac4e778e(json_data,user_obj):
	A=json_data;M=A[_M];D=_B
	if M:D=A[_s];D=qube_e3b4c78a63.sparta_5ff3a13eb1(D)
	N=A[_A2];O=str(uuid.uuid4());B=datetime.now().astimezone(UTC);P=CodeEditorNotebook.objects.create(notebook_id=O,cells=N,date_created=B,last_update=B);G=str(uuid.uuid4());H=A[_A3];I=A['is_gui_plot']
	if I:H=_C
	C=A['plotSlug']
	if len(C)==0:C=A[_t]
	J=slugify(C);C=J;K=1
	while PlotDBChart.objects.filter(slug=C).exists():C=f"{J}-{K}";K+=1
	F=_B;E=A.get(_AM,_B)
	if E is not _B:
		try:
			E=E.split(',')[1];Q=base64.b64decode(E);R=os.path.dirname(__file__);S=os.path.dirname(os.path.dirname(os.path.dirname(R)));L=os.path.join(S,'static',_AN,'widget');os.makedirs(L,exist_ok=_C);F=str(uuid.uuid4());T=os.path.join(L,f"{F}.png")
			with open(T,'wb')as U:U.write(Q)
		except:pass
	V=PlotDBChart.objects.create(plot_chart_id=G,type_chart=A[_AO],name=A[_t],slug=C,description=A[_A4],is_expose_widget=A[_A5],is_public_widget=A[_u],is_static_data=H,has_widget_password=A[_M],widget_password_e=D,data_source_list=A[_AP],chart_params=A[_AQ],chart_config=A[_AR],code_editor_notebook=P,is_created_from_api=I,thumbnail_path=F,date_created=B,last_update=B,last_date_used=B,spartaqube_version=sparta_c4aba70c92());W=ShareRights.objects.create(is_admin=_C,has_write_rights=_C,has_reshare_rights=_C,last_update=B);PlotDBChartShared.objects.create(plot_db_chart=V,user=user_obj,share_rights=W,is_owner=_C,date_created=B);return{_A:1,_G:G}
def sparta_32a3160898(json_data,user_obj):
	G=user_obj;B=json_data;N=B[_G];H=PlotDBChart.objects.filter(plot_chart_id=N,is_delete=_D).all()
	if H.count()>0:
		A=H[H.count()-1];K=sparta_7d8d6d46a2(G)
		if len(K)>0:I=PlotDBChartShared.objects.filter(Q(is_delete=0,user_group__in=K,plot_db_chart__is_delete=0,plot_db_chart=A)|Q(is_delete=0,user=G,plot_db_chart__is_delete=0,plot_db_chart=A))
		else:I=PlotDBChartShared.objects.filter(is_delete=0,user=G,plot_db_chart__is_delete=0,plot_db_chart=A)
		if I.count()>0:
			O=I[0];L=O.share_rights
			if L.is_admin or L.has_write_rights:
				P=B[_M];C=_B
				if P:C=B[_s];C=qube_e3b4c78a63.sparta_5ff3a13eb1(C)
				D=_B;E=B.get(_AM,_B)
				if E is not _B:
					E=E.split(',')[1];R=base64.b64decode(E)
					try:
						S=os.path.dirname(__file__);T=os.path.dirname(os.path.dirname(os.path.dirname(S)));M=os.path.join(T,'static',_AN,'widget');os.makedirs(M,exist_ok=_C)
						if A.thumbnail_path is _B:D=str(uuid.uuid4())
						else:D=A.thumbnail_path
						U=os.path.join(M,f"{D}.png")
						with open(U,'wb')as V:V.write(R)
					except:pass
				J=datetime.now().astimezone(UTC);A.type_chart=B[_AO];A.name=B[_t];A.description=B[_A4];A.is_expose_widget=B[_A5];A.is_static_data=B[_A3];A.has_widget_password=B[_M];A.is_public_widget=B[_u];A.widget_password_e=C;A.data_source_list=B[_AP];A.chart_params=B[_AQ];A.chart_config=B[_AR];A.thumbnail_path=D;A.last_update=J;A.last_date_used=J;A.save();F=A.code_editor_notebook
				if F is not _B:F.cells=B[_A2];F.last_update=J;F.save()
	return{_A:1}
def sparta_2cd835a7b8(json_data,user_obj):0
def sparta_a24f347725(json_data,user_obj):
	D=user_obj;F=sparta_7d8d6d46a2(D)
	if len(F)>0:A=PlotDBChartShared.objects.filter(Q(is_delete=0,user_group__in=F,plot_db_chart__is_delete=0)|Q(is_delete=0,user=D,plot_db_chart__is_delete=0))
	else:A=PlotDBChartShared.objects.filter(is_delete=0,user=D,plot_db_chart__is_delete=0)
	if A.count()>0:
		C=json_data.get('orderBy',_j)
		if C==_j:A=A.order_by('-plot_db_chart__last_date_used')
		elif C==_AI:A=A.order_by('-plot_db_chart__last_update')
		elif C=='Date asc':A=A.order_by('plot_db_chart__last_update')
		elif C==_AJ:A=A.order_by('-plot_db_chart__name')
		elif C=='Name asc':A=A.order_by('plot_db_chart__name')
		elif C=='Type':A=A.order_by('plot_db_chart__type_chart')
	G=[]
	for E in A:
		B=E.plot_db_chart;J=E.share_rights;H=_B
		try:H=str(B.last_update.strftime(_P))
		except:pass
		I=_B
		try:I=str(B.date_created.strftime(_P))
		except Exception as K:logger.debug(K)
		G.append({_G:B.plot_chart_id,_h:B.type_chart,_J:B.name,'slug':B.slug,_L:B.description,_A6:B.is_expose_widget,_A7:B.is_static_data,_v:B.has_widget_password,_w:B.is_public_widget,_x:E.is_owner,_AS:J.has_write_rights,'thumbnail_path':B.thumbnail_path,_A8:H,_A9:I})
	return{_A:1,_AT:G}
def exec_notebook_and_get_workspace_variables(full_code,data_source_variables,workspace_variables,api_key):
	B=full_code;F=sparta_ab2d4b6ec5()['project'];G=sparta_ab2d4b6ec5()['project/core/api'];A='import sys, os\n';A+=f'sys.path.insert(0, r"{str(F)}")\n';A+=f'sys.path.insert(0, r"{str(G)}")\n';A+=f'os.environ["api_key"] = "{api_key}"\n';B=A+'\n'+B;D=dict();C=tinykernel.TinyKernel()
	for(H,I)in data_source_variables.items():C.glb[H]=I
	C(B)
	for E in workspace_variables:D[E]=C(E)
	return D
def sparta_ae685aa3e9(json_data,user_obj):
	b='kernelVariableName';a='isNotebook';Z='password_widget';C=json_data;D=C.get('token_permission','')
	if len(D)==0:D=_B
	H=C[_G];P=_B
	if Z in C:P=C[Z]
	c=C.get('dataSourceListOverride',[]);I=PlotDBChart.objects.filter(plot_chart_id__startswith=H,is_delete=_D).all()
	if I.count()==1:
		A=I[I.count()-1];H=A.plot_chart_id;E=_D
		if D is not _B:
			d=sparta_15bd86cc07(D)
			if d[_A]==1:E=_C
		if not E:
			if has_permission_widget_or_shared_rights(A,user_obj,password_widget=P):E=_C
		if E:
			Q=PlotDBChartShared.objects.filter(is_delete=0,plot_db_chart__is_delete=0,plot_db_chart=A)
			if Q.count()>0:
				J=Q[0];e=J.user;f=sparta_2aa24d038e(e);R=J.user;K=[];A=J.plot_db_chart;g=A.is_static_data
				if g:0
				else:
					for B in A.data_source_list:
						L=B[a]
						if L:K.append(B[b])
						else:
							if _I in B:
								h=B[_H];S=sparta_e241d10f47(h,R);T=[]
								if S.dynamic_inputs is not _B:
									try:T=json.loads(S.dynamic_inputs)
									except:pass
								M=B[_I];i=[A[_q]for A in M]
								for U in T:
									j=U[_q]
									if j not in i:M.append(U)
								B[_I]=M
								for F in c:
									if _H in F:
										if F[_H]==B[_H]:
											if F[_O]==B[_O]:B[_I]=F[_I]
							V=sparta_402787c56f(B,R)
							if V[_A]==1:k=V[_F];B[_F]=k
				W=A.code_editor_notebook
				if W is not _B:G=W.cells
				else:G=_B
				if len(K)>0:
					if G is not _B:
						l='\n'.join([A['code']for A in json.loads(G)]);X=dict()
						for N in A.data_source_list:
							if N['isDataSource']:O=json.loads(N[_F]);X[N['table_name_workspace']]=pd.DataFrame(O[_F],index=O['index'],columns=O[_r])
						m=exec_notebook_and_get_workspace_variables(l,X,K,f)
						for B in A.data_source_list:
							L=B[a]
							if L:Y=B[b];n=m[Y];B[_F]=convert_dataframe_to_json(convert_to_dataframe(n,variable_name=Y))
				def o(s):s=s.lower();A='-_.() %s%s'%(re.escape('/'),re.escape('\\'));B=re.sub('[^A-Za-z0-9%s]'%A,'_',s);return B
				return{_A:1,_G:H,_h:A.type_chart,_J:A.name,'slug':A.slug,'name_file':o(A.name),_L:A.description,_A6:A.is_expose_widget,_A7:A.is_static_data,_v:A.has_widget_password,_w:A.is_public_widget,_AA:A.data_source_list,_AU:A.chart_params,_AV:A.chart_config,_AW:G}
		else:return{_A:-1,_E:_AB}
	return{_A:-1,_E:'Unexpected error, please try again'}
def sparta_b8ca3b83a2(json_data,user_obj):
	B=json_data;logger.debug(_AL);logger.debug(B);D=B[_G];A=PlotDBChart.objects.filter(plot_chart_id=D,is_delete=_D).all()
	if A.count()>0:C=A[A.count()-1];E=datetime.now().astimezone(UTC);C.last_date_used=E;C.save()
	return{_A:1}
def sparta_3e7f12b97d(user_obj,widget_id):
	F='options';D=user_obj;C=_D;E=PlotDBChart.objects.filter(plot_chart_id__startswith=widget_id,is_delete=_D).all()
	if E.count()>0:
		A=E[E.count()-1]
		if A.is_expose_widget:
			if A.is_public_widget:C=_C
		if not C:
			G=sparta_7d8d6d46a2(D)
			if len(G)>0:H=PlotDBChartShared.objects.filter(Q(is_delete=0,user_group__in=G,plot_db_chart__is_delete=0,plot_db_chart=A)|Q(is_delete=0,user=D,plot_db_chart__is_delete=0,plot_db_chart=A))
			else:H=PlotDBChartShared.objects.filter(is_delete=0,user=D,plot_db_chart__is_delete=0,plot_db_chart=A)
			if H.count()>0:C=_C
	if C:
		B=A.chart_params
		if F in B:B[F]=json.loads(B[F])
		if _F in B:B[_AC]=json.loads(B[_F])[_AC]
		I=A.type_chart;return{_A:1,'override_options':B,_h:I}
	else:return{_A:-1,_E:'You do not have the rights to access this template'}
def sparta_286ff621f1(json_data,user_obj):
	X='is_index';R=json_data;K=user_obj;J='uuid'
	try:
		S=R[_G];Y=R['session_id'];L=PlotDBChart.objects.filter(plot_chart_id=S,is_delete=_D).all()
		if L.count()>0:
			A=L[L.count()-1];T=sparta_7d8d6d46a2(K)
			if len(T)>0:M=PlotDBChartShared.objects.filter(Q(is_delete=0,user_group__in=T,plot_db_chart__is_delete=0,plot_db_chart=A)|Q(is_delete=0,user=K,plot_db_chart__is_delete=0,plot_db_chart=A))
			else:M=PlotDBChartShared.objects.filter(is_delete=0,user=K,plot_db_chart__is_delete=0,plot_db_chart=A)
			if M.count()>0:
				Z=M[0];A=Z.plot_db_chart;U=NewPlotApiVariables.objects.filter(session_id=Y).all()
				if U.count()>0:
					a=U[0];b=a.pickled_variables;E=cloudpickle.loads(b.encode('latin1'));F=dict()
					for G in A.data_source_list:C=G[J];F[C]=pd.DataFrame()
					H=json.loads(A.chart_config)
					for B in H.keys():
						if B in INPUTS_KEYS:
							if B=='xAxis':
								N=H[B];C=N[J];O=N[X];P=N[_AD];D=F[C]
								if O:D.index=E[B]
								else:D[P]=E[B]
							elif H[B]is not _B:
								c=H[B]
								for(V,I)in enumerate(c):
									if I is not _B:
										C=I[J];O=I[X];P=I[_AD];D=F[C]
										if O:D.index=E[B][V]
										else:D[P]=E[B][V]
					for G in A.data_source_list:C=G[J];G[_F]=F[C].to_json(orient=_A1)
				return{_A:1,_G:S,_h:A.type_chart,_J:A.name,_L:A.description,_A6:A.is_expose_widget,_A7:A.is_static_data,_v:A.has_widget_password,_w:A.is_public_widget,_AA:A.data_source_list,_AU:A.chart_params,_AV:A.chart_config,_AW:_B}
	except Exception as W:logger.debug('Error exception > '+str(W));return{_A:-1,_E:str(W)}
def sparta_f8f8b923ba(json_data,user_obj):
	E=json_data;A=user_obj;print('DELTE PLOT');print(E);H=E[_G];B=PlotDBChart.objects.filter(plot_chart_id=H,is_delete=_D).all()
	if B.count()>0:
		C=B[B.count()-1];F=sparta_7d8d6d46a2(A)
		if len(F)>0:D=PlotDBChartShared.objects.filter(Q(is_delete=0,user_group__in=F,plot_db_chart__is_delete=0,plot_db_chart=C)|Q(is_delete=0,user=A,plot_db_chart__is_delete=0,plot_db_chart=C))
		else:D=PlotDBChartShared.objects.filter(is_delete=0,user=A,plot_db_chart__is_delete=0,plot_db_chart=C)
		if D.count()>0:G=D[0];G.is_delete=_C;G.save();print('Deleted plotDB')
	return{_A:1}
def sparta_15bd86cc07(token_permission):
	A=PlotDBPermission.objects.filter(token=token_permission)
	if A.count()>0:B=A[A.count()-1];return{_A:1,_K:B.plot_db_chart}
	return{_A:-1}
def has_permission_widget_or_shared_rights(plot_db_chart_obj,user_obj,password_widget=_B):
	B=user_obj;A=plot_db_chart_obj;F=A.has_widget_password;C=_D
	if B.is_authenticated:
		D=sparta_7d8d6d46a2(B)
		if len(D)>0:E=PlotDBChartShared.objects.filter(Q(is_delete=0,user_group__in=D,plot_db_chart__is_delete=0,plot_db_chart=A)|Q(is_delete=0,user=B,plot_db_chart__is_delete=0,plot_db_chart=A))
		else:E=PlotDBChartShared.objects.filter(is_delete=0,user=B,plot_db_chart__is_delete=0,plot_db_chart=A)
		if E.count()>0:C=_C
	if C:return _C
	if A.is_expose_widget:
		if A.is_public_widget:
			if not F:return _C
			else:
				try:
					if qube_e3b4c78a63.sparta_44317619db(A.widget_password_e)==password_widget:return _C
					else:return _D
				except:return _D
		else:return _D
	return _D
def sparta_c54ed50773(plot_chart_id,user_obj,password_widget=_B):
	F=password_widget;E=plot_chart_id;C=user_obj;logger.debug('CHECK NOW has_widget_access:');B=PlotDBChart.objects.filter(plot_chart_id__startswith=E,is_delete=_D).all();D=_D
	if B.count()==1:D=_C
	else:
		I=E;B=PlotDBChart.objects.filter(slug__startswith=I,is_delete=_D).all()
		if B.count()==1:D=_C
	if D:
		A=B[B.count()-1];J=A.has_widget_password
		if A.is_expose_widget:
			if A.is_public_widget:
				if not J:return{_A:1,_K:A}
				elif F is _B:return{_A:2,_E:'Require password',_K:A}
				else:
					try:
						if qube_e3b4c78a63.sparta_44317619db(A.widget_password_e)==F:return{_A:1,_K:A}
						else:return{_A:3,_E:_AB,_K:A}
					except:return{_A:3,_E:_AB,_K:A}
			elif C.is_authenticated:
				G=sparta_7d8d6d46a2(C)
				if len(G)>0:H=PlotDBChartShared.objects.filter(Q(is_delete=0,user_group__in=G,plot_db_chart__is_delete=0,plot_db_chart=A)|Q(is_delete=0,user=C,plot_db_chart__is_delete=0,plot_db_chart=A))
				else:H=PlotDBChartShared.objects.filter(is_delete=0,user=C,plot_db_chart__is_delete=0,plot_db_chart=A)
				if H.count()>0:return{_A:1,_K:A}
			else:return{_A:-1}
	return{_A:-1}
def sparta_0c66b66e60(plot_chart_id,user_obj):
	F=plot_chart_id;C=user_obj;A=PlotDBChart.objects.filter(plot_chart_id__startswith=F,is_delete=_D).all();D=_D
	if A.count()==1:D=_C
	else:
		H=F;A=PlotDBChart.objects.filter(slug__startswith=H,is_delete=_D).all()
		if A.count()==1:D=_C
	if D:
		B=A[A.count()-1];G=sparta_7d8d6d46a2(C)
		if len(G)>0:E=PlotDBChartShared.objects.filter(Q(is_delete=0,user_group__in=G,plot_db_chart__is_delete=0,plot_db_chart=B)|Q(is_delete=0,user=C,plot_db_chart__is_delete=0,plot_db_chart=B))
		else:E=PlotDBChartShared.objects.filter(is_delete=0,user=C,plot_db_chart__is_delete=0,plot_db_chart=B)
		if E.count()>0:I=E[0];B=I.plot_db_chart;return{_A:1,_i:_C,_K:B}
	return{_A:1,_i:_D}
def sparta_b9cf13af86(plot_db_chart_obj):
	B=json.loads(plot_db_chart_obj.chart_config);C=dict();E={'xAxisArr':'x','yAxisArr':'y',_AG:'r',_AF:_AE,'ohlcvArr':'ohlcv',_AH:'shaded_background'}
	for A in B.keys():
		if A in INPUTS_KEYS:
			try:
				F=E[A]
				if B[A]is not _B:
					D=len([A for A in B[A]if A is not _B])
					if D>0:C[F]=D
			except Exception as G:logger.debug('Except input struct');logger.debug(G)
	return C
def sparta_e23fda3c74(json_data,user_obj):
	B=user_obj;D=sparta_7d8d6d46a2(B)
	if len(D)>0:E=PlotDBChartShared.objects.filter(Q(is_delete=0,user_group__in=D,plot_db_chart__is_delete=0,plot_db_chart=A,plot_db_chart__is_expose_widget=_C)|Q(is_delete=0,user=B,plot_db_chart__is_delete=0,plot_db_chart__is_expose_widget=_C))
	else:E=PlotDBChartShared.objects.filter(is_delete=0,user=B,plot_db_chart__is_delete=0,plot_db_chart__is_expose_widget=_C)
	F=[]
	for C in E:
		A=C.plot_db_chart;I=C.share_rights;G=_B
		try:G=str(A.last_update.strftime(_P))
		except:pass
		H=_B
		try:H=str(A.date_created.strftime(_P))
		except Exception as J:logger.debug(J)
		F.append({_G:A.plot_chart_id,_h:A.type_chart,_v:A.has_widget_password,_w:A.is_public_widget,_J:A.name,'slug':A.slug,_L:A.description,_x:C.is_owner,_AS:I.has_write_rights,_A8:G,_A9:H})
	return{_A:1,_AT:F}
def sparta_c080656c6a(json_data,user_obj):
	E=user_obj;B=json_data;K=B[_G];L=B['isCalledFromLibrary'];F=PlotDBChart.objects.filter(plot_chart_id=K,is_delete=_D).all()
	if F.count()>0:
		A=F[F.count()-1];H=sparta_7d8d6d46a2(E)
		if len(H)>0:G=PlotDBChartShared.objects.filter(Q(is_delete=0,user_group__in=H,plot_db_chart__is_delete=0,plot_db_chart=A)|Q(is_delete=0,user=E,plot_db_chart__is_delete=0,plot_db_chart=A))
		else:G=PlotDBChartShared.objects.filter(is_delete=0,user=E,plot_db_chart__is_delete=0,plot_db_chart=A)
		if G.count()>0:
			M=G[0];I=M.share_rights
			if I.is_admin or I.has_write_rights:
				N=B[_M];C=_B
				if N:C=B[_s];C=qube_e3b4c78a63.sparta_5ff3a13eb1(C)
				J=datetime.now().astimezone(UTC);A.has_widget_password=B[_M];A.widget_password_e=C;A.name=B[_t];A.plotDes=B[_A4];A.is_expose_widget=B[_A5];A.is_public_widget=B[_u];A.is_static_data=B[_A3];A.last_update=J;A.save()
				if L:0
				else:
					D=A.code_editor_notebook
					if D is not _B:D.cells=B[_A2];D.last_update=J;D.save()
	return{_A:1}
def sparta_18f8988986(json_data,user_obj):
	D=user_obj;B=json_data;I=B[_G];E=PlotDBChart.objects.filter(plot_chart_id=I,is_delete=_D).all()
	if E.count()>0:
		A=E[E.count()-1];G=sparta_7d8d6d46a2(D)
		if len(G)>0:F=PlotDBChartShared.objects.filter(Q(is_delete=0,user_group__in=G,plot_db_chart__is_delete=0,plot_db_chart=A)|Q(is_delete=0,user=D,plot_db_chart__is_delete=0,plot_db_chart=A))
		else:F=PlotDBChartShared.objects.filter(is_delete=0,user=D,plot_db_chart__is_delete=0,plot_db_chart=A)
		if F.count()>0:
			J=F[0];H=J.share_rights
			if H.is_admin or H.has_write_rights:
				K=B[_M];C=_B
				if K:C=B[_s];C=qube_e3b4c78a63.sparta_5ff3a13eb1(C)
				L=datetime.now().astimezone(UTC);A.has_widget_password=B[_M];A.is_public_widget=B[_u];A.widget_password_e=C;A.last_update=L;A.save()
	return{_A:1}
def sparta_969302082e(json_data,user_obj):
	B=user_obj;G=json_data[_G];C=PlotDBChart.objects.filter(plot_chart_id=G,is_delete=_D).all()
	if C.count()>0:
		A=C[C.count()-1];E=sparta_7d8d6d46a2(B)
		if len(E)>0:D=PlotDBChartShared.objects.filter(Q(is_delete=0,user_group__in=E,plot_db_chart__is_delete=0,plot_db_chart=A)|Q(is_delete=0,user=B,plot_db_chart__is_delete=0,plot_db_chart=A))
		else:D=PlotDBChartShared.objects.filter(is_delete=0,user=B,plot_db_chart__is_delete=0,plot_db_chart=A)
		if D.count()>0:
			H=D[0];F=H.share_rights
			if F.is_admin or F.has_write_rights:I=datetime.now().astimezone(UTC);A.is_expose_widget=_D;A.last_update=I;A.save()
	return{_A:1}
def sparta_67d3369ad0(user_obj):
	B=user_obj;C=sparta_7d8d6d46a2(B)
	if len(C)>0:D=PlotDBChartShared.objects.filter(Q(is_delete=0,user_group__in=C,plot_db_chart__is_delete=0,plot_db_chart=A,plot_db_chart__is_expose_widget=_C)|Q(is_delete=0,user=B,plot_db_chart__is_delete=0,plot_db_chart__is_expose_widget=_C))
	else:D=PlotDBChartShared.objects.filter(is_delete=0,user=B,plot_db_chart__is_delete=0,plot_db_chart__is_expose_widget=_C)
	E=[]
	for F in D:
		A=F.plot_db_chart;J=F.share_rights;G=_B
		try:G=str(A.last_update.strftime(_P))
		except:pass
		H=_B
		try:H=str(A.date_created.strftime(_P))
		except Exception as I:logger.debug(I)
		E.append({'id':A.plot_chart_id,_J:A.name,_L:A.description,_A8:G,_A9:H})
	return E
def sparta_4766ab7476(json_data,user_obj):
	try:A=sparta_0c66b66e60(json_data[_AX],user_obj);B=A[_i];return{_A:1,_i:B}
	except:pass
	return{_A:-1}
def sparta_11db3e854e(json_data,user_obj):
	B=user_obj;A=json_data;C=sparta_0c66b66e60(A[_AX],B);D=C[_i]
	if D:E=C[_K];A[_G]=E.plot_chart_id;F=sparta_ae685aa3e9(A,B);return{_A:1,_F:[A[_F]for A in F[_AA]]}
	return{_A:-1}
def sparta_26efc55c5c(json_data,user_obj):
	F='Error quantstats';C=user_obj;A=json_data;from project.sparta_3bc15131c6.sparta_1ec16518f2 import qube_cbbd424db9 as D;E=A['service']
	if E=='quantstats':
		try:return D.sparta_602dd07419(A,C)
		except Exception as B:logger.debug(F);logger.debug(traceback.format_exc());logger.debug(F);return{_A:-1,_E:str(B)}
	elif E=='matplotlib':
		try:return D.sparta_23dde1dc3c(A,C)
		except Exception as B:logger.debug('Error matpltlib');logger.debug(traceback.format_exc());return{_A:-1,_E:str(B)}
	return{_A:1}
def sparta_817c9f8581(json_data,user_obj):
	B=json_data;import quantstats as K;B=B[_F];G=B[_AY];L=B[_AZ];H=B['columnsX'];I=B[_r];F=L;C=I
	if len(H)>1:C=H[1:]+I;F=G[1:]+F
	A=pd.DataFrame(F).T;A.index=pd.to_datetime(G[0]);A.columns=C
	try:A.index=A.index.tz_localize('UTC')
	except:pass
	for E in C:
		try:A[E]=A[E].astype(float)
		except:pass
	M=A.pct_change();D=pd.DataFrame()
	for(N,E)in enumerate(C):
		J=K.reports.metrics(M[E],mode='basic',display=_D)
		if N==0:D=J
		else:D=pd.concat([D,J],axis=1)
	D.columns=C;return{_A:1,'metrics':D.to_json(orient=_A1)}
def sparta_0db17ad966(json_data,user_obj):
	N='Salary';A=json_data;A=A[_F];O=A[_AY];P=A[_AZ];G=A['columnsX'];H=A[_r];C=P;I=H
	if len(G)>1:I=G+H;C=O+C
	D=pd.DataFrame(C).T;D.columns=I;E=['Country','City'];J=[N,'Rent'];J=[N];D.set_index(E,inplace=_C);B=D.groupby(E).mean();logger.debug('res_group_by_df');logger.debug(B);Q=E;F=len(B.index[0]);K=sorted(list(set(B.index.get_level_values(F-2))));L=[]
	def M(this_df,level=0,previous_index_list=_B):
		D=previous_index_list;C=this_df;A=level
		if A==F-1:
			for H in J:L.append({_F:[0]*len(K),_F:C[H].tolist(),_AE:list(C.index.get_level_values(A)),'hierarchy':D,_AD:H,'label':D[-1]})
		elif A<F-1:
			I=sorted(list(set(B.index.get_level_values(A))))
			for E in I:
				if D is _B:G=[E]
				else:G=D.copy();G.append(E)
				M(C[C.index.get_level_values(A)==E],A+1,G)
	M(B);logger.debug('chart_data');return{_A:1,_AC:L,_AE:K}