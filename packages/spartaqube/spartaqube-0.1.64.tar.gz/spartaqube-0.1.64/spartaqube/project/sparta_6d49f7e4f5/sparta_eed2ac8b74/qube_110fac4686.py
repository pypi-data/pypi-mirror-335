_I='output'
_H='yAxisDataArr'
_G='xAxisDataArr'
_F='res'
_E='png'
_D='utf-8'
_C=True
_B=None
_A=False
import json,io,os,base64,pandas as pd,quantstats as qs,matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from io import BytesIO
def sparta_a319e136cb(df):
	A=df
	if pd.api.types.is_datetime64_any_dtype(A.index):
		if A.index.tz is not _B:A.index=A.index.tz_localize(_B)
	return A
def sparta_9dfefcf62a(series):
	A=series
	if(A>=0).all():
		if A.max()>1.:return _A
	return _C
def sparta_77c5e02190(fig):A=io.BytesIO();fig.savefig(A,format=_E);A.seek(0);B=base64.b64encode(A.getvalue()).decode(_D);A.close();return B
def sparta_961a848067(fig):A=BytesIO();fig.savefig(A,format=_E);B=base64.b64encode(A.getvalue()).decode(_D);return B
def sparta_d6312dd30d(json_data,user_obj):
	g='basic';f='Portfolio';e='title';d='benchmark_title';c='strategyTitle';b='riskFreeRate';a='reportType';V='split';U='Benchmark';P='date';N=json_data;A=json.loads(N['opts']);K=int(A[a]);W=json.loads(N[_G])[0];C=json.loads(N[_H]);O=0
	if b in A:O=float(A[b])
	G=U;E='Strategy'
	if c in A:
		Q=A[c]
		if Q is not _B:
			if len(Q)>0:E=Q
	if d in A:
		R=A[d]
		if R is not _B:
			if len(R)>0:G=R
	X='Strategy Tearsheet'
	if e in A:
		Y=A[e]
		if len(Y)>0:X=Y
	H=pd.DataFrame(C[0]);H[P]=pd.to_datetime(W);H.set_index(P,inplace=_C);H.columns=[f];H=sparta_a319e136cb(H);B=H[f]
	if not sparta_9dfefcf62a(B):B=B.pct_change().dropna()
	D=_B
	if len(C)==2:
		I=pd.DataFrame(C[1]);I[P]=pd.to_datetime(W);I.set_index(P,inplace=_C);I.columns=[U];I=sparta_a319e136cb(I);D=I[U]
		if not sparta_9dfefcf62a(D):D=D.pct_change().dropna()
	if'bHtmlReport'in list(N.keys()):
		h=os.path.dirname(os.path.abspath(__file__));S=os.path.join(h,'quantstats/quantstats-tearsheet.html')
		with open(S,mode='a')as i:i.close()
		qs.reports.html(B,benchmark=D,rf=O,mode='full',match_dates=_C,output=S,title=X,strategy_title=E,benchmark_title=G)
		with open(S,'rb')as j:k=j.read()
		return{_F:1,'file_content':k.decode(_D),'b_downloader':_C}
	if K==0:
		def L(data,benchmark=_B):
			C=benchmark;A=[];D=qs.plots.snapshot(data,show=_A,strategy_title=E,benchmark_title=G);A.append(sparta_961a848067(D));B=qs.plots.monthly_heatmap(data,show=_A,ylabel=_A,returns_label=E);A.append(sparta_961a848067(B))
			if C is not _B:B=qs.plots.monthly_heatmap(C,show=_A,ylabel=_A,returns_label=G);A.append(sparta_961a848067(B))
			return A
		if len(C)==1:F=L(B);J=F
		elif len(C)==2:F=L(B,D);J=F
	elif K==1:
		if len(C)==1:Z=qs.reports.metrics(B,rf=O,mode=g,display=_A,strategy_title=E,benchmark_title=G)
		elif len(C)==2:Z=qs.reports.metrics(B,benchmark=D,rf=O,mode=g,display=_A,strategy_title=E,benchmark_title=G)
		J=Z.to_json(orient=V)
	elif K==2:
		def L(data,benchmark=_B):
			D=benchmark;C=data;B=[]
			if A['returns']:F=qs.plots.returns(C,benchmark=D,show=_A,ylabel=_A);B.append(sparta_961a848067(F))
			if A['logReturns']:G=qs.plots.log_returns(C,benchmark=D,show=_A,ylabel=_A);B.append(sparta_961a848067(G))
			if A['yearlyReturns']:H=qs.plots.yearly_returns(C,benchmark=D,show=_A,ylabel=_A);B.append(sparta_961a848067(H))
			if A['dailyReturns']:I=qs.plots.daily_returns(C,benchmark=D,show=_A,ylabel=_A);B.append(sparta_961a848067(I))
			if A['histogram']:J=qs.plots.histogram(C,benchmark=D,show=_A,ylabel=_A);B.append(sparta_961a848067(J))
			if A['rollingVol']:K=qs.plots.rolling_volatility(C,benchmark=D,show=_A,ylabel=_A);B.append(sparta_961a848067(K))
			if A['rollingSharpe']:L=qs.plots.rolling_sharpe(C,benchmark=D,show=_A,ylabel=_A);B.append(sparta_961a848067(L))
			if A['rollingSortino']:M=qs.plots.rolling_sortino(C,benchmark=D,show=_A,ylabel=_A);B.append(sparta_961a848067(M))
			if A['rollingBeta']:
				if D is not _B:N=qs.plots.rolling_beta(C,benchmark=D,show=_A,ylabel=_A);B.append(sparta_961a848067(N))
			if A['distribution']:O=qs.plots.distribution(C,show=_A,ylabel=_A);B.append(sparta_961a848067(O))
			if A['heatmap']:P=qs.plots.monthly_heatmap(C,benchmark=D,show=_A,ylabel=_A);B.append(sparta_961a848067(P))
			if A['drawdowns']:Q=qs.plots.drawdown(C,show=_A,ylabel=_A);B.append(sparta_961a848067(Q))
			if A['drawdownsPeriod']:R=qs.plots.drawdowns_periods(C,show=_A,ylabel=_A,title=E);B.append(sparta_961a848067(R))
			if A['returnQuantiles']:S=qs.plots.distribution(C,show=_A,ylabel=_A);B.append(sparta_961a848067(S))
			return B
		if len(C)==1:F=L(B);J=F
		elif len(C)==2:F=L(B,D);J=F
	elif K==3:l=[E];M=B;M.columns=l;m=qs.reports._calc_dd(M);n=qs.stats.drawdown_details(M).sort_values(by='max drawdown',ascending=_C)[:10];T=[];o=qs.plots.drawdown(M,show=_A,ylabel=_A);T.append(sparta_961a848067(o));p=qs.plots.drawdowns_periods(M,show=_A,ylabel=_A,title=E);T.append(sparta_961a848067(p));J=[m.to_json(orient=V),n.to_json(orient=V),T]
	return{_F:1,a:K,_I:J}
