_Z='stderr'
_Y='<IPY-INPUT>'
_X='<ipython-input-\\d+-[0-9a-f]+>'
_W='TRACEBACK RAISE EXCEPTION NOW'
_V='stdout'
_U='is_terminated'
_T='errorMsg'
_S='traceback'
_R='/*/*/*/*/*/*/*/*/*/*/*/*/*/*/*/*/*/*/*/*/*/*/*/*/*/*/*/'
_Q='text'
_P='idle'
_O='busy'
_N='type'
_M='\n'
_L='data'
_K='cell_id'
_J='exec'
_I='execution_state'
_H='output'
_G='content'
_F='name'
_E='service'
_D='res'
_C=True
_B=False
_A=None
import os,gc,re,json,time,websocket,cloudpickle,base64,getpass,platform,asyncio
from pathlib import Path
from pprint import pprint
from jupyter_client import KernelManager
from IPython.display import display,Javascript
from IPython.core.magics.namespace import NamespaceMagics
from nbconvert.filters import strip_ansi
from django.conf import settings as conf_settings
from spartaqube_app.path_mapper_obf import sparta_ab2d4b6ec5
from project.sparta_76336d2b79.qube_4b40d1a432 import timeout
from project.sparta_3bc15131c6.sparta_0d2990c769.qube_48c282f85d import convert_to_dataframe,sparta_b0cac1454c
from project.sparta_3bc15131c6.sparta_0d2990c769.qube_886837873c import sparta_235d77fd71
from project.logger_config import logger
B_DEBUG=_B
SEND_INTERVAL=.8
def sparta_f6b51512b7():return conf_settings.DEFAULT_TIMEOUT
def sparta_1536687b5e(file_path=_A,text=_A):
	A=file_path
	if text is _A:return
	if A is _A:A='C:\\Users\\benme\\Desktop\\LOG_DEBUG.txt'
	try:
		B='a'if os.path.exists(A)and os.path.getsize(A)>0 else'w'
		with open(A,B,encoding='utf-8')as C:
			if B=='a':C.write(_M)
			C.write(text)
		logger.debug(f"Successfully wrote/appended to {A}")
	except Exception as D:logger.debug(f"Error writing to file: {D}")
class KernelException(Exception):
	def __init__(B,message):
		A=message;super().__init__(A)
		if B_DEBUG:logger.debug('KernelException message');logger.debug(A)
		B.traceback_msg=A
	def get_traceback_errors(A):return A.traceback_msg
