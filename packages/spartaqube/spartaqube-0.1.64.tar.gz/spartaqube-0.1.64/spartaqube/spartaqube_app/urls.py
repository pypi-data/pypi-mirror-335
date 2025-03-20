from django.contrib import admin
from django.urls import path
from django.urls import path,re_path,include
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve
import debug_toolbar
from.url_base import get_url_patterns as get_url_patterns_base
from.url_spartaqube import get_url_patterns as get_url_patterns_spartaqube
handler404='project.sparta_2a12c2aa15.sparta_5e33e02709.qube_39f1734673.sparta_305aa0245b'
handler500='project.sparta_2a12c2aa15.sparta_5e33e02709.qube_39f1734673.sparta_ede5bf8f5d'
handler403='project.sparta_2a12c2aa15.sparta_5e33e02709.qube_39f1734673.sparta_15f4245021'
handler400='project.sparta_2a12c2aa15.sparta_5e33e02709.qube_39f1734673.sparta_114b8a6cb3'
urlpatterns=get_url_patterns_base()+get_url_patterns_spartaqube()
if settings.B_TOOLBAR:urlpatterns+=[path('__debug__/',include(debug_toolbar.urls))]