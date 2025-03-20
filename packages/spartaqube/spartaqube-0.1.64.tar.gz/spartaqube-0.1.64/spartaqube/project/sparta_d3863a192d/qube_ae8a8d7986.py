import time
from project.logger_config import logger
def sparta_18f39d56ed():
	B=0;A=time.time()
	while True:B=A;A=time.time();yield A-B
TicToc=sparta_18f39d56ed()
def sparta_755a9ac0c1(tempBool=True):
	A=next(TicToc)
	if tempBool:logger.debug('Elapsed time: %f seconds.\n'%A);return A
def sparta_d5fbf8d040():sparta_755a9ac0c1(False)