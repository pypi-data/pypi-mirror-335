import pkg_resources
from channels.routing import ProtocolTypeRouter,URLRouter
from django.urls import re_path as url
from django.conf import settings
from project.sparta_76336d2b79.sparta_60cd085f1e import qube_48105bff7f,qube_d608101e00,qube_b44edb5a70,qube_fb5c83b93d,qube_1fe735dcd0,qube_d6dfb49999,qube_5327be23f7,qube_24fd825ff5,qube_70dbdc8380
from channels.auth import AuthMiddlewareStack
import channels
channels_ver=pkg_resources.get_distribution('channels').version
channels_major=int(channels_ver.split('.')[0])
def sparta_cb63289e99(this_class):
	A=this_class
	if channels_major<=2:return A
	else:return A.as_asgi()
urlpatterns=[url('ws/statusWS',sparta_cb63289e99(qube_48105bff7f.StatusWS)),url('ws/notebookWS',sparta_cb63289e99(qube_d608101e00.NotebookWS)),url('ws/wssConnectorWS',sparta_cb63289e99(qube_b44edb5a70.WssConnectorWS)),url('ws/pipInstallWS',sparta_cb63289e99(qube_fb5c83b93d.PipInstallWS)),url('ws/gitNotebookWS',sparta_cb63289e99(qube_1fe735dcd0.GitNotebookWS)),url('ws/xtermGitWS',sparta_cb63289e99(qube_d6dfb49999.XtermGitWS)),url('ws/hotReloadLivePreviewWS',sparta_cb63289e99(qube_5327be23f7.HotReloadLivePreviewWS)),url('ws/apiWebserviceWS',sparta_cb63289e99(qube_24fd825ff5.ApiWebserviceWS)),url('ws/apiWebsocketWS',sparta_cb63289e99(qube_70dbdc8380.ApiWebsocketWS))]
application=ProtocolTypeRouter({'websocket':AuthMiddlewareStack(URLRouter(urlpatterns))})
for thisUrlPattern in urlpatterns:
	try:
		if len(settings.DAPHNE_PREFIX)>0:thisUrlPattern.pattern._regex='^'+settings.DAPHNE_PREFIX+'/'+thisUrlPattern.pattern._regex
	except Exception as e:print(e)