_F='output'
_E=None
_D=False
_C='name'
_B='utf-8'
_A='res'
import os,sys,json,ast,re,base64,uuid,hashlib,socket,cloudpickle,websocket,subprocess,threading
from random import randint
import pandas as pd
from pathlib import Path
from cryptography.fernet import Fernet
from subprocess import PIPE
from datetime import datetime,timedelta
from django.contrib.auth.models import User
from django.db.models import Q
from django.core.cache import cache
from django.conf import settings as conf_settings
from asgiref.sync import sync_to_async
import pytz
UTC=pytz.utc
from spartaqube_app.path_mapper_obf import sparta_3acf216d77
from project.models import UserProfile,NewPlotApiVariables,NotebookShared,DashboardShared
from project.sparta_6d49f7e4f5.sparta_c59310761b import qube_6ff33ab51c as qube_6ff33ab51c
from project.sparta_6d49f7e4f5.sparta_eed2ac8b74 import qube_f98e616a62 as qube_f98e616a62
from project.sparta_6d49f7e4f5.sparta_bb74460757.qube_795f848f90 import convert_to_dataframe,convert_dataframe_to_json,sparta_cfece85c36
from project.sparta_6d49f7e4f5.sparta_bb74460757.qube_74042b161e import sparta_9bd4d72961,sparta_b9ec499999
from project.logger_config import logger
def sparta_e71774cdcf():keygen_fernet='spartaqube-api-key';key=keygen_fernet.encode(_B);key=hashlib.md5(key).hexdigest();key=base64.b64encode(key.encode(_B));return key.decode(_B)
def sparta_d835bc29fe():keygen_fernet='spartaqube-internal-decoder-api-key';key=keygen_fernet.encode(_B);key=hashlib.md5(key).hexdigest();key=base64.b64encode(key.encode(_B));return key.decode(_B)
def sparta_e79f05a8f2(f,str_to_encrypt):data_to_encrypt=str_to_encrypt.encode(_B);token=f.encrypt(data_to_encrypt).decode(_B);token=base64.b64encode(token.encode(_B)).decode(_B);return token
def sparta_237f719939(api_token_id):
	if api_token_id=='public':
		try:return User.objects.filter(email='public@spartaqube.com').all()[0]
		except:return
	try:
		f_private=Fernet(sparta_d835bc29fe().encode(_B));api_key=f_private.decrypt(base64.b64decode(api_token_id)).decode(_B).split('@')[1];user_profile_set=UserProfile.objects.filter(api_key=api_key,is_banned=_D).all()
		if user_profile_set.count()==1:return user_profile_set[0].user
		return
	except Exception as e:logger.debug('Could not authenticate api with error msg:');logger.debug(e);return
def sparta_2f4f0ad181(user_obj):
	userprofile_obj=UserProfile.objects.get(user=user_obj);api_key=userprofile_obj.api_key
	if api_key is _E:api_key=str(uuid.uuid4());userprofile_obj.api_key=api_key;userprofile_obj.save()
	return api_key
async def get_api_key_async_DEPREC(user_obj):
	userprofile_obj=await UserProfile.objects.aget(user=user_obj);api_key=userprofile_obj.api_key
	if api_key is _E:api_key=str(uuid.uuid4());userprofile_obj.api_key=api_key;await userprofile_obj.asave()
	return api_key
async def get_api_key_async(user_obj):
	userprofile_obj=await sync_to_async(lambda:UserProfile.objects.get(user=user_obj),thread_sensitive=_D)()
	if userprofile_obj.api_key is _E:userprofile_obj.api_key=str(uuid.uuid4());await sync_to_async(userprofile_obj.save,thread_sensitive=_D)()
	return userprofile_obj.api_key
def sparta_8d5a029b4d(user_obj,domain_name):api_key=sparta_2f4f0ad181(user_obj);random_nb=str(randint(0,1000));data_to_encrypt=f"apikey@{api_key}@{random_nb}";f_private=Fernet(sparta_d835bc29fe().encode(_B));private_encryption=sparta_e79f05a8f2(f_private,data_to_encrypt);data_to_encrypt=f"apikey@{domain_name}@{private_encryption}";f_public=Fernet(sparta_e71774cdcf().encode(_B));public_encryption=sparta_e79f05a8f2(f_public,data_to_encrypt);return public_encryption
def sparta_f6a5acfc61(json_data,user_obj):api_key=sparta_2f4f0ad181(user_obj);domain_name=json_data['domain'];public_encryption=sparta_8d5a029b4d(user_obj,domain_name);return{_A:1,'token':public_encryption}
def sparta_de5f321c7c(json_data,user_obj):userprofile_obj=UserProfile.objects.get(user=user_obj);api_key=str(uuid.uuid4());userprofile_obj.api_key=api_key;userprofile_obj.save();return{_A:1}
def sparta_4c6f48fb7d():plot_types=sparta_9bd4d72961();plot_types=sorted(plot_types,key=lambda x:x['Library'].lower(),reverse=_D);return{_A:1,'plot_types':plot_types}
def sparta_adf356536c(json_data):logger.debug('DEBUG get_plot_options json_data');logger.debug(json_data);plot_type=json_data['plot_type'];plot_input_options_dict=sparta_b9ec499999(plot_type);plot_input_options_dict[_A]=1;return plot_input_options_dict
def sparta_57cfd1e868(code):
	tree=ast.parse(code)
	if isinstance(tree.body[-1],ast.Expr):last_expr_node=tree.body[-1].value;last_expr_code=ast.unparse(last_expr_node);return last_expr_code
	else:return
