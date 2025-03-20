_H='execution_count'
_G='cell_type'
_F='code'
_E='outputs'
_D='source'
_C='cells'
_B='sqMetadata'
_A='metadata'
import os,re,uuid,json
from datetime import datetime
from nbconvert.filters import strip_ansi
from project.sparta_6d49f7e4f5.sparta_5fe6b9feb3 import qube_9f221e9d36 as qube_9f221e9d36
from project.sparta_6d49f7e4f5.sparta_bb74460757.qube_795f848f90 import sparta_cfece85c36,sparta_660353d55e
from project.logger_config import logger
def sparta_cd17faec86(file_path):return os.path.isfile(file_path)
def sparta_5566bf32d2():return qube_9f221e9d36.sparta_980d9e2d88(json.dumps({'date':str(datetime.now())}))
def sparta_ad97ab689b():B='python';A='name';C={'kernelspec':{'display_name':'Python 3 (ipykernel)','language':B,A:'python3'},'language_info':{'codemirror_mode':{A:'ipython','version':3},'file_extension':'.py','mimetype':'text/x-python',A:B,'nbconvert_exporter':B,'pygments_lexer':'ipython3'},_B:sparta_5566bf32d2()};return C
def sparta_54968fc7ae():return{_G:_F,_D:[''],_A:{},_H:None,_E:[]}
def sparta_b88ca308da():return[sparta_54968fc7ae()]
def sparta_677b1606b2():return{'nbformat':4,'nbformat_minor':0,_A:sparta_ad97ab689b(),_C:[]}
def sparta_e1c349b9a0(first_cell_code=''):A=sparta_677b1606b2();B=sparta_54968fc7ae();B[_D]=[first_cell_code];A[_C]=[B];return A
def sparta_1a2993aa62(full_path):
	A=full_path
	if sparta_cd17faec86(A):return sparta_581d2a6100(A)
	else:return sparta_e1c349b9a0()
def sparta_581d2a6100(full_path):return sparta_e7ab93e572(full_path)
def sparta_aefb43f579():A=sparta_677b1606b2();B=json.loads(qube_9f221e9d36.sparta_01a0cc1a29(A[_A][_B]));A[_A][_B]=B;return A
def sparta_e7ab93e572(full_path):
	with open(full_path)as C:B=C.read()
	if len(B)==0:A=sparta_677b1606b2()
	else:A=json.loads(B)
	A=sparta_179fd7ae3a(A);return A
def sparta_179fd7ae3a(ipynb_dict):
	A=ipynb_dict;C=list(A.keys())
	if _C in C:
		D=A[_C]
		for B in D:
			if _A in list(B.keys()):
				if _B in B[_A]:B[_A][_B]=qube_9f221e9d36.sparta_01a0cc1a29(B[_A][_B])
	try:A[_A][_B]=json.loads(qube_9f221e9d36.sparta_01a0cc1a29(A[_A][_B]))
	except:A[_A][_B]=json.loads(qube_9f221e9d36.sparta_01a0cc1a29(sparta_5566bf32d2()))
	return A
def sparta_deafe1d3a3(full_path):
	B=full_path;A=dict()
	with open(B)as C:A=C.read()
	if len(A)==0:A=sparta_aefb43f579();A[_A][_B]=json.dumps(A[_A][_B])
	else:
		A=json.loads(A)
		if _A in list(A.keys()):
			if _B in list(A[_A].keys()):A=sparta_179fd7ae3a(A);A[_A][_B]=json.dumps(A[_A][_B])
	A['fullPath']=B;return A
def save_ipnyb_from_notebook_cells(notebook_cells_arr,full_path,dashboard_id='-1'):
	R='output_type';Q='markdown';L=full_path;K='tmp_idx';B=[]
	for A in notebook_cells_arr:
		A['bIsComputing']=False;S=A['bDelete'];F=A['cellType'];M=A[_F];T=A['positionIndex'];A[_D]=[M];G=A.get('ipynbOutput',[]);C=A.get('ipynbError',[]);logger.debug('ipynb_output_list');logger.debug(G);logger.debug(type(G));logger.debug('ipynb_error_list');logger.debug(C);logger.debug(type(C));logger.debug('this_cell_dict');logger.debug(A)
		if int(S)==0:
			if F==0:H=_F
			elif F==1:H=Q
			elif F==2:H=Q
			elif F==3:H='raw'
			D={_A:{_B:qube_9f221e9d36.sparta_980d9e2d88(json.dumps(A))},'id':uuid.uuid4().hex[:8],_G:H,_D:[M],_H:None,K:T,_E:[]}
			if len(G)>0:
				N=[]
				for E in G:O={};O[E['type']]=[E['output']];N.append({'data':O,R:'execute_result'})
				D[_E]=N
			elif len(C)>0:
				D[_E]=C
				try:
					J=[];U=re.compile('<ipython-input-\\d+-[0-9a-f]+>')
					for E in C:E[R]='error';J+=[re.sub(U,'<IPY-INPUT>',strip_ansi(A))for A in E['traceback']]
					if len(J)>0:D['tbErrors']='\n'.join(J)
				except Exception as V:logger.debug('Except prepare error output traceback with msg:');logger.debug(V)
			else:D[_E]=[]
			B.append(D)
	B=sorted(B,key=lambda d:d[K]);[A.pop(K,None)for A in B];I=sparta_1a2993aa62(L);P=I[_A][_B];P['identifier']={'dashboardId':dashboard_id};I[_A][_B]=qube_9f221e9d36.sparta_980d9e2d88(json.dumps(P));I[_C]=B
	with open(L,'w')as W:json.dump(I,W,indent=4)
	return{'res':1}
def sparta_6860f183c1(full_path):
	A=full_path;A=sparta_cfece85c36(A);C=dict()
	with open(A)as D:E=D.read();C=json.loads(E)
	F=C[_C];B=[]
	for G in F:B.append({_F:G[_D][0]})
	logger.debug('notebook_cells_list');logger.debug(B);return B