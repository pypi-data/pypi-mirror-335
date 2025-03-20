from django.contrib import admin
from django.urls import path
from django.urls import path,re_path,include
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve
import debug_toolbar
from.url_base import get_url_patterns as get_url_patterns_base
from.url_spartaqube import get_url_patterns as get_url_patterns_spartaqube
handler404='project.sparta_724d6e104f.sparta_270c634a73.qube_b64b7f13e3.sparta_d8f58c9fb1'
handler500='project.sparta_724d6e104f.sparta_270c634a73.qube_b64b7f13e3.sparta_f66934afc0'
handler403='project.sparta_724d6e104f.sparta_270c634a73.qube_b64b7f13e3.sparta_a4992dd4a3'
handler400='project.sparta_724d6e104f.sparta_270c634a73.qube_b64b7f13e3.sparta_7eff103e7d'
urlpatterns=get_url_patterns_base()+get_url_patterns_spartaqube()
if settings.B_TOOLBAR:urlpatterns+=[path('__debug__/',include(debug_toolbar.urls))]