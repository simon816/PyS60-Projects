def int2char(i):
 return a[i-1:i]
def ints2chars(ints):
 i=0;s=''
 while i < len(str(ints)):
  s+=int2char(int(float(str(ints)[i:i+1])))
  i=i+1
 return s

import random
a='abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ\t'
def encode(s,n,o='',w='', al=a):
 for x in range(len(s)):
  n=n+1;c=s[x:x+1]
  if a.find(c)>=0 or w=='a':al+=a;o+=al[al.find(c)+n:al.find(c)+1+n]
  else:
   try:
    if int(c) in range(0,10):o+=chr(int(c)+n)
   except:
    o+=chr(ord(c)+100)
 return o
def decode(s,n,r='', al=a):
 print 'random no.',n
 for z in range(len(s)):
  n=n+1;c=s[z:z+1]
  if al.find(c)>=0:al+=a;r+=al[al.find(c)-n+1:al.find(c)+2-n]
  else:
   if ord(c) in range(0,10+n):r+=str(ord(c)-n+1)
   else:r+=chr(ord(s[z:z+1])-100)
 return r
def decodestring(s,a):return decode(str(s[int(float(s[:1]))+1:]),int(float(a.find(s[1:2])+1)))
def encodestring(s, a):K=random.randint(1,len(a)-1);k=encode(str(K), K, '', 'a');print 'random no.',K,'\nkey',k;return encode(s, K, str(len(k))+k)
import sysinfo
print 'imei',ints2chars(float(sysinfo.imei()))
O=raw_input('encode > ')
e=encodestring(O, a)
d=decodestring(e,a)
print 'origional string= '+O
print 'encoded string= '+e
print 'decoded string= '+d
print decodestring(raw_input('decode > '), a)