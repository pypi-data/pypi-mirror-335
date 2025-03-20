import os
from project.sparta_d3863a192d.sparta_16b6cf6949.qube_8150d2d2a5 import qube_8150d2d2a5
from project.sparta_d3863a192d.sparta_16b6cf6949.qube_1adbc6fbe0 import qube_1adbc6fbe0
from project.sparta_d3863a192d.sparta_16b6cf6949.qube_98a09a644e import qube_98a09a644e
from project.sparta_d3863a192d.sparta_16b6cf6949.qube_2b769c79b1 import qube_2b769c79b1
class db_connection:
	def __init__(A,dbType=0):A.dbType=dbType;A.dbCon=None
	def get_db_type(A):return A.dbType
	def getConnection(A):
		if A.dbType==0:
			from django.conf import settings as B
			if B.PLATFORM in['SANDBOX','SANDBOX_MYSQL']:return
			A.dbCon=qube_8150d2d2a5()
		elif A.dbType==1:A.dbCon=qube_1adbc6fbe0()
		elif A.dbType==2:A.dbCon=qube_98a09a644e()
		elif A.dbType==4:A.dbCon=qube_2b769c79b1()
		return A.dbCon