import pkg_resources
from channels.routing import ProtocolTypeRouter,URLRouter
from django.urls import re_path as url
from django.conf import settings
from project.sparta_d3863a192d.sparta_1da18f3cab import qube_969539d1cd,qube_7b0d8de758,qube_dcc7c2edf2,qube_5f61bb53d5,qube_a2a1ed9420,qube_0347cc66db,qube_63b050d0e2,qube_103ca9020a,qube_8ede9f43da
from channels.auth import AuthMiddlewareStack
import channels
channels_ver=pkg_resources.get_distribution('channels').version
channels_major=int(channels_ver.split('.')[0])
def sparta_a2121d6566(this_class):
	A=this_class
	if channels_major<=2:return A
	else:return A.as_asgi()
urlpatterns=[url('ws/statusWS',sparta_a2121d6566(qube_969539d1cd.StatusWS)),url('ws/notebookWS',sparta_a2121d6566(qube_7b0d8de758.NotebookWS)),url('ws/wssConnectorWS',sparta_a2121d6566(qube_dcc7c2edf2.WssConnectorWS)),url('ws/pipInstallWS',sparta_a2121d6566(qube_5f61bb53d5.PipInstallWS)),url('ws/gitNotebookWS',sparta_a2121d6566(qube_a2a1ed9420.GitNotebookWS)),url('ws/xtermGitWS',sparta_a2121d6566(qube_0347cc66db.XtermGitWS)),url('ws/hotReloadLivePreviewWS',sparta_a2121d6566(qube_63b050d0e2.HotReloadLivePreviewWS)),url('ws/apiWebserviceWS',sparta_a2121d6566(qube_103ca9020a.ApiWebserviceWS)),url('ws/apiWebsocketWS',sparta_a2121d6566(qube_8ede9f43da.ApiWebsocketWS))]
application=ProtocolTypeRouter({'websocket':AuthMiddlewareStack(URLRouter(urlpatterns))})
for thisUrlPattern in urlpatterns:
	try:
		if len(settings.DAPHNE_PREFIX)>0:thisUrlPattern.pattern._regex='^'+settings.DAPHNE_PREFIX+'/'+thisUrlPattern.pattern._regex
	except Exception as e:print(e)