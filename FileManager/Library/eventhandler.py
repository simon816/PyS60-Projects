"""
about:
trigger multiple functions simultaneously without functions overiding each other.
the 'event' is an object which contains properties about the function, properties include the function instance, arguments and instructions of how/when to execute the function
Quick Guide

function eventHander.add_event(func,opts="",args=[])
func = function to be called when events begin
opts = string of options options are:
  'p' --> priority. calls first in line, if multiple priorities exist, the order that they were added is the order they are called
  'w' --> wait. waits for the next function to be added before getting called
args = list of arguments to be passed to the function
this function returns the event ID of the new event

function eventHandler.getResponse(id)
id = the event id of a completed event
this function returns the given response or "complete" of a finished event
to save memory, the response is deleted after this is called
raises a not found error if the response does not exist (if the function is not complete it will also raise error.)

function eventHandler.is_ready(id)
id=event id to query
returns 1 if the action is finished, otherwise 0
this function does not raise an error if id doesn't exist
###
syncronous scenario:
here is an example when a callback is not an option
standard method : fn=lambda:"success";response=fn()
eh=eventHandler()
...
id=eh.add_event(lambda:"success")
while not eh.is_ready(id):
   sleep(0.01) # pause, halt, wait etc. (stop your program from continuing) 
response=eh.getResponse(id)
"""
class eventHandler:
 def __init__(self):
  self.queue={}
  self.responses={}
  self.cid=0
  self.doing=False
  self.waiting=False
  self.wait_queue=[]
 def makeID(self):
  self.cid+=1
  return self.cid
 def find_first(self):
  identifier=0
  for id in self.queue:
   if self.queue[id]["i"]==0:identifier=id
  return identifier
 def add_event(self,action,options="",args=[],kwargs={}):
  evt={"f":action,"a":args,"kw":kwargs}
  return self.add_to_queue(self.apply_opts(options,evt))
  
 def add_to_queue(self,eventObj):
  id=self.makeID()
  eventObj["uid"]=id
  if not self.doing:
   self.queue[id]=eventObj
   self.do_events()
  else:
   self.wait_until_ready(eventObj,id)
  return id
 def apply_opts(self,options,evt):
  if 'p' in options:evt["i"]=0
  else:evt["i"]=self.cid
  if 'w' in options:evt["w"]=True
  else:evt["w"]=False
  return evt
 def do_events(self):
  self.doing=True
  def post_event():
   for i in deletelist:del self.queue[i]
   self.doing=False
   self.check_waiting()
  order={}
  deletelist=[]
  for id in self.queue:
   i=self.queue[id]["i"]
   if not i in order:order[i]=[id]
   else:order[i].append(id)
  for priorityid in order:
   for id in order[priorityid]:
    event=self.queue[id]
    if not event["w"]:
     deletelist.append(id)
     try:
      resp=event["f"](*event["a"],**event["kw"])
      self.responses[event["uid"]]=resp or 'complete'
     except:
      self.responses[event["uid"]]='error found'
      post_event()
      raise
    else:
     event["w"]=False
  post_event()
 def wait_until_ready(self,eventobj,eventid):
  if not self.doing:
   self.queue[eventid]=eventobj
   self.do_events()
  else:
   self.waiting=True
   self.wait_queue.append([eventid,eventobj])
 def check_waiting(self):
  if self.waiting:
   self.waiting=False
   i=0
   for bundle in self.wait_queue:
    self.queue[bundle[0]]=bundle[1]
    del self.wait_queue[i]
    i=i+1
   self.do_events()
 def get_response(self,id):
  if id in self.responses.keys():
   r=self.responses[id]
   del self.responses[id]
   return r
  else:
   raise 'Event does not exist or not complete'
 def isready(self,id):
  return id in self.responses.keys()