def sparta_cb7a27d88a(json_data,user_obj):
	A='errorMsg';user_code_example=json_data['userCode'];resp=_E;error_msg=''
	try:
		logger.debug('EXECUTE API EXAMPLE DEBUG DEBUG DEBUG');api_key=sparta_2f4f0ad181(user_obj);core_api_path=sparta_3acf216d77()['project/core/api'];ini_code='import os, sys\n';ini_code+=f'sys.path.insert(0, r"{str(core_api_path)}")\n';ini_code+='from spartaqube import Spartaqube as Spartaqube\n';ini_code+=f"Spartaqube('{api_key}')\n";user_code_example=ini_code+'\n'+user_code_example;exec(user_code_example,globals());last_expression_str=sparta_57cfd1e868(user_code_example)
		if last_expression_str is not _E:
			last_expression_output=eval(last_expression_str)
			if last_expression_output.__class__.__name__=='HTML':resp=last_expression_output.data
			else:resp=last_expression_output
			resp=json.dumps(resp);return{_A:1,'resp':resp,A:error_msg}
		return{_A:-1,A:'No output to display. You should put the variable to display as the last line of the code'}
	except Exception as e:return{_A:-1,A:str(e)}
def sparta_559bff7a41(json_data,user_obj):
	session_id=json_data['session'];new_plot_api_variables_set=NewPlotApiVariables.objects.filter(session_id=session_id).all();logger.debug(f"gui_plot_api_variables with session_id {session_id}");logger.debug(new_plot_api_variables_set)
	if new_plot_api_variables_set.count()>0:
		new_plot_api_variables_obj=new_plot_api_variables_set[0];pickled_variables=new_plot_api_variables_obj.pickled_variables;unpickled_data=cloudpickle.loads(pickled_variables.encode('latin1'));notebook_variables=[]
		for notebook_variable in unpickled_data:
			notebook_variables_df=convert_to_dataframe(notebook_variable)
			if notebook_variables_df is not _E:0
			else:notebook_variables_df=pd.DataFrame()
			notebook_variables.append(convert_dataframe_to_json(notebook_variables_df))
		logger.debug(notebook_variables);return{_A:1,'notebook_variables':notebook_variables}
	return{_A:-1}
def sparta_b24954a9c2(json_data,user_obj):widget_id=json_data['widgetId'];return qube_f98e616a62.sparta_b24954a9c2(user_obj,widget_id)
def sparta_a94b699e48(json_data,user_obj):
	api_service=json_data['api_service']
	if api_service=='get_status':output=sparta_fdc451991e()
	elif api_service=='get_status_ws':return sparta_04dbe32370()
	elif api_service=='get_connectors':return sparta_65265b6bd9(json_data,user_obj)
	elif api_service=='get_connector_tables':return sparta_028a172f3e(json_data,user_obj)
	elif api_service=='get_data_from_connector':return sparta_d2927f7855(json_data,user_obj)
	elif api_service=='get_widgets':output=sparta_8d1a7156f1(user_obj)
	elif api_service=='has_widget_id':return sparta_680080e5db(json_data,user_obj)
	elif api_service=='get_widget_data':return sparta_cbc297a2f5(json_data,user_obj)
	elif api_service=='get_plot_types':return sparta_9bd4d72961()
	return{_A:1,_F:output}
def sparta_fdc451991e():return 1
def sparta_65265b6bd9(json_data,user_obj):
	A='db_connectors';keys_to_retain=['connector_id',_C,'db_engine'];res_dict=qube_f98e616a62.sparta_f1f3dd35f1(json_data,user_obj)
	if res_dict[_A]==1:res_dict[A]=[{k:d[k]for k in keys_to_retain if k in d}for d in res_dict[A]]
	return res_dict
