import appuifw as ui
app=ui.app
class tabs:
 def __init__(self,tabs=[],callbacks=[]):
  self.tabs=tabs
  self.callback=callbacks
  self.selected=0
  self.update()
 def update(self):
  app.set_tabs(self.tabs, self.handler)
  self.select_tab(self.selected)
 def handler(self, index):
  self.selected=index
  try:self.callback[index]({'index':index,'name':self.tabs[index]})
  except:
   try:self.callback[index]()
   except:pass
 def new_tab(self,value, call,index=-1):
  if value:
   if index==-1:self.tabs.append(value);self.callback.append(call)
   else:self.tabs.insert(index,value);self.callback.insert(index,call)
   self.update()
 def _getTab(self,tab):
  try:
   i=int(tab)
   if i==len(self.tabs):raise 'OutOfRange'
   else:return i
  except:
   try:return self.tabs.index(tab)
   except:return None
 def change_tab(self,tab,new,call=None):
  i=self._getTab(tab)
  if i or i==0 and new:self.tabs[i]=new
  if call:self.callback[i]=call
  self.update()
 def select_tab(self,tab,doCall=0):
  i=self._getTab(tab)
  if i or i==0:
   app.activate_tab(i)
   self.selected=i
   if doCall:self.handler(i)
 def delete_tab(self,tab):
  i=self._getTab(tab)
  if i or i==0:
   self.tabs.remove(self.tabs[i])
   self.callback.remove(self.callback[i])
  self.update()
 def current(self):return self.tabs[self.selected]
 def blank(self):pass
 def hide_tabs(self):
  app.set_tabs([],self.blank)
 def show_tabs(self):self.update()
 def reset(self):self.__init__()


# test
import e32
l=e32.Ao_lock()
t=tabs()
def test_exit():
 l.signal()
 t.hide_tabs()
 
app.exit_key_handler=test_exit
app.body=ui.Text()
def test_call(data):print data
def test_new():
 t.new_tab(ui.query(u'Name','text'),test_call)
def test_change():
 c=ui.multi_query(u'Old',u'New')
 o=c[0];n=c[1]
 try:o=int(float(o))
 except:pass
 t.change_tab(o,n)
def test_select():
 t.select_tab(ui.query(u'Select','text'))
def test_delete():
 t.delete_tab(ui.query(u'Delete','text'))
app.menu=[(u'New Tab',test_new),(u'Change Tab',test_change),(u'Select Tab',test_select),(u'Delete Tab', test_delete),(u'Reset',t.reset)]
l.wait()