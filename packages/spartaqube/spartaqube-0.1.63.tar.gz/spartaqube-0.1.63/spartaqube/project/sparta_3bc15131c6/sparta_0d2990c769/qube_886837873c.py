_A='windows'
import os,platform,getpass
def sparta_02c62a021f():
	try:A=str(os.environ.get('IS_REMOTE_SPARTAQUBE_CONTAINER','False'))=='True'
	except:A=False
	return A
def sparta_9761ee48b4():
	A=platform.system()
	if A=='Windows':return _A
	elif A=='Linux':return'linux'
	elif A=='Darwin':return'mac'
	else:return
def sparta_235d77fd71():
	if sparta_02c62a021f():return'/spartaqube'
	A=sparta_9761ee48b4()
	if A==_A:B=f"C:\\Users\\{getpass.getuser()}\\SpartaQube"
	elif A=='linux':B=os.path.expanduser('~/SpartaQube')
	elif A=='mac':B=os.path.expanduser('~/Library/Application Support\\SpartaQube')
	return B