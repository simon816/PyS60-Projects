import dialog as _dialog
from time import time
class Wait:
 def __init__(self, label=u'',onfinish=0,cancelbtn=0):
  self.obj=_dialog.Wait
  self.inst_state=0
  self.label=label
  self.cancelB=cancelbtn
  self.finish=onfinish
  if cancelbtn:
   raise RuntimeWarning('Warning! Using a cancel button is very buggy')
 def update(self):
  if self.inst_state:
   self.show()
 def set_label(self,label):
  if label:self.label=unicode(label)
 def show(self):
  params=[self.label]
  if self.cancelB:
   params.extend([1,self.cancelB])
  self.inst=self.obj(*params)
  self.inst.show()
  self.inst_state=1
 def close(self):
  if self.cancelB:
   self.cancelB=0 # } force update as cannot close if
   self.update()    # } self.cancelB exists 
  if self.finish:
   self.finish()
  self.inst.close()
  self.inst_state=0

class Progress:
 def __init__(self,label=u'', bars=5, time=5):
  self.label=label
  self.maxbars=bars
  self.time=time
  self.prog=_dialog.Progress(unicode(label),bars,time,1)
  self.start=0
  self.barworth=float(time)/bars
 def bars(self):
  return self.prog.bars()
 def close(self):
  self.prog.close()
  self.start=0
 def goto(self,pos):
  cpos=self.bars()
  self.prog.goto(pos)
  if pos > cpos:
   self.start-=self.barworth*(pos-cpos)
  elif pos < cpos:
   self.start+=self.barworth*(cpos-pos)
  return 1
 def set_label(self,label):
  self.label=label
  self.prog.set_label(unicode(label))
 def show(self):
  self.prog.show()
  self.start=time()
 def step(self,pos=1):
  return self.goto(self.bars()+pos)
 def isopen(self):
  return time()-self.start<self.time
del _dialog