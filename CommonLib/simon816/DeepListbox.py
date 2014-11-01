import appuifw
class DeepListbox:
 def __init__(self,items,handler):
  self.handler=handler
  self.openarr=u'->'
  self.closearr=u'<-'
  self.subs=[]
  self.subitems=[]
  self.current_offset=0
  list=[]
  for item in items:
   text=item[0]
   if item[1] is not None:
    text+=u' '+self.openarr
    self.subitems.append([item[1],item[0]])
    item[1].reverse()
    self.subs.append({'items':item[1],'isopen':0,'parent':item[0]})
   list.append(text)
  self.lb=appuifw.Listbox(list,self.onclick)
  self.items=list
   
 def onclick(self):
  real=self.lb.current()
  subitems={}
  for i in self.subitems:
   for e in i[0]:
    subitems[e]=i[1]
  for sub in self.subs:
   if sub['parent']==self.items[real][:-len(self.openarr)-1]:
    if not sub['isopen']:
     self.items[real]=sub['parent']+' '+self.closearr
     sub['isopen']=1
     for item in sub['items']:
      self.items.insert(real+1,self.openarr+' '+item)
    else:
     sub['isopen']=0
     self.items[real]=sub['parent']+' '+self.openarr
     for item in sub['items']:
      self.items.remove(self.openarr+' '+item)
    self.lb.set_list(self.items,real)
    return
  n=self.items[real][len(self.openarr)+1:]
  if n in subitems:
   self.handler(subitems[n]+'::'+n)
  elif not self.items[real].endswith(self.closearr) and not self.items[real].endswith(self.openarr):
   self.handler(self.items[real])
 def uiShow(self):
  appuifw.app.body=self.lb