class IPythonKernel:
	def __init__(A,api_key=_A,django_settings_module=_A,project_folder=_A):A.api_key=api_key;A.workspaceVarNameArr=[];A.django_settings_module=django_settings_module;A.project_folder=project_folder;A.output_queue=[];A.last_send_time=time.time();A.kernel_manager=KernelManager();A.zmq_identity=_A;A.zmq_request_dict=dict()
	async def initialize(A):await A.startup_kernel()
	async def startup_kernel(A):
		if A.django_settings_module is not _A:B=os.environ.copy();B['DJANGO_ALLOW_ASYNC_UNSAFE']='true';A.kernel_manager.start_kernel(env=B)
		else:A.kernel_manager.start_kernel()
		A.kernel_client=A.kernel_manager.client();A.kernel_client.start_channels()
		try:A.kernel_client.wait_for_ready();C=time.time();logger.debug('Ready, initialize with Django');await A.initialize_kernel();logger.debug('--- %s seconds ---'%(time.time()-C))
		except Exception as D:logger.debug('Exception runtime now');A.kernel_client.stop_channels();A.kernel_manager.shutdown_kernel()
	def set_zmq_identity(A,zmq_identity):A.zmq_identity=zmq_identity;A.output_queue=[];A.last_send_time=time.time()
	def set_zmq_request(A,zmq_request_dict):A.zmq_request_dict=zmq_request_dict
	async def send_sync(A,websocket,data,is_terminated=_B):
		B=is_terminated;A.output_queue.append(data)
		if time.time()-A.last_send_time>=SEND_INTERVAL or B:
			if B_DEBUG:logger.debug(f"Send batch now Interval diff: {time.time()-A.last_send_time}")
			await A.send_batch(websocket,is_terminated=B)
	async def send_batch(A,websocket,is_terminated=_B):
		F='zmq.asyncio.Socket';B=websocket;C=f"{B.__class__.__module__}.{B.__class__.__name__}"
		if len(A.output_queue)>0:
			if B is not _A:
				D={_D:1,_U:is_terminated,_E:_J,'batch_output':json.dumps(A.output_queue)}
				if C==F:await B.send_multipart([A.zmq_identity,json.dumps(D).encode()])
				else:B.send(json.dumps(D))
				A.output_queue=[];A.last_send_time=time.time()
		else:
			E={_D:1,_U:_C,'method':'send_batch',_E:'break-loop','service-req':A.zmq_request_dict.get(_E,'-1')}
			if B is not _A:
				if C==F:await B.send_multipart([A.zmq_identity,json.dumps(E).encode()])
				else:B.send(json.dumps(E))
				A.output_queue=[];A.last_send_time=time.time()
	def get_kernel_manager(A):return A.kernel_manager
	def get_kernel_client(A):return A.kernel_client
	async def initialize_kernel(B):
		A='import os, sys\n';A+='import django\n';A+='os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"\n'
		if B.project_folder is not _A:C=f'user_app_db_path = r"{os.path.join(B.project_folder,"app","db.sqlite3")}"\n';C+='from django.conf import settings\n';C+='user_app_name = "notebook_app"\n';C+='settings.DATABASES[user_app_name] = {"ENGINE": "django.db.backends.sqlite3", "NAME": user_app_db_path}\n';A+=C
		A+='django.setup()\n';D=sparta_ab2d4b6ec5()['project'];E=sparta_ab2d4b6ec5()['project/core/api'];A+=f'sys.path.insert(0, r"{str(D)}")\n';A+=f'sys.path.insert(0, r"{str(E)}")\n';A+=f'os.environ["api_key"] = "{B.api_key}"\n'
		if B.project_folder is not _A:A+=f'os.chdir(r"{B.project_folder}")\n'
		logger.debug('ini_code');logger.debug(A);await B.execute(A,b_debug=_B);await B.backup_venv_at_startup()
	async def backup_venv_at_startup(A):B=f'import sys, os, json\nos.environ["PATH_BK"] = os.environ["PATH"]\nos.environ["VIRTUAL_ENV_BK"] = os.environ["VIRTUAL_ENV"]\nos.environ["SYS_PATH_BK"] = json.dumps(sys.path)\n';await A.execute(B)
	async def activate_venv(C,venv_name):
		def D():B=sparta_235d77fd71();A=os.path.join(B,'sq_venv');A=os.path.normpath(A);os.makedirs(A,exist_ok=_C);return A
		def A():return os.path.normpath(os.path.join(D(),venv_name))
		def E():
			if os.name=='nt':B=os.path.join(A(),'Scripts')
			else:B=os.path.join(A(),'bin')
			return os.path.normpath(B)
		def F():
			C='site-packages'
			if os.name=='nt':B=os.path.join(A(),'Lib',C)
			else:D=f"python{sys.version_info.major}.{sys.version_info.minor}";B=os.path.join(A(),'lib',D,C)
			return os.path.normpath(B)
		G=f'import sys, os\nos.environ["PATH"] = os.environ["PATH_BK"]\nos.environ["VIRTUAL_ENV"] = os.environ["VIRTUAL_ENV_BK"]\n';H=f'os.environ["PATH"] = r"{E()};" + os.environ["PATH"] \nsite_packages_path = r"{F()}"\nsys.path = [elem for elem in sys.path if "site-packages" not in elem] \nsys.path.insert(0, site_packages_path)\n';B=G+H;logger.debug('+'*100);logger.debug('cmd_to_execute activate VENV');logger.debug(B);logger.debug('+'*100);await C.execute(B)
	async def deactivate_venv(A):B=f'import sys, os, json\nos.environ["PATH"] = os.environ["PATH_BK"]\nos.environ["VIRTUAL_ENV"] = os.environ["VIRTUAL_ENV_BK"]\nsys.path = json.loads(os.environ["SYS_PATH_BK"])\n';await A.execute(B)
	def stop_kernel(A):A.kernel_client.stop_channels();A.kernel_manager.interrupt_kernel();A.kernel_manager.shutdown_kernel(now=_C)
	async def cd_to_notebook_folder(C,notebook_path,websocket=_A):B=notebook_path;A=f"import os, sys\n";A+=f"os.chdir('{B}')\n";A+=f"sys.path.insert(0, '{B}')";await C.execute(A,websocket)
	def escape_ansi(C,line):A=re.compile('\\x1B(?:[@-Z\\\\-_]|\\[[0-?]*[ -/]*[@-~])');A=re.compile('(?:\\x1B[@-_]|[\\x80-\\x9F])[0-?]*[ -/]*[@-~]');A=re.compile('(\\x9B|\\x1B\\[)[0-?]*[ -/]*[@-~]');B='\\x1b((\\[\\??\\d+[hl])|([=<>a-kzNM78])|([\\(\\)][a-b0-2])|(\\[\\d{0,2}[ma-dgkjqi])|(\\[\\d+;\\d+[hfy]?)|(\\[;?[hf])|(#[3-68])|([01356]n)|(O[mlnp-z]?)|(/Z)|(\\d+)|(\\[\\?\\d;\\d0c)|(\\d;\\dR))';A=re.compile(B,flags=re.IGNORECASE);return A.sub('',line)
	async def execute(B,cmd,websocket=_A,cell_id=_A,b_debug=_B):
		I=b_debug;F=cell_id;E=websocket;B.last_send_time=time.time();O=B.kernel_client.execute(cmd);J=_O;C=_A;G=_B
		while J!=_P and B.kernel_client.is_alive():
			try:
				K=B.kernel_client.get_iopub_msg()
				if not _G in K:continue
				A=K[_G]
				if B_DEBUG or I:logger.debug(_R);logger.debug(type(A));logger.debug(A);logger.debug(A.keys());logger.debug(_R)
				if _S in A:
					if B_DEBUG or I:logger.debug(_W);logger.debug(A)
					M=re.compile(_X);L=[re.sub(M,_Y,strip_ansi(A))for A in A[_S]];C=KernelException(_M.join(L))
					if E is not _A:D=json.dumps({_D:-1,_K:F,_E:_J,_T:_M.join(L),'errorMsgRaw':A});await B.send_sync(E,D,is_terminated=_C);G=_C
				if _F in A:
					if A[_F]==_V:C=A[_Q];H=B.format_output(C);D=json.dumps({_D:1,_E:_J,_H:H,_K:F});await B.send_sync(E,D)
					if A[_F]==_Z:C=A[_Q];D=json.dumps({_D:-1,_K:F,_E:_J,_T:C});await B.send_sync(E,D,is_terminated=_B)
				if _L in A:C=A[_L];H=B.format_output(C);D=json.dumps({_D:1,_E:_J,_H:H,_K:F});await B.send_sync(E,D)
				if _I in A:J=A[_I]
			except Exception as N:logger.debug('Execute exception EXECUTION');logger.debug(N);G=_C
		if not G:await B.send_batch(E,is_terminated=_C)
		return C
	async def execute_shell(B,cmd,websocket=_A,cell_id=_A,b_debug=_B):
		Q='Custom signal term detected. Breaking loop name.';K=b_debug;J='custom_sig_term';G=cmd;F=cell_id;E=websocket;G=f'{G} && echo "custom_sig_term"';B.last_send_time=time.time();U=B.kernel_client.execute(G);H=_O;C=_A;L=_B;M=_A;R=2;N=_B
		while B.kernel_client.is_alive():
			if L:
				if time.time()-M>R:break
			try:
				O=B.kernel_client.get_iopub_msg(timeout=2)
				if not _G in O:continue
				A=O[_G]
				if B_DEBUG or K:logger.debug(_R);logger.debug(type(A));logger.debug(A);logger.debug(A.keys());logger.debug(_R)
				if _S in A:
					if B_DEBUG or K:logger.debug(_W);logger.debug(A)
					S=re.compile(_X);P=[re.sub(S,_Y,strip_ansi(A))for A in A[_S]];C=KernelException(_M.join(P))
					if E is not _A:D=json.dumps({_D:-1,_K:F,_E:_J,_T:_M.join(P)});await B.send_sync(E,D,is_terminated=_C);N=_C
				if _F in A:
					if A[_F]==_V:
						C=A[_Q]
						if J in C:logger.debug(Q);break
						I=B.format_output(C);D=json.dumps({_D:1,_E:_J,_H:I,_K:F});await B.send_sync(E,D)
					if A[_F]==_Z:
						C=A[_Q]
						if J in C:logger.debug(Q);break
						D=json.dumps({_D:-1,_K:F,_E:_J,_T:C});await B.send_sync(E,D,is_terminated=_B)
				if _L in A:
					C=A[_L]
					if J in str(C):logger.debug('Custom signal term detected. Breaking loop data.');break
					I=B.format_output(C);D=json.dumps({_D:1,_E:_J,_H:I,_K:F});await B.send_sync(E,D)
				if _I in A:
					H=A[_I];logger.debug(f"STATE STATE STATE {H}")
					if H==_P:L=_C;M=time.time()
			except Exception as T:logger.debug('Execute exception shell EXECUTION');logger.debug(T)
		if not N:await B.send_batch(E,is_terminated=_C)
		return C
	async def list_workspace_variables(C):
		N='df_columns';M='is_df';L='preview'
		def O(data,trunc_size):B=trunc_size;A=data;A=A[:B]+'...'if len(A)>B else A;return A
		P='%whos';U=C.kernel_client.execute(P);H=_O;A=[]
		while H!=_P and C.kernel_client.is_alive():
			try:
				I=C.kernel_client.get_iopub_msg()
				if not _G in I:continue
				D=I[_G]
				if _F in D:
					if D[_F]==_V:A.append(D[_Q])
				if _I in D:H=D[_I]
			except Exception as F:logger.debug(F);pass
		G=await C.get_kernel_variables_memory_dict()
		if G is _A:G=dict()
		try:
			A=''.join(A).split(_M);A=A[2:-1];J=[]
			for Q in A:
				E=re.split('\\s{2,}',Q.strip())
				if len(E)>=2:K=E[0];R=E[1];S=' '.join(E[2:])if len(E)>2 else'';J.append({_F:K,_N:R,L:S,'size':G.get(K,0)})
			A=J
			for B in A:
				B['preview_display']=O(B[L],30);B[M]=_B;B[N]=json.dumps([])
				if B[_N]=='DataFrame':
					try:T=convert_to_dataframe(await C._method_get_workspace_variable(B[_F]),B[_F]);B[N]=json.dumps(list(T.columns));B[M]=_C
					except:pass
		except Exception as F:logger.debug('Except list workspace var');logger.debug(F)
		return A
	async def get_kernel_variables_memory_dict(A):B='size_in_bytes_variables_dict';C='\nimport os, sys\ndef get_size_bytes_variables_dict():\n    # Exclude the function itself and common IPython artifacts\n    excluded_vars = {"get_size_mb", "_", "__builtins__", "__file__", "__name__", "__doc__"}\n    all_vars = {k: v for k, v in globals().items() if k not in excluded_vars and not callable(v) and not k.startswith("__")}\n    \n    variables_mem_dict = dict()\n    for var_name, obj in all_vars.items():\n        variables_mem_dict[var_name] = sys.getsizeof(obj)\n    \n    return variables_mem_dict\nsize_in_bytes_variables_dict = get_size_bytes_variables_dict()    \n';await A.execute(C,b_debug=_B);D=await A._method_get_workspace_variable(B);await A.remove_variable_from_kernel(B);return D
	async def get_kernel_memory_size(A):B='size_in_bytes';C='\ndef get_size_bytes():\n    # Exclude the function itself and common IPython artifacts\n    excluded_vars = {"get_size_mb", "_", "__builtins__", "__file__", "__name__", "__doc__"}\n    all_vars = {k: v for k, v in globals().items() if k not in excluded_vars and not callable(v) and not k.startswith("__")}\n    \n    size_in_bytes = 0\n    for var_name, obj in all_vars.items():\n        size_in_bytes += sys.getsizeof(obj)\n    \n    return size_in_bytes\nsize_in_bytes = get_size_bytes()    \n';await A.execute(C,b_debug=_B);D=await A._method_get_workspace_variable(B);await A.remove_variable_from_kernel(B);return D
	def _method_get_kernel_variable_repr(A,kernel_variable):
		F=f"{kernel_variable}";J=A.kernel_client.execute(F);C=_O;D=json.dumps({_D:-1,_U:_C})
		while C!=_P and A.kernel_client.is_alive():
			try:
				E=A.kernel_client.get_iopub_msg()
				if not _G in E:continue
				B=E[_G]
				if _L in B:G=B[_L];H=A.format_output(G);D=json.dumps({_D:1,_H:H})
				if _I in B:C=B[_I]
			except Exception as I:logger.debug('Exception get_kernel_variable_repr');logger.debug(I);pass
		return D
	def format_output(E,output):
		D='image/png';C='text/html';B='text/plain';A=output
		if isinstance(A,dict):
			if C in A:return{_H:A[C],_N:C}
			if D in A:return{_H:A[D],_N:D}
			if B in A:return{_H:A[B],_N:B}
		return{_H:A,_N:B}
	async def _method_get_workspace_variable(A,kernel_variable):
		D=_A
		try:
			G=f"import cloudpickle\nimport base64\ntmp_sq_ans = _\nbase64.b64encode(cloudpickle.dumps({kernel_variable})).decode()";J=A.kernel_client.execute(G);E=_O
			while E!=_P and A.kernel_client.is_alive():
				try:
					F=A.kernel_client.get_iopub_msg()
					if not _G in F:continue
					B=F[_G]
					if _L in B:H=B[_L];I=A.format_output(H);D=cloudpickle.loads(base64.b64decode(I[_H]))
					if _I in B:E=B[_I]
				except Exception as C:logger.debug(C);pass
		except Exception as C:logger.debug('Exception _method_get_workspace_variable');logger.debug(C)
		await A.execute(f"del tmp_sq_ans");await A.execute(f"del cloudpickle");await A.execute(f"del base64");return D
	async def set_workspace_variables(A,variables_dict,websocket=_A):
		for(B,C)in variables_dict.items():await A._method_set_workspace_variable(B,C,websocket=websocket)
	async def _method_set_workspace_variable(A,name,value,websocket=_A):
		try:B=f'import cloudpickle\nimport base64\n{name} = cloudpickle.loads(base64.b64decode("{base64.b64encode(cloudpickle.dumps(value)).decode()}"))';await A.execute(B,websocket)
		except Exception as C:logger.debug('Exception setWorkspaceVariable');logger.debug(C)
		await A.execute(f"del cloudpickle");await A.execute(f"del base64")
	async def reset_kernel_workspace(A):B='%reset -f';await A.execute(B)
	async def remove_variable_from_kernel(A,kernel_variable):
		try:B="del globals()['"+str(kernel_variable)+"']";await A.execute(B)
		except:pass
	async def cloudpickle_kernel_variables(A):C='kernel_cpkl_unpicklable';B='kernel_cpkl_picklable';await A.execute('import cloudpickle');await A.execute('\nimport io\nimport cloudpickle\ndef test_picklability():\n    variables = {k: v for k, v in globals().items() if not k.startswith(\'_\')}\n    picklable = {}\n    unpicklable = {}\n    var_not_to_pickle = [\'In\', \'Out\', \'test_picklability\', \'get_ipython\']\n    var_type_not_to_pickle = [\'ZMQExitAutocall\']\n    \n    for var_name, var_value in variables.items():\n        var_type = type(var_value)\n        if var_name in var_not_to_pickle:\n            continue\n        if var_type.__name__ in var_type_not_to_pickle:\n            continue\n        try:\n            # Attempt to serialize the variable\n            buffer = io.BytesIO()\n            cloudpickle.dump(var_value, buffer)\n            picklable[var_name] = buffer.getvalue()\n        except Exception as e:\n            unpicklable[var_name] = {\n                "type_name": var_type.__name__,\n                "module": var_type.__module__,\n                "repr": repr(var_value),\n                "error": str(e),\n            }\n    \n    return picklable, unpicklable\n\nkernel_cpkl_picklable, kernel_cpkl_unpicklable = test_picklability()\ndel test_picklability\n');D=await A._method_get_workspace_variable(B);E=await A._method_get_workspace_variable(C);await A.remove_variable_from_kernel(B);await A.remove_variable_from_kernel(C);return D,E
	async def execute_code(A,cmd,websocket=_A,cell_id=_A,bTimeout=_B):
		C=cell_id;B=websocket
		if bTimeout:return await A.execute_code_timeout(cmd,websocket=B,cell_id=C)
		else:return await A.execute_code_no_timeout(cmd,websocket=B,cell_id=C)
	@timeout(sparta_f6b51512b7())
	async def execute_code_timeout(self,cmd,websocket=_A,cell_id=_A):return await self.execute(cmd,websocket=websocket,cell_id=cell_id)
	async def execute_code_no_timeout(A,cmd,websocket=_A,cell_id=_A):return await A.execute(cmd,websocket=websocket,cell_id=cell_id)
	async def getLastExecutedVariable(A,websocket):
		try:B=f"import cloudpickle\nimport base64\ntmp_sq_ans = _\nbase64.b64encode(cloudpickle.dumps(tmp_sq_ans)).decode()";return cloudpickle.loads(base64.b64decode(A.format_output(await A.execute(B,websocket))))
		except Exception as C:logger.debug('Excep last exec val');raise C
	async def _method_get_kernel_variable(A,nameVar):
		try:B=f"import cloudpickle\nimport base64\ntmp_sq_ans = _\nbase64.b64encode(cloudpickle.dumps({nameVar})).decode()";return cloudpickle.loads(base64.b64decode(A.format_output(await A.execute(B))))
		except Exception as C:logger.debug('Exception get_kernel_variable');logger.debug(C);return
	async def removeWorkspaceVariable(A,name):
		try:del A.workspaceVarNameArr[name]
		except Exception as B:logger.debug('Exception removeWorkspaceVariable');logger.debug(B)
	def getWorkspaceVariables(A):return[]