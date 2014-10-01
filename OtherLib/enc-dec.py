a='abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
def int2chr(i):
 pass
def encode(s,n,al,o='',w=''):
 a=al
 for x in range(len(s)):
  n=n+1;c=s[x:x+1]
  if a.find(c)>=0 or w=='a':al+=a;o+=al[al.find(c)+n:al.find(c)+1+n]
  else:
   try:
    i=int(c)
    if i<5:o+=str(i+5)
    else:o+=str(i-5)
   except:
    try:o+=chr(ord(c)+n+100)
    except:pass
 return o
def decode(s,n,al,r=''):
 a=al
 for z in range(len(s)):
  n=n+1;c=s[z:z+1]
  if al.find(c)>=0:al+=a;r+=al[al.find(c)-n+1:al.find(c)+2-n]
  else:
   try:
    i=int(c)
    if i<5:r+=str(i+5)
    else:r+=str(i-5)
   except:
    r+=chr(ord(c)-n-99)
 return r
import random
def decodestring(s,a=a):
 s=eval("'%s'"%s)
 return decode(
  str(s[int(s[:1])+1:]),
  int(float(a.find(s[1:2])+1)),
  a
  )
def encodestring(s, a=a):
 n=random.randint(1,len(a)-1)
 k=encode(
  str(n), n,a,'', 'a'
  )
 return repr(encode(
  s, n,a, str(len(k))+k
  ))[1:-1]
# known errors: {}[] dont work
encoded=encodestring("Hello WorldZ")
print encoded
decoded=decodestring(encoded)
print decoded
"""
st="SuperSecret"
l=100
i=0
while i<l:
 st=eval(encodestring(st))
 i=i+1
i=0
st2=st
pr=[l,l-(l/4),l/2,l/4,l/8]
pr.extend(range(0,20))
while i<l:
 st2=decodestring(repr(st2))
 if l-i in pr:print st2
 i=i+1
 """
def testen(string):
 o=""
 prev=ord(string[0])
 #print string[0],prev
 for letter in string[1:]:
  xo=(prev^ord(letter))
  o+=chr(xo)#chr(xo^ord(letter))
  prev=ord(letter)
 o+=chr(prev)
 return o
def testde(string):
 o=""
 prev=ord(string[0])
 for letter in string[1:]:
  print (prev^ord(letter))^ord("l")
  prev=ord(letter)


en=testen("hello")
print repr(en)
testde(en)