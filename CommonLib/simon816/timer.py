import e32
class Timer:
 def __init__(self,call):
  self.callback=call
 def start(self,seconds):
  self.delay=int(seconds)
  self.stopped=False
  if self.delay>0:
   self.elapsed=0
   self.loop()
 def loop(self):
  e32.ao_sleep(self.delay,self.check)
 def check(self):
  self.elapsed=self.elapsed+self.delay
  if not self.stopped:
   self.loop()
   self.callback(self.elapsed)
 def stop(self):
  self.stopped=True
