from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.conf import settings as conf_settings
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime
import hashlib,project.sparta_76336d2b79.sparta_76426419cc.qube_7aa7c52dd2 as qube_7aa7c52dd2
from project.sparta_3bc15131c6.sparta_6d9c27d78c.qube_9777884b7b import sparta_34d9a3cc83
@csrf_exempt
def sparta_48e6c5b418(request):B=request;A=qube_7aa7c52dd2.sparta_2ebbb966d2(B);A['menuBar']=8;A['bCodeMirror']=True;C=qube_7aa7c52dd2.sparta_86bdc57f92(B.user);A.update(C);return render(B,'dist/project/api/api.html',A)