_H='connector_id'
_G='Invalid chart type. Use an ID found in the DataFrame get_plot_types()'
_F='data'
_E='100%'
_D='api_service'
_C=True
_B='widget_id'
_A=None
import os,json,uuid,pandas as pd,urllib.parse
from IPython.core.display import display,HTML
import warnings
warnings.filterwarnings('ignore',message='Consider using IPython.display.IFrame instead',category=UserWarning)
from datetime import datetime,timedelta
import pytz
UTC=pytz.utc
from project.models import UserProfile,PlotDBChart,PlotDBChartShared,PlotDBPermission
from project.sparta_6d49f7e4f5.sparta_dac0a6d98d.qube_b950b30269 import sparta_a94b699e48
from project.sparta_6d49f7e4f5.sparta_bb74460757.qube_795f848f90 import convert_to_dataframe,convert_dataframe_to_json
from project.sparta_6d49f7e4f5.sparta_bb74460757.qube_74042b161e import sparta_9bd4d72961
class Spartaqube:
	_instance=_A
	def __new__(A,*B,**C):
		if A._instance is _A:A._instance=super().__new__(A);A._instance._initialized=False
		return A._instance
	def __init__(A,api_token_id=_A):
		B=api_token_id
		if A._initialized:return
		A._initialized=_C
		if B is _A:
			try:B=os.environ['api_key']
			except:pass
		A.api_token_id=B;A.user_obj=UserProfile.objects.get(api_key=B).user
	def test(A):print('test')
	def get_widget_data(A,widget_id):B={_D:'get_widget_data',_B:widget_id};return sparta_a94b699e48(B,A.user_obj)
	def sparta_4ed82e58f9(A,widget_id):B={_D:'has_widget_id',_B:widget_id};return sparta_a94b699e48(B,A.user_obj)
	def get_widget(C,widget_id,width=_E,height=500):
		A=PlotDBChartShared.objects.filter(is_delete=0,user=C.user_obj,plot_db_chart__is_delete=0,plot_db_chart__plot_chart_id=widget_id)
		if A.count()>0:B=str(uuid.uuid4());D=datetime.now().astimezone(UTC);PlotDBPermission.objects.create(plot_db_chart=A[0].plot_db_chart,token=B,date_created=D);return HTML(f'<iframe src="/plot-widget-token/{B}" width="{width}" height="{height}" frameborder="0" allow="clipboard-write"></iframe>')
		return'You do not have the rights to access this object'
	def iplot(I,*B,width=_E,height=550):
		if len(B)==0:raise Exception('You must pass at least one input variable to plot')
		else:
			C=dict()
			for(E,D)in enumerate(B):
				if D is _A:continue
				F=convert_to_dataframe(D);C[E]=convert_dataframe_to_json(F)
			G=json.dumps(C);A=str(uuid.uuid4());H=f'''
                <form id="dataForm_{A}" action="plot-gui" method="POST" target="{A}">
                    <input type="hidden" name="data" value=\'{G}\' />
                </form>
                <iframe 
                    id="{A}"
                    name="{A}"
                    width="{width}" 
                    height="{height}" 
                    frameborder="0" 
                    allow="clipboard-write"></iframe>

                <script>
                    // Submit the form automatically to send data to the iframe
                    document.getElementById(\'dataForm_{A}\').submit();
                </script>
                ''';return HTML(H)
	def plot(V,*W,**A):
		I='width';H='chart_type';D=dict()
		for(J,F)in A.items():
			if F is _A:continue
			K=convert_to_dataframe(F);D[J]=convert_dataframe_to_json(K)
		E=_A
		if H not in A:
			if _B not in A:raise Exception("Missing chart_type parameter. For instance: chart_type='line'")
			else:E=0
		if E is _A:
			L=sparta_9bd4d72961(b_return_type_id=_C)
			try:M=json.loads(D[H])[_F][0][0];E=[A for A in L if A['ID']==M][0]['type_plot']
			except:raise Exception(_G)
		N=A.get(I,_E);O=A.get(I,'500');P=A.get('interactive',_C);G=A.get(_B,_A);Q={'interactive_api':1 if P else 0,'is_api_template':1 if G is not _A else 0,_B:G};R=json.dumps(Q);S=urllib.parse.quote(R);B=dict();B['res']=1;B['notebook_variables']=D;B['type_chart']=E;B['override_options']=D.get('options',dict());T=json.dumps(B);C=str(uuid.uuid4());U=f'''
            <form id="dataForm_{C}" action="plot-api/{S}" method="POST" target="{C}">
                <input type="hidden" name="data" value=\'{T}\' />
            </form>
            <iframe 
                id="{C}"
                name="{C}"
                width="{N}" 
                height="{O}" 
                frameborder="0" 
                allow="clipboard-write"></iframe>

            <script>
                // Submit the form automatically to send data to the iframe
                document.getElementById(\'dataForm_{C}\').submit();
            </script>
            ''';return HTML(U)
	def plot_documentation(B,chart_type='line'):
		A=chart_type;C=B.get_plot_types()
		if len([B for B in C if B['ID']==A])>0:D=f"api#plot-{A}";return D
		else:raise Exception(_G)
	def plot_template(B,*C,**A):
		if _B in A:return B.plot(*C,**A)
		raise Exception('Missing widget_id')
	def get_connector_tables(A,connector_id):B={_D:'get_connector_tables',_H:connector_id};return sparta_a94b699e48(B,A.user_obj)
	def get_data_from_connector(I,connector_id,table=_A,sql_query=_A,output_format=_A,dynamic_inputs=_A):
		G=dynamic_inputs;F=output_format;E=sql_query;A={_D:'get_data_from_connector'};A[_H]=connector_id;A['table_name']=table;A['query_filter']=E;A['bApplyFilter']=1 if E is not _A else 0;H=[]
		if G is not _A:
			for(J,K)in G.items():H.append({'input':J,'default':K})
		A['dynamic_inputs']=H;B=sparta_a94b699e48(A,I.user_obj);C=False
		if F is _A:C=_C
		elif F=='DataFrame':C=_C
		if C:
			if B['res']==1:D=json.loads(B[_F])
			return pd.DataFrame(D[_F],index=D['index'],columns=D['columns'])
		return B
	def apply_method(B,method_name,*D,**C):A=C;A[_D]=method_name;return sparta_a94b699e48(A,B.user_obj)
	def __getattr__(A,name):return lambda*B,**C:A.apply_method(name,*B,**C)