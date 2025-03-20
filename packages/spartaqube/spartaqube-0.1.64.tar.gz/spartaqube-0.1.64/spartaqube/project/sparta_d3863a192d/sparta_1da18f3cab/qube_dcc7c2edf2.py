import os,json,platform,websocket,threading,time,pandas as pd
from project.sparta_6d49f7e4f5.sparta_eed2ac8b74 import qube_f98e616a62 as qube_f98e616a62
from project.sparta_6d49f7e4f5.sparta_bb74460757.qube_795f848f90 import convert_to_dataframe
from project.sparta_6d49f7e4f5.sparta_d0477f20f9.qube_c8e95923d2 import Connector as Connector
from project.logger_config import logger
IS_WINDOWS=False
if platform.system()=='Windows':IS_WINDOWS=True
from channels.generic.websocket import WebsocketConsumer
from project.sparta_d3863a192d.sparta_3c800a8540 import qube_a8d0eb6c62 as qube_a8d0eb6c62
from project.sparta_6d49f7e4f5.sparta_bb74460757 import qube_795f848f90 as qube_795f848f90
class WssConnectorWS(WebsocketConsumer):
	channel_session=True;http_user_and_session=True
	def connect(A):logger.debug('Connect Now');A.accept();A.user=A.scope['user'];A.json_data_dict=dict()
	def init_socket(B,json_data):
		A=json_data;D=A['is_model_connector'];B.connector_obj=Connector(db_engine='wss')
		if D:
			E=A['connector_id'];C=qube_f98e616a62.sparta_50f51c7fca(E,B.user)
			if C is None:F={'res':-2,'errorMsg':'Invalid connector, please try again'};G=json.dumps(F);B.send(text_data=G);return
			B.connector_obj.init_with_model(C)
		else:B.connector_obj.init_with_params(host=A['host'],port=A['port'],user=A['user'],password=A['password'],database=A['database'],oracle_service_name=A['oracle_service_name'],csv_path=A['csv_path'],csv_delimiter=A['csv_delimiter'],keyspace=A['keyspace'],library_arctic=A['library_arctic'],database_path=A['database_path'],read_only=A['read_only'],json_url=A['json_url'],socket_url=A['socket_url'],redis_db=A['redis_db'],dynamic_inputs=A['dynamic_inputs'],py_code_processing=A['py_code_processing'])
		B.connector_obj.get_db_connector().start_stream(gui_websocket=B)
	def disconnect(A,close_code):
		logger.debug('Disconnect')
		try:A.connector_obj.get_db_connector().stop_threads()
		except:pass
		try:A.close()
		except:pass
	def receive(A,text_data):
		E='service';C=text_data
		if len(C)>0:
			D=json.loads(C);B=D[E]
			if B=='init-socket':A.init_socket(D);F={'res':1,E:B};G=json.dumps(F);A.send(text_data=G)
			if B=='stop-socket':A.connector_obj.get_db_connector().stop_stream(gui_websocket=A)