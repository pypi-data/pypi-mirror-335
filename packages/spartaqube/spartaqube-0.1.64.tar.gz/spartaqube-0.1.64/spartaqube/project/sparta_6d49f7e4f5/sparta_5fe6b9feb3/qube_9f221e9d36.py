_A='utf-8'
import os,json,base64,hashlib,random
from cryptography.fernet import Fernet
def sparta_078a0e4e74():A='__API_AUTH__';A=A.encode(_A);A=hashlib.md5(A).hexdigest();A=base64.b64encode(A.encode(_A));return A
def sparta_afe2f5c7f2(objectToCrypt):A=objectToCrypt;C=sparta_078a0e4e74();D=Fernet(C);A=A.encode(_A);B=D.encrypt(A).decode(_A);B=base64.b64encode(B.encode(_A)).decode(_A);return B
def sparta_d2f5f886aa(apiAuth):A=apiAuth;B=sparta_078a0e4e74();C=Fernet(B);A=base64.b64decode(A);return C.decrypt(A).decode(_A)
def sparta_bcef0fdabc(kCrypt):A='__SQ_AUTH__'+str(kCrypt);A=A.encode(_A);A=hashlib.md5(A).hexdigest();A=base64.b64encode(A.encode(_A));return A
def sparta_1586ae4ff4(objectToCrypt,kCrypt):A=objectToCrypt;C=sparta_bcef0fdabc(kCrypt);D=Fernet(C);A=A.encode(_A);B=D.encrypt(A).decode(_A);B=base64.b64encode(B.encode(_A)).decode(_A);return B
def sparta_ca27053d4e(objectToDecrypt,kCrypt):A=objectToDecrypt;B=sparta_bcef0fdabc(kCrypt);C=Fernet(B);A=base64.b64decode(A);return C.decrypt(A).decode(_A)
def sparta_a1c774496d(kCrypt):A='__SQ_EMAIL__'+str(kCrypt);A=A.encode(_A);A=hashlib.md5(A).hexdigest();A=base64.b64encode(A.encode(_A));return A
def sparta_6a4ea19e3a(objectToCrypt,kCrypt):A=objectToCrypt;C=sparta_a1c774496d(kCrypt);D=Fernet(C);A=A.encode(_A);B=D.encrypt(A).decode(_A);B=base64.b64encode(B.encode(_A)).decode(_A);return B
def sparta_c97804ba92(objectToDecrypt,kCrypt):A=objectToDecrypt;B=sparta_a1c774496d(kCrypt);C=Fernet(B);A=base64.b64decode(A);return C.decrypt(A).decode(_A)
def sparta_c0e5ba4abe(kCrypt):A='__SQ_KEY_SSO_CRYPT__'+str(kCrypt);A=A.encode(_A);A=hashlib.md5(A).hexdigest();A=base64.b64encode(A.encode(_A));return A
def sparta_20ff951ce1(objectToCrypt,kCrypt):A=objectToCrypt;C=sparta_c0e5ba4abe(kCrypt);D=Fernet(C);A=A.encode(_A);B=D.encrypt(A).decode(_A);B=base64.b64encode(B.encode(_A)).decode(_A);return B
def sparta_dfdb21a6cd(objectToDecrypt,kCrypt):A=objectToDecrypt;B=sparta_c0e5ba4abe(kCrypt);C=Fernet(B);A=base64.b64decode(A);return C.decrypt(A).decode(_A)
def sparta_b8dc5a0994():A='__SQ_IPYNB_SQ_METADATA__';A=A.encode(_A);A=hashlib.md5(A).hexdigest();A=base64.b64encode(A.encode(_A));return A
def sparta_980d9e2d88(objectToCrypt):A=objectToCrypt;C=sparta_b8dc5a0994();D=Fernet(C);A=A.encode(_A);B=D.encrypt(A).decode(_A);B=base64.b64encode(B.encode(_A)).decode(_A);return B
def sparta_01a0cc1a29(objectToDecrypt):A=objectToDecrypt;B=sparta_b8dc5a0994();C=Fernet(B);A=base64.b64decode(A);return C.decrypt(A).decode(_A)