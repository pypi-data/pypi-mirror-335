_B=False
_A=None
import os,json,platform,websocket,threading,time,pandas as pd
from pathlib import Path
from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from project.logger_config import logger
from project.sparta_d3863a192d.sparta_3c800a8540 import qube_a8d0eb6c62 as qube_a8d0eb6c62
from project.sparta_6d49f7e4f5.sparta_bb74460757 import qube_795f848f90 as qube_795f848f90
from project.sparta_6d49f7e4f5.sparta_902927134a.qube_5aa94b9e67 import sparta_8363a03cbe
from project.sparta_6d49f7e4f5.sparta_902927134a.qube_c18b61af6f import sparta_0822b32c7f
from project.sparta_6d49f7e4f5.sparta_bb74460757.qube_795f848f90 import convert_to_dataframe,convert_dataframe_to_json,sparta_cfece85c36
from project.sparta_6d49f7e4f5.sparta_5adaec37f1.qube_c0a51f1ec6 import SenderKernel
from project.sparta_6d49f7e4f5.sparta_dac0a6d98d.qube_b950b30269 import sparta_8d5a029b4d,sparta_2f4f0ad181,get_api_key_async
class NotebookWS(AsyncWebsocketConsumer):
	channel_session=True;http_user_and_session=True
	async def connect(A):logger.debug('Connect Now');await A.accept();A.user=A.scope['user'];A.json_data_dict=dict();A.sender_kernel_obj=_A
	async def disconnect(A,close_code=_A):
		logger.debug('Disconnect')
		if A.sender_kernel_obj is not _A:A.sender_kernel_obj.zmq_close()
		try:await A.close()
		except:pass
	async def notebook_permission_code_exec(A,json_data):from project.sparta_6d49f7e4f5.sparta_f346ee3364 import qube_713337071c as B;return await coreNotebook.notebook_permission_code_exec(json_data)
	async def prepare_sender_kernel(A,kernel_manager_uuid):
		from project.models import KernelProcess as C;B=await sync_to_async(lambda:list(C.objects.filter(kernel_manager_uuid=kernel_manager_uuid)),thread_sensitive=_B)()
		if len(B)>0:
			D=B[0];E=D.port
			if A.sender_kernel_obj is _A:A.sender_kernel_obj=SenderKernel(A,E)
			A.sender_kernel_obj.zmq_connect()
	async def get_kernel_type(D,kernel_manager_uuid):
		from project.models import KernelProcess as B;A=await sync_to_async(lambda:list(B.objects.filter(kernel_manager_uuid=kernel_manager_uuid)),thread_sensitive=_B)()
		if len(A)>0:C=A[0];return C.type
		return 1
	async def receive(B,text_data):
		AL='kernel_variable_arr';AK='workspace_variables_to_update';AJ='repr_data';AI='raw_data';AH='cellTitleVarName';AG='execCodeTitle';AF='cellId';AE='cell_id';AD='cellCode';AC='activate_venv';AB='venv_name';AA='import json\n';t=text_data;s='updated_variables';r='output';q='defaultDashboardVars';m='assignGuiComponentVariable';l='variable';k='get_workspace_variable';j='json_data';i='value';Z='get_kernel_variable_repr';Y='code';T='errorMsg';Q='dashboardVenv';P='execute_code';N='\n';M='';K='kernel_variable';J='cmd';F='res';D='service'
		if len(t)>0:
			A=json.loads(t);logger.debug('-'*100);logger.debug(f"NOTEBOOK KERNEL json_data");logger.debug(A);E=A[D];u=A['kernelManagerUUID'];await B.prepare_sender_kernel(u);AM=await B.get_kernel_type(u)
			def W(code_to_exec,json_data):
				C=json_data;B=code_to_exec;A=AA
				if q in C:
					E=C[q]
					for(D,F)in E.items():G=F['outputDefaultValue'];A+=f'if "{D}" in globals():\n    pass\nelse:\n    {D} = {repr(G)}\n'
				H=json.dumps({i:_A,'col':-1,'row':-1});A+=f"if \"last_action_state\" in globals():\n    pass\nelse:\n    last_action_state = json.loads('{H}')\n"
				if len(A)>0:B=f"{A}\n{B}"
				return B
			async def R(json_data):
				E='projectSysPath';C=json_data
				if E in C:
					if len(C[E])>0:A=sparta_cfece85c36(C[E]);A=Path(A).resolve();F=f'import sys, os\nsys.path.insert(0, r"{str(A)}")\nos.chdir(r"{str(A)}")\n';await B.sender_kernel_obj.send_zmq_request({D:P,J:F})
			async def a(json_data):
				A=json_data
				if Q in A:
					if A[Q]is not _A:
						if len(A[Q])>0:C=A[Q];await B.sender_kernel_obj.send_zmq_request({D:AC,AB:C})
			if E=='init-socket'or E=='reconnect-kernel'or E=='reconnect-kernel-run-all':
				G={F:1,D:E}
				if q in A:I=W(M,A);await B.sender_kernel_obj.send_zmq_request({D:P,J:I})
				await R(A);await a(A);C=json.dumps(G);await B.send(text_data=C);return
			elif E=='disconnect':B.disconnect()
			elif E=='exec':
				await R(A);AN=time.time();logger.debug('='*50);b=A[AD];I=b
				if AM==5:logger.debug('Execute for the notebook Execution Exec case');logger.debug(A);I=await B.notebook_permission_code_exec(A)
				I=W(I,A);v=_B
				if b is not _A:
					if len(b)>0:
						if b[0]=='!':v=True
				if v:await B.sender_kernel_obj.send_zmq_request({D:'execute_shell',J:I,j:json.dumps(A)})
				else:await B.sender_kernel_obj.send_zmq_request({D:'execute',J:I,j:json.dumps(A)})
				try:w=sparta_8363a03cbe(A[AD])
				except:w=[]
				logger.debug('='*50);AO=time.time()-AN;C=json.dumps({F:2,D:E,'elapsed_time':round(AO,2),AE:A[AF],'updated_plot_variables':w,'input':json.dumps(A)});await B.send(text_data=C)
			elif E=='trigger-code-gui-component-input':
				R(A)
				try:
					try:c=json.loads(A[AG]);L=N.join([A[Y]for A in c])
					except:L=M
					AP=json.loads(A['execCodeInput']);x=N.join([A[Y]for A in AP]);U=W(x,A);U+=N+L;await B.sender_kernel_obj.send_zmq_request(sender_dict={D:P,J:U},b_send_websocket_msg=_B);V=sparta_8363a03cbe(x);y=A['guiInputVarName'];AQ=A['guiOutputVarName'];AR=A[AH];n=[y,AQ,AR];X=[]
					for S in n:
						try:O=await B.sender_kernel_obj.send_zmq_request({D:Z,K:S})
						except:O=json.dumps({F:1,r:M})
						o=convert_dataframe_to_json(convert_to_dataframe(await B.sender_kernel_obj.send_zmq_request({D:k,K:S}),y));X.append({l:S,AI:o,AJ:O})
				except Exception as H:C=json.dumps({F:-1,D:E,T:str(H)});logger.debug('Error',C);await B.send(text_data=C);return
				C=json.dumps({F:1,D:E,s:V,AK:X});await B.send(text_data=C)
			elif E=='trigger-code-gui-component-output':
				R(A)
				try:
					z=M;d=M
					if m in A:e=A[m];A0=sparta_0822b32c7f(e);z=A0['assign_state_variable'];d=A0['assign_code']
					AS=json.loads(A['execCodeOutput']);A1=N.join([A[Y]for A in AS]);U=d+N;U+=z+N;U+=A1;await B.sender_kernel_obj.send_zmq_request(sender_dict={D:P,J:U},b_send_websocket_msg=_B);V=sparta_8363a03cbe(A1)
					try:V.append(A[m][l])
					except Exception as H:pass
				except Exception as H:C=json.dumps({F:-1,D:E,T:str(H)});await B.send(text_data=C);return
				C=json.dumps({F:1,D:E,s:V});logger.debug(f"return final here {C}");await B.send(text_data=C)
			elif E=='assign-kernel-variable-from-gui':
				try:e=A[m];AT=e[i];d=f"{e[l]} = {AT}";await B.sender_kernel_obj.send_zmq_request({D:P,J:d})
				except Exception as H:C=json.dumps({F:-1,D:E,T:str(H)});await B.send(text_data=C);return
				C=json.dumps({F:1,D:E});await B.send(text_data=C)
			elif E=='exec-main-dashboard-notebook-init':
				await R(A);await a(A);I=A['dashboardFullCode'];I=W(I,A)
				try:await B.sender_kernel_obj.send_zmq_request({D:P,J:I},b_send_websocket_msg=_B)
				except Exception as H:C=json.dumps({F:-1,D:E,T:str(H)});await B.send(text_data=C);return
				A2=A['plotDBRawVariablesList'];AU=A2;A3=[];A4=[]
				for p in A2:
					try:A3.append(convert_dataframe_to_json(convert_to_dataframe(await B.sender_kernel_obj.send_zmq_request({D:k,K:p}),p)));A4.append(await B.sender_kernel_obj.send_zmq_request({D:Z,K:p}))
					except Exception as H:logger.debug('Except get var');logger.debug(H)
				C=json.dumps({F:1,D:E,'variables_names':AU,'variables_raw':A3,'variables_repr':A4});await B.send(text_data=C)
			elif E=='trigger-action-plot-db':
				logger.debug('TRIGGER CODE ACTION PLOTDB');logger.debug(A)
				try:
					f=AA;f+=f"last_action_state = json.loads('{A['actionDict']}')\n"
					try:g=json.loads(A['triggerCode']);g=N.join([A[Y]for A in c])
					except:g=M
					f+=N+g;logger.debug('cmd to execute');logger.debug('cmd_to_exec');logger.debug(f);await B.sender_kernel_obj.send_zmq_request({D:P,J:f});V=sparta_8363a03cbe(g)
				except Exception as H:C=json.dumps({F:-1,D:E,T:str(H)});await B.send(text_data=C);return
				C=json.dumps({F:1,D:E,s:V});await B.send(text_data=C)
			elif E=='dynamic-title':
				try:c=json.loads(A[AG]);L=N.join([A[Y]for A in c])
				except:L=M
				if len(L)>0:
					L=W(L,A);await R(A);await a(A)
					try:
						await B.sender_kernel_obj.send_zmq_request({D:P,J:L});A5=A[AH];n=[A5];X=[]
						for S in n:
							try:O=await B.sender_kernel_obj.send_zmq_request({D:Z,K:S})
							except:O=json.dumps({F:1,r:M})
							o=convert_dataframe_to_json(convert_to_dataframe(await B.sender_kernel_obj.send_zmq_request({D:k,K:S}),A5));X.append({l:S,AI:o,AJ:O})
						C=json.dumps({F:1,D:E,AK:X});await B.send(text_data=C)
					except Exception as H:C=json.dumps({F:-1,D:E,T:str(H)});logger.debug('Error',C);logger.debug(L);await B.send(text_data=C);return
			elif E=='reset':await B.sender_kernel_obj.send_zmq_request({D:'reset_kernel_workspace'});await a(A);G={F:1,D:E};C=json.dumps(G);await B.send(text_data=C)
			elif E=='workspace-list':AV=await B.sender_kernel_obj.send_zmq_request({D:'list_workspace_variables'});G={F:1,D:E,'workspace_variables':AV};G.update(A);C=json.dumps(G);await B.send(text_data=C)
			elif E=='workspace-get-variable-as-df':
				print('SANS FIN LA PTUAINDE SA MERE');A6=[];A7=[];A8=[]
				for h in A[AL]:
					A9=await B.sender_kernel_obj.send_zmq_request({D:k,K:h});print('workspace_variable FUCK FUCK SANS FIN');print(A9);AW=convert_to_dataframe(A9,variable_name=h)
					try:A6.append(convert_dataframe_to_json(AW));A7.append(h)
					except:pass
					try:O=await B.sender_kernel_obj.send_zmq_request({D:Z,K:h})
					except:O=json.dumps({F:1,r:M})
					A8.append(O)
				G={F:1,D:E,AL:A7,'workspace_variable_arr':A6,'kernel_variable_repr_arr':A8};C=json.dumps(G);await B.send(text_data=C)
			elif E=='workspace-get-variable'or E=='workspace-get-variable-preview':AX=await B.sender_kernel_obj.send_zmq_request({D:Z,K:A[K]});G={F:1,D:E,AE:A.get(AF,_A),'workspace_variable':AX};C=json.dumps(G);await B.send(text_data=C)
			elif E=='workspace-set-variable-from-datasource':
				if i in list(A.keys()):await B.sender_kernel_obj.send_zmq_request({D:'set_workspace_variable_from_datasource',j:json.dumps(A)});G={F:1,D:E};C=json.dumps(G);await B.send(text_data=C)
			elif E=='workspace-set-variable':
				if i in list(A.keys()):await B.sender_kernel_obj.send_zmq_request({D:'set_workspace_variable',j:json.dumps(A)});G={F:1,D:E};C=json.dumps(G);await B.send(text_data=C)
			elif E=='set-sys-path-import':
				if'projectPath'in A:await R(A)
				G={F:1,D:E};C=json.dumps(G);await B.send(text_data=C)
			elif E=='set-kernel-venv':
				if Q in A:
					if A[Q]is not _A:
						if len(A[Q])>0:AY=A[Q];await B.sender_kernel_obj.send_zmq_request({D:AC,AB:AY})
				G={F:1,D:E};C=json.dumps(G);await B.send(text_data=C)
			elif E=='deactivate-venv':await B.sender_kernel_obj.send_zmq_request({D:'deactivate_venv'});G={F:1,D:E};C=json.dumps(G);await B.send(text_data=C)
			elif E=='get-widget-iframe':
				logger.debug('Deal with iframe here');from IPython.core.display import display,HTML;import warnings as AZ;AZ.filterwarnings('ignore',message='Consider using IPython.display.IFrame instead',category=UserWarning)
				try:Aa=A['widget_id'];Ab=await get_api_key_async(B.user);Ac=await sync_to_async(lambda:HTML(f'<iframe src="/plot-widget/{Aa}/{Ab}" width="100%" height="500" frameborder="0" allow="clipboard-write"></iframe>').data)();G={F:1,D:E,'widget_iframe':Ac};C=json.dumps(G);await B.send(text_data=C)
				except Exception as H:G={F:-1,T:str(H)};C=json.dumps(G);await B.send(text_data=C)