def sparta_d75ca84457():import matplotlib,matplotlib.pyplot as A;from matplotlib.path import Path;from matplotlib.patches import PathPatch;from matplotlib.patches import Patch;import matplotlib.patches as B
def sparta_0651c99216(json_data,user_obj):
	R='alpha';Q='sq_index';P='None';O='data_df';N='column_renamed';C=json_data;sparta_d75ca84457();S=json.loads(C['opts']);D=json.loads(C[_G])[0];E=json.loads(C[_H]);F=json.loads(C['chartParamsEditorDict']);print('MATPLOTIB DEBUGGER BACKJEND SERIVCE');print('x_data_arr');print(D);print(type(D));print('y_data_arr');print(E);print(type(E));print('common_props');print(S);print('chart_params_editor_dict');print(F);A=pd.DataFrame(E).T;A.index=D;H=[]
	try:H=[A[N]for A in F['yAxisArr']];A.columns=H
	except:pass
	I=[]
	try:I=[A[N]for A in F['xAxisArr']]
	except:pass
	print(O);print(A);print('user_input_x_columns');print(I);M='';J=F['typeChart'];print('LA type_chart >> '+str(J))
	if J==101:
		K=plt.figure(figsize=(12,6));B=K.add_subplot(1,1,1)
		for(T,U)in enumerate(list(A.columns)):V=E[T];B.scatter(D,V,label=U)
		B.spines['top'].set_color(P);B.spines['right'].set_color(P);B.set_xlabel('Area');B.set_ylabel('Population');B.set_xlim(-.01);B.legend(loc='upper left',fontsize=10);plt.grid()
	elif J==102:
		import seaborn as W;K,B=plt.subplots(figsize=(10,6));X=list(A.columns);A[Q]=A.index;print(O);print(A)
		for L in H:print(L);W.regplot(x=Q,y=L,data=A,label=L,scatter_kws={R:.7},line_kws={R:.7})
		plt.xlabel(I[0]);plt.ylabel('');plt.legend(title='Category');plt.grid()
	G=BytesIO();plt.savefig(G,format=_E,bbox_inches='tight')
	try:plt.close(K)
	except:pass
	G.seek(0);M=base64.b64encode(G.getvalue()).decode(_D);G.close();return{_F:1,_I:M}