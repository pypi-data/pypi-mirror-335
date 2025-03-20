_D='execute_code'
_C='backend'
_B=None
_A='service'
import os,sys,json,base64,cloudpickle,importlib,traceback,asyncio,subprocess,platform
from django.conf import settings
from pathlib import Path
from channels.generic.websocket import AsyncWebsocketConsumer
from spartaqube_app.path_mapper_obf import sparta_ab2d4b6ec5
from project.sparta_3bc15131c6.sparta_0d2990c769.qube_48c282f85d import sparta_b0cac1454c
from project.sparta_3bc15131c6.sparta_e0bb3dc4e4.qube_4031ea9712 import SenderKernel
from project.sparta_3bc15131c6.sparta_ef73db400d.qube_a300615bb6 import sparta_5d910cb206,sparta_00fc6ac630
from project.logger_config import logger
class OutputRedirector:
	def __init__(A,websocket):A.websocket=websocket;A.original_stdout=sys.stdout;A.original_stderr=sys.stderr
	def __enter__(A):
		class B:
			def __init__(A,websocket):A.websocket=websocket
			def write(A,message):
				if A.websocket:
					try:A.websocket.send(json.dumps({'res':1000,'msg':message}))
					except Exception as B:logger.debug(f"WebSocket send error: {B}")
		A.custom_stream=B(A.websocket);sys.stdout=A.custom_stream;sys.stderr=A.custom_stream
	def __exit__(A,exc_type,exc_val,exc_tb):sys.stdout=A.original_stdout;sys.stderr=A.original_stderr
class ApiWebserviceWS(AsyncWebsocketConsumer):
	async def prepare_sender_kernel(A,kernel_manager_uuid):
		from project.models import KernelProcess as C;B=C.objects.filter(kernel_manager_uuid=kernel_manager_uuid)
		if await B.acount()>0:
			D=await B.afirst();E=D.port
			if A.sender_kernel_obj is _B:A.sender_kernel_obj=SenderKernel(A)
			A.sender_kernel_obj.zmq_connect()
	async def connect(A):await A.accept();A.user=A.scope['user'];A.sender_kernel_obj=_B
	async def disconnect(A,close_code=_B):
		logger.debug('Disconnect')
		try:await A.close()
		except:pass
	async def init_kernel_import_models(B,user_project_path):C=os.path.join(os.path.dirname(user_project_path),_C);A=os.path.join(C,'app');D=f'''
%load_ext autoreload
%autoreload 2    
import os, sys
import django
# Set the Django settings module
os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"
sys.path.insert(0, r"{A}")
os.chdir(r"{A}")
os.environ[\'DJANGO_SETTINGS_MODULE\'] = \'app.settings\'
# Initialize Django
django.setup()
''';await B.sender_kernel_obj.send_zmq_request({_A:_D,'cmd':D})
	async def init_kernel(A,kernel_manager_uuid,user_project_path):await A.prepare_sender_kernel(kernel_manager_uuid);await A.init_kernel_import_models(user_project_path)
	async def receive(A,text_data):
		G=False;E=text_data
		if len(E)>0:
			B=json.loads(E);H=B['kernelManagerUUID'];O=B.get('isRunMode',G);I=B.get('initOnly',G);F=sparta_b0cac1454c(B['baseProjectPath']);J=os.path.join(os.path.dirname(F),_C);K=B[_A];L=B.copy();await A.init_kernel(H,F)
			if I:await A.send(json.dumps({'res':1}));return
			C='import os, sys, importlib\n';C+=f'sys.path.insert(0, r"{J}")\n';C+=f"import webservices\n";C+=f"importlib.reload(webservices)\n";C+=f"webservice_res_dict = webservices.sparta_e4cbeeea9c(service_name, post_data)\n";M={'service_name':K,'post_data':L};N=base64.b64encode(cloudpickle.dumps(M)).decode('utf-8');await A.sender_kernel_obj.send_zmq_request({_A:'set_workspace_variables','encoded_dict':N});await A.sender_kernel_obj.send_zmq_request({_A:_D,'cmd':C});D=await A.sender_kernel_obj.send_zmq_request({_A:'get_workspace_variable','kernel_variable':'webservice_res_dict'})
			if D is not _B:D['webservice_resolve']=1;await A.send(json.dumps(D))