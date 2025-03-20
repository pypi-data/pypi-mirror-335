import os
from project.sparta_76336d2b79.sparta_8361cbc5b7.qube_9aabd69296 import qube_9aabd69296
from project.sparta_76336d2b79.sparta_8361cbc5b7.qube_d026d07aa7 import qube_d026d07aa7
from project.sparta_76336d2b79.sparta_8361cbc5b7.qube_ca3c1d4c32 import qube_ca3c1d4c32
from project.sparta_76336d2b79.sparta_8361cbc5b7.qube_34f77f9fd8 import qube_34f77f9fd8
class db_connection:
	def __init__(A,dbType=0):A.dbType=dbType;A.dbCon=None
	def get_db_type(A):return A.dbType
	def getConnection(A):
		if A.dbType==0:
			from django.conf import settings as B
			if B.PLATFORM in['SANDBOX','SANDBOX_MYSQL']:return
			A.dbCon=qube_9aabd69296()
		elif A.dbType==1:A.dbCon=qube_d026d07aa7()
		elif A.dbType==2:A.dbCon=qube_ca3c1d4c32()
		elif A.dbType==4:A.dbCon=qube_34f77f9fd8()
		return A.dbCon