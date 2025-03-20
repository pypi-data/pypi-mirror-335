import time
from project.logger_config import logger
def sparta_e8700c0dec():
	B=0;A=time.time()
	while True:B=A;A=time.time();yield A-B
TicToc=sparta_e8700c0dec()
def sparta_bea9101033(tempBool=True):
	A=next(TicToc)
	if tempBool:logger.debug('Elapsed time: %f seconds.\n'%A);return A
def sparta_c6aedcd902():sparta_bea9101033(False)