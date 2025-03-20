import os,json,base64,subprocess,pandas as pd
from datetime import datetime,timedelta
from dateutil import parser
import pytz
UTC=pytz.utc
from django.db.models import Q
from django.conf import settings as conf_settings
from django.contrib.auth.models import User
from django.contrib.humanize.templatetags.humanize import naturalday
from django.utils.text import Truncator
from django.db.models import CharField,TextField
from django.db.models.functions import Lower
CharField.register_lookup(Lower)
TextField.register_lookup(Lower)
from project.models import User,UserProfile,PlotDBChart,PlotDBChartShared,DashboardShared,Notebook,NotebookShared
from project.sparta_3bc15131c6.sparta_6156be0aab import qube_c9db55e3c2 as qube_c9db55e3c2
from project.sparta_3bc15131c6.sparta_438eb06364 import qube_879159c153 as qube_879159c153
def sparta_7d8d6d46a2(user_obj):
	A=qube_c9db55e3c2.sparta_e2c6ddbe2b(user_obj)
	if len(A)>0:B=[A.user_group for A in A]
	else:B=[]
	return B
def sparta_975f3d2f3c(json_data,user_obj):
	g='notebooks';f='dashboards';e='widgets';d=False;c='plot_chart_id';S=True;R='description_trunc';P='description';O='name_trunc';N='name';C=user_obj;G=json_data['keyword'].lower();D=120;E=sparta_7d8d6d46a2(C)
	if len(E)>0:I=PlotDBChartShared.objects.filter(Q(is_delete=0,user_group__in=E,plot_db_chart__is_delete=0,plot_db_chart__name__lower__icontains=G)|Q(is_delete=0,user=C,plot_db_chart__is_delete=0,plot_db_chart__name__lower__icontains=G))
	else:I=PlotDBChartShared.objects.filter(is_delete=0,user=C,plot_db_chart__is_delete=0,plot_db_chart__name__lower__icontains=G)
	h=I.count();J=[]
	for i in I[:5]:F=i.plot_db_chart;J.append({c:F.plot_chart_id,'type_chart':F.type_chart,N:F.name,O:Truncator(F.name).chars(D),P:F.description,R:Truncator(F.description).chars(D)})
	j=sorted(set([A[c]for A in J]));K=[];T=[];U=0
	if len(E)>0:V=DashboardShared.objects.filter(Q(is_delete=0,user_group__in=E,dashboard__is_delete=0)|Q(is_delete=0,user=C,dashboard__is_delete=0))
	else:V=DashboardShared.objects.filter(is_delete=0,user=C,dashboard__is_delete=0)
	for k in V:
		L=d;A=k.dashboard
		if G in A.name.lower():L=S
		else:
			H=A.plot_db_dependencies
			if H is not None:
				H=json.loads(H)
				for l in H:
					if l in j:L=S;break
		if L:
			if A.dashboard_id not in T:T.append(A.dashboard_id);K.append({'dashboard_id':A.dashboard_id,N:A.name,O:Truncator(A.name).chars(D),P:A.description,R:Truncator(A.description).chars(D)})
	U=len(K);M=[];W=[];X=0
	if len(E)>0:Y=NotebookShared.objects.filter(Q(is_delete=0,user_group__in=E,notebook__is_delete=0)|Q(is_delete=0,user=C,notebook__is_delete=0))
	else:Y=NotebookShared.objects.filter(is_delete=0,user=C,notebook__is_delete=0)
	for m in Y:
		Z=d;B=m.notebook
		if G in B.name.lower():Z=S
		if Z:
			if B.notebook_id not in W:W.append(B.notebook_id);M.append({'notebook_id':B.notebook_id,N:B.name,O:Truncator(B.name).chars(D),P:B.description,R:Truncator(B.description).chars(D)})
	X=len(M);a=0;b={e:h,f:U,g:X}
	for(o,n)in b.items():a+=n
	return{'res':1,e:J,f:K,g:M,'cntTotal':a,'counter_dict':b}