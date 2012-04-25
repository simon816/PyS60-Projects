import sys
sys.path.append('E:\\Python\\Projects\\')
import newgithub
ns={}
for k in dir(newgithub):
 print k
 ns[k]=getattr(newgithub,k)
del sys,k,newgithub
try:
 x=execfile('E:\\Python\\Projects\\newgithub\\default.py',ns)
except:
 ns.clear()
 raise
ns.clear()
del x