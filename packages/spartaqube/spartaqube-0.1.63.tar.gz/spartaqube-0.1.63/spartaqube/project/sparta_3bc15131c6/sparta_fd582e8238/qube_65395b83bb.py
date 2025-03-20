_A='is_size_reduced'
import os,sys,json,ast,re,base64,uuid,hashlib,socket,cloudpickle,websocket,subprocess,threading
from random import randint
import pandas as pd
from pathlib import Path
from cryptography.fernet import Fernet
from subprocess import PIPE
from datetime import datetime,timedelta
from django.contrib.auth.models import User
from django.db.models import Q
from django.core.cache import cache
from django.conf import settings as conf_settings
import pytz
UTC=pytz.utc
from project.models import UserProfile
def sparta_08e81ef554(json_data,user_obj):
	C=json_data[_A];A=UserProfile.objects.filter(user=user_obj)
	if A.count()>0:B=A[0];B.is_size_reduced_plot_db=C;B.save()
	return{'res':1}
def sparta_08001d1a5b(json_data,user_obj):
	C=json_data[_A];A=UserProfile.objects.filter(user=user_obj)
	if A.count()>0:B=A[0];B.is_size_reduced_api=C;B.save()
	return{'res':1}