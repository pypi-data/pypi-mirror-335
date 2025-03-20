import os,zipfile,pytz
UTC=pytz.utc
from django.conf import settings as conf_settings
def sparta_35c7ca1d02():
	B='APPDATA'
	if conf_settings.PLATFORMS_NFS:
		A='/var/nfs/notebooks/'
		if not os.path.exists(A):os.makedirs(A)
		return A
	if conf_settings.PLATFORM=='LOCAL_DESKTOP'or conf_settings.IS_LOCAL_PLATFORM:
		if conf_settings.PLATFORM_DEBUG=='DEBUG-CLIENT-2':return os.path.join(os.environ[B],'SpartaQuantNB/CLIENT2')
		return os.path.join(os.environ[B],'SpartaQuantNB')
	if conf_settings.PLATFORM=='LOCAL_CE':return'/app/notebooks/'
def sparta_8470993bdc(userId):A=sparta_35c7ca1d02();B=os.path.join(A,userId);return B
def sparta_fa91c36303(notebookProjectId,userId):A=sparta_8470993bdc(userId);B=os.path.join(A,notebookProjectId);return B
def sparta_f9e7928cb1(notebookProjectId,userId):A=sparta_8470993bdc(userId);B=os.path.join(A,notebookProjectId);return os.path.exists(B)
def sparta_666c3b49bd(notebookProjectId,userId,ipynbFileName):A=sparta_8470993bdc(userId);B=os.path.join(A,notebookProjectId);return os.path.isfile(os.path.join(B,ipynbFileName))
def sparta_faf4d025db(notebookProjectId,userId):
	C=userId;B=notebookProjectId;D=sparta_fa91c36303(B,C);G=sparta_8470993bdc(C);A=f"{G}/zipTmp/"
	if not os.path.exists(A):os.makedirs(A)
	H=f"{A}/{B}.zip";E=zipfile.ZipFile(H,'w',zipfile.ZIP_DEFLATED);I=len(D)+1
	for(J,M,K)in os.walk(D):
		for L in K:F=os.path.join(J,L);E.write(F,F[I:])
	return E
def sparta_fbc37044e0(notebookProjectId,userId):B=userId;A=notebookProjectId;sparta_faf4d025db(A,B);C=f"{A}.zip";D=sparta_8470993bdc(B);E=f"{D}/zipTmp/{A}.zip";F=open(E,'rb');return{'zipName':C,'zipObj':F}