def sparta_028a172f3e(json_data,user_obj):res_dict=qube_f98e616a62.sparta_0339427124(json_data,user_obj);return res_dict
def sparta_d2927f7855(json_data,user_obj):res_dict=qube_f98e616a62.sparta_a8a301ea84(json_data,user_obj);return res_dict
def sparta_8d1a7156f1(user_obj):return qube_f98e616a62.sparta_cf5f8ed06f(user_obj)
def sparta_680080e5db(json_data,user_obj):return qube_f98e616a62.sparta_4ed82e58f9(json_data,user_obj)
def sparta_cbc297a2f5(json_data,user_obj):return qube_f98e616a62.sparta_a12bade0e6(json_data,user_obj)
def sparta_d296beab1e(json_data,user_obj):date_now=datetime.now().astimezone(UTC);session_id=str(uuid.uuid4());pickled_data=json_data['data'];NewPlotApiVariables.objects.create(user=user_obj,session_id=session_id,pickled_variables=pickled_data,date_created=date_now,last_update=date_now);return{_A:1,'session_id':session_id}
def sparta_50b57f41ae():return sparta_9bd4d72961()
def sparta_b03876feac():cache.clear();return{_A:1}
def sparta_04dbe32370():
	global is_wss_valid;is_wss_valid=_D
	try:
		api_path=sparta_3acf216d77()['api']
		with open(os.path.join(api_path,'app_data_asgi.json'),'r')as json_file:loaded_data_dict=json.load(json_file)
		ASGI_PORT=int(loaded_data_dict['default_port'])
	except:ASGI_PORT=5664
	logger.debug('ASGI_PORT');logger.debug(ASGI_PORT)
	def on_open(ws):global is_wss_valid;is_wss_valid=True;ws.close()
	def on_error(ws,error):global is_wss_valid;is_wss_valid=_D;ws.close()
	def on_close(ws,close_status_code,close_msg):
		try:logger.debug(f"Connection closed with code: {close_status_code}, message: {close_msg}");ws.close()
		except Exception as e:logger.debug(f"Except: {e}")
	ws=websocket.WebSocketApp(f"ws://127.0.0.1:{ASGI_PORT}/ws/statusWS",on_open=on_open,on_close=on_close);ws.run_forever()
	if ws.sock and ws.sock.connected:logger.debug('WebSocket is still connected. Attempting to close again.');ws.close()
	else:logger.debug('WebSocket is properly closed.')
	return{_A:1,_F:is_wss_valid}
def sparta_d457e69c90(json_data,user_obj):
	H='displayText';G='Plot';F='dict';E='popTitle';D='other';C='preview';B='popType';A='type';api_methods=[{_C:'Spartaqube().get_connectors()',A:1,B:F,C:'',D:'',E:'Get Connectors'},{_C:'Spartaqube().get_connector_tables("connector_id")',A:1,B:F,C:'',D:'',E:'Get Connector Tables'},{_C:'Spartaqube().get_data_from_connector("connector_id", table=None, sql_query=None, output_format=None)',A:1,B:F,C:'',D:'',E:'Get Connector Data'},{_C:'Spartaqube().get_plot_types()',A:1,B:'list',C:'',D:'',E:'Get Plot Type'},{_C:'Spartaqube().get_widgets()',A:1,B:F,C:'',D:'',E:'Get Widgets list'},{_C:'Spartaqube().iplot([var1, var2], width="100%", height=750)',A:1,B:G,C:'',D:'-1',E:'Interactive plot'},{_C:'Spartaqube().plot(\n    x:list=None, y:list=None, r:list=None, legend:list=None, labels:list=None, ohlcv:list=None, shaded_background:list=None, \n    datalabels:list=None, border:list=None, background:list=None, border_style:list=None, tooltips_title:list=None, tooltips_label:list=None,\n    chart_type="line", interactive=True, widget_id=None, title=None, title_css:dict=None, stacked:bool=False, date_format:str=None, time_range:bool=False,\n    gauge:dict=None, gauge_zones:list=None, gauge_zones_labels:list=None, gauge_zones_height:list=None,\n    dataframe:pd.DataFrame=None, dates:list=None, returns:list=None, returns_bmk:list=None,\n    options:dict=None, width=\'100%\', height=750\n)',A:1,B:G,C:'',D:'-1',H:'Spartaqube().plot(...)',E:'Programmatic plot'}];api_widgets_suggestions=[]
	if not user_obj.is_anonymous:
		api_get_widgets=sparta_8d1a7156f1(user_obj)
		for widget_dict in api_get_widgets:widget_id_with_quote="'"+str(widget_dict['id'])+"'";widget_cmd=f"Spartaqube().get_widget({widget_id_with_quote})";api_widgets_suggestions.append({_C:widget_cmd,H:widget_dict[_C],E:widget_dict[_C],A:2,B:'Widget',C:widget_cmd,D:widget_dict['id']})
	autocomplete_suggestions_arr=api_methods+api_widgets_suggestions;return{_A:1,'suggestions':autocomplete_suggestions_arr}
def sparta_fadb3d60a4(notebook_id):
	notebook_shared_set=NotebookShared.objects.filter(is_delete=0,notebook__is_delete=0,notebook__notebook_id=notebook_id)
	if notebook_shared_set.count()>0:return notebook_shared_set[0].user
def sparta_73cec261eb(dashboard_id):
	dashboard_shared_set=DashboardShared.objects.filter(is_delete=0,dashboard__is_delete=0,dashboard__dashboard_id=dashboard_id)
	if dashboard_shared_set.count()>0:return dashboard_shared_set[0].user