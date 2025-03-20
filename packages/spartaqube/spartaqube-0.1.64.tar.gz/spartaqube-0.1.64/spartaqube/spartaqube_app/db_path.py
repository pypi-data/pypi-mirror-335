import os,sys,getpass,platform
from project.sparta_6d49f7e4f5.sparta_bb74460757.qube_96ecfb2e32 import sparta_dac749eee2,sparta_51cdb2420e
def sparta_ec9cdd001b(full_path,b_print=False):
	B=b_print;A=full_path
	try:
		if not os.path.exists(A):
			os.makedirs(A)
			if B:print(f"Folder created successfully at {A}")
		elif B:print(f"Folder already exists at {A}")
	except Exception as C:print(f"An error occurred: {C}")
def sparta_6b3b338259():
	if sparta_51cdb2420e():A='/app/APPDATA/local_db/db.sqlite3'
	else:C=sparta_dac749eee2();B=os.path.join(C,'data');sparta_ec9cdd001b(B);A=os.path.join(B,'db.sqlite3')
	return A