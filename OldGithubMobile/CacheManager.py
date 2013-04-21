from GithubGlobals import *
import os
def createCache(dir):
 return Cache(dir)
def moveCache():
 pass
class Cache:
 # cache object
 def __init__(self,dir):
  self.dir=dir
  util.mkdir([dir])
 def bindToRepo(self,repo):
  # attaches a Reposory object to the cache
  self.repo=repo
 def makefile(self,name):
  filename=self.dir+'\\'+name
  if not os.path.exists(filename):
   util.mkdir([os.path.split(filename)[0]])
   f=open(filename,'w')
  else:
   f=open(filename, 'r+')
  return f