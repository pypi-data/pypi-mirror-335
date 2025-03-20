import os,sys,getpass,platform
from project.sparta_3bc15131c6.sparta_0d2990c769.qube_886837873c import sparta_235d77fd71,sparta_02c62a021f
def sparta_220289455a(full_path,b_print=False):
	B=b_print;A=full_path
	try:
		if not os.path.exists(A):
			os.makedirs(A)
			if B:print(f"Folder created successfully at {A}")
		elif B:print(f"Folder already exists at {A}")
	except Exception as C:print(f"An error occurred: {C}")
def sparta_5b5d2a5060():
	if sparta_02c62a021f():A='/app/APPDATA/local_db/db.sqlite3'
	else:C=sparta_235d77fd71();B=os.path.join(C,'data');sparta_220289455a(B);A=os.path.join(B,'db.sqlite3')
	return A