import re,os,json,requests
from datetime import datetime
from packaging.version import parse
from project.models import AppVersioning
from project.logger_config import logger
import pytz
UTC=pytz.utc
proxies_dict={'http':os.environ.get('http_proxy',None),'https':os.environ.get('https_proxy',None)}
def sparta_5a83e1c87b():0
def sparta_d88db40f11():A='name';B='https://api.github.com/repos/SpartaQube/spartaqube-version/tags';C=requests.get(B,proxies=proxies_dict);D=json.loads(C.text);E=max(D,key=lambda t:parse(t[A]));return E[A]
def sparta_1d12f748ae():A='https://spartaqube-version.pages.dev/latest_version.txt';B=requests.get(A,proxies=proxies_dict);return B.text.split('\n')[0]
def sparta_710edb9025():
	try:A='https://pypi.org/project/spartaqube/';B=requests.get(A,proxies=proxies_dict).text;C=re.search('<h1 class="package-header__name">(.*?)</h1>',B,re.DOTALL);D=C.group(1);E=D.strip().split('spartaqube ')[1];return E
	except:pass
def sparta_c4aba70c92():
	B=os.path.dirname(__file__);C=os.path.dirname(B);D=os.path.dirname(C);E=os.path.dirname(D)
	try:
		with open(os.path.join(E,'app_version.json'),'r')as F:G=json.load(F);A=G['version']
	except:A='0.1.1'
	return A
def sparta_ad35b7f76b():
	G='res'
	try:
		C=sparta_c4aba70c92();A=sparta_1d12f748ae();D=AppVersioning.objects.all();E=datetime.now().astimezone(UTC)
		if D.count()==0:AppVersioning.objects.create(last_available_version_pip=A,last_check_date=E)
		else:B=D[0];B.last_available_version_pip=A;B.last_check_date=E;B.save()
		H=not C==A;return{'current_version':C,'latest_version':A,'b_update':H,'humanDate':'A moment ago',G:1}
	except Exception as F:logger.debug('Exception versioning update');logger.debug(F);return{G:-1,'errorMsg':str(F)}