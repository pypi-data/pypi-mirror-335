import json,base64,asyncio,subprocess,uuid,os,requests,pandas as pd
from subprocess import PIPE
from django.db.models import Q
from datetime import datetime,timedelta
import pytz
UTC=pytz.utc
from project.models_spartaqube import DBConnector,DBConnectorUserShared,PlotDBChart,PlotDBChartShared
from project.models import ShareRights
from project.sparta_3bc15131c6.sparta_6156be0aab import qube_c9db55e3c2 as qube_c9db55e3c2
from project.sparta_3bc15131c6.sparta_21301ca379 import qube_85e301a8bd
from project.sparta_3bc15131c6.sparta_1ec16518f2 import qube_e3b4c78a63 as qube_e3b4c78a63
from project.sparta_3bc15131c6.sparta_21301ca379.qube_a2478f1fd1 import Connector as Connector
from project.logger_config import logger
def sparta_ee3135e631(json_data,user_obj):
	D='key';A=json_data;logger.debug('Call autocompelte api');logger.debug(A);B=A[D];E=A['api_func'];C=[]
	if E=='tv_symbols':C=sparta_3eb0c6a2f4(B)
	return{'res':1,'output':C,D:B}
def sparta_3eb0c6a2f4(key_symbol):
	F='</em>';E='<em>';B='symbol_id';G=f"https://symbol-search.tradingview.com/local_search/v3/?text={key_symbol}&hl=1&exchange=&lang=en&search_type=undefined&domain=production&sort_by_country=US";H={'http':os.environ.get('http_proxy',None),'https':os.environ.get('https_proxy',None)};C=requests.get(G,proxies=H)
	try:
		if int(C.status_code)==200:
			I=json.loads(C.text);D=I['symbols']
			for A in D:A[B]=A['symbol'].replace(E,'').replace(F,'');A['title']=A[B];A['subtitle']=A['description'].replace(E,'').replace(F,'');A['value']=A[B]
			return D
		return[]
	except:return[]