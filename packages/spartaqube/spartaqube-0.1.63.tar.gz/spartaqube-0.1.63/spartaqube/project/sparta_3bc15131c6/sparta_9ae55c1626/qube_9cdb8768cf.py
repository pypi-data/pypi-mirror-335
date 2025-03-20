_A='utf-8'
import os,json,base64,hashlib,random
from cryptography.fernet import Fernet
def sparta_6bc0766204():A='__API_AUTH__';A=A.encode(_A);A=hashlib.md5(A).hexdigest();A=base64.b64encode(A.encode(_A));return A
def sparta_086c0120fe(objectToCrypt):A=objectToCrypt;C=sparta_6bc0766204();D=Fernet(C);A=A.encode(_A);B=D.encrypt(A).decode(_A);B=base64.b64encode(B.encode(_A)).decode(_A);return B
def sparta_bd83078eb1(apiAuth):A=apiAuth;B=sparta_6bc0766204();C=Fernet(B);A=base64.b64decode(A);return C.decrypt(A).decode(_A)
def sparta_886a10fc03(kCrypt):A='__SQ_AUTH__'+str(kCrypt);A=A.encode(_A);A=hashlib.md5(A).hexdigest();A=base64.b64encode(A.encode(_A));return A
def sparta_71c25e6d1a(objectToCrypt,kCrypt):A=objectToCrypt;C=sparta_886a10fc03(kCrypt);D=Fernet(C);A=A.encode(_A);B=D.encrypt(A).decode(_A);B=base64.b64encode(B.encode(_A)).decode(_A);return B
def sparta_4cc35f441f(objectToDecrypt,kCrypt):A=objectToDecrypt;B=sparta_886a10fc03(kCrypt);C=Fernet(B);A=base64.b64decode(A);return C.decrypt(A).decode(_A)
def sparta_355a7829a8(kCrypt):A='__SQ_EMAIL__'+str(kCrypt);A=A.encode(_A);A=hashlib.md5(A).hexdigest();A=base64.b64encode(A.encode(_A));return A
def sparta_30546d1822(objectToCrypt,kCrypt):A=objectToCrypt;C=sparta_355a7829a8(kCrypt);D=Fernet(C);A=A.encode(_A);B=D.encrypt(A).decode(_A);B=base64.b64encode(B.encode(_A)).decode(_A);return B
def sparta_76e6aa3f9b(objectToDecrypt,kCrypt):A=objectToDecrypt;B=sparta_355a7829a8(kCrypt);C=Fernet(B);A=base64.b64decode(A);return C.decrypt(A).decode(_A)
def sparta_3717a0c1a3(kCrypt):A='__SQ_KEY_SSO_CRYPT__'+str(kCrypt);A=A.encode(_A);A=hashlib.md5(A).hexdigest();A=base64.b64encode(A.encode(_A));return A
def sparta_35c1313229(objectToCrypt,kCrypt):A=objectToCrypt;C=sparta_3717a0c1a3(kCrypt);D=Fernet(C);A=A.encode(_A);B=D.encrypt(A).decode(_A);B=base64.b64encode(B.encode(_A)).decode(_A);return B
def sparta_38b5f55822(objectToDecrypt,kCrypt):A=objectToDecrypt;B=sparta_3717a0c1a3(kCrypt);C=Fernet(B);A=base64.b64decode(A);return C.decrypt(A).decode(_A)
def sparta_5643c8f25d():A='__SQ_IPYNB_SQ_METADATA__';A=A.encode(_A);A=hashlib.md5(A).hexdigest();A=base64.b64encode(A.encode(_A));return A
def sparta_1b707002c3(objectToCrypt):A=objectToCrypt;C=sparta_5643c8f25d();D=Fernet(C);A=A.encode(_A);B=D.encrypt(A).decode(_A);B=base64.b64encode(B.encode(_A)).decode(_A);return B
def sparta_ab3422cd03(objectToDecrypt):A=objectToDecrypt;B=sparta_5643c8f25d();C=Fernet(B);A=base64.b64decode(A);return C.decrypt(A).decode(_A)