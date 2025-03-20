import re,json,subprocess
from channels.generic.websocket import WebsocketConsumer
from project.sparta_6d49f7e4f5.sparta_93fbedec69 import qube_44d243048c as qube_44d243048c
from project.logger_config import logger
def sparta_c8367b076a(command):
	A=command
	if not A.startswith('pip install'):return False
	B='^pip install( [a-zA-Z0-9_\\-\\.]+(==|>=|<=|>|<)?[a-zA-Z0-9_\\-\\.]*)+$';return bool(re.match(B,A))
class PipInstallWS(WebsocketConsumer):
	channel_session=True;http_user_and_session=True
	def connect(A):logger.debug('Connect Now');A.accept();A.json_data_dict=dict()
	def disconnect(A,close_code=None):
		logger.debug('Disconnect')
		try:A.close()
		except:pass
	def receive(C,text_data):
		K='line';F=text_data;E='res'
		if len(F)>0:
			G=json.loads(F);H=G['pipInstallCmd'].strip();L=G['env_name'];M=qube_44d243048c.sparta_0c3f61e02d(L);N=H.replace('pip',M)
			if not sparta_c8367b076a(H):A={E:-1,'errorMsg':'Invalid syntax'};B=json.dumps(A);C.send(text_data=B);return
			I=0;J=subprocess.Popen(N,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
			try:
				for D in J.stdout:
					if'Successfully installed'in D or'Requirement already satisfied'in D:I=1
					A={E:2,K:D};B=json.dumps(A);C.send(text_data=B)
			except Exception as O:logger.debug(f"An error occurred: {O}");A={E:-1,K:D};B=json.dumps(A);C.send(text_data=B)
			J.wait()
		A={E:1,'success':I};B=json.dumps(A);C.send(text_data=B)