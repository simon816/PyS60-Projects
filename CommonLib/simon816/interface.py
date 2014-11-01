import e32
import appuifw
import sys

class Listbox:
    def __init__(self, items, callback=None):
        listitems = []
        callbacks = {}
        i = 0
        for item in items:
            if type(item) is str:
                item = unicode(item)
            if type(item) is unicode:
                listitems.append(item)
                callbacks[i] = callback
            elif type(item) is tuple:
                entry = item[0]
                if hasattr(item[1], '__call__'):
                    callbacks[i] = item[1]
                else:
                    entry = item[:2]
                    if len(item) > 2:
                        callbacks[i] = item[2]
                    else:
                        callbacks[i] = callback
                listitems.append(entry)
            elif type(item) is dict:
                for call, its in item.iteritems():
                    for it in its:
                        listitems.append(it)
                    callbacks[i] = call
            i += 1
        self._data = (listitems, callbacks)
        self._lb = appuifw.Listbox(listitems, self._handler)

    def get_listbox(self):
        return self._lb

    def _handler(self):
        curr = self._lb.current()
        item = self._data[0][curr]
        call = self._data[1][curr]
        if hasattr(call, '__call__'):
            try: call(item)
            except TypeError: call()

class Window:
  def __init__(self,props,parent=None):
    self.name='Unnamed'
    if parent is None:parent=BLANK_WINDOW
    self.parent=parent
    self._status='unused'
    if 'body' in props and isinstance(props['body'], Listbox):
        props['listbox'] = props['body']
        props['body'] = props['listbox'].get_listbox()
    self.__dict__.update(props)
  def override(self):
    appuifw.app.body=self.body
    appuifw.app.menu=self.menu
    appuifw.app.title=unicode(self.title)
    appuifw.app.exit_key_handler=self.exit
    self._status='active'
  def parent_window(self):
    return self.parent
  def remove(self):
    self.parent.override()
    self._status='inactive'
  def destroy(self):
    self.__dict__={}
    self._status='dead'
  def __repr__(self):
    return 'Window(%s)'%str({'body':self.body,'exit':self.exit,'menu':self.menu,'title':self.title})
  def __str__(self):
    return '<Window "%s" status:%s>'%(self.name,self._status)
BLANK_WINDOW=Window({
  'body':None,
  'menu':[],
  'title':u'',
  'exit':lambda:BLANK_WINDOW.remove(),
  'name':"BLANK_WINDOW"
  },False)

class Interface:
  def __init__(self):
   self._lock=e32.Ao_lock()
   self._active=self.get_screen()
   self._active.exit=self._lock.signal
  def create_screen(self,**kwargs):
    if not 'exit' in kwargs:kwargs['exit']=self.current('exit')
    if not 'menu' in kwargs:kwargs['menu']=[(u'Exit',kwargs['exit'])]
    if not 'body' in kwargs:kwargs['body']=None
    if not 'title' in kwargs:kwargs['title']=''
    return Window(kwargs,self._active)
  def current(self,thing):
    return getattr(self._active,thing)
  def set_screen(self,window):
    window.override()
    self._active=window
    try:self._lock.wait()
    except AssertionError:
      pass
  def close_current(self):
    self._active.remove()
    self._active=self._active.parent_window()
  def get_screen(self):
    return Window({
    'body':appuifw.app.body,
    'menu':appuifw.app.menu,
    'title':appuifw.app.title,
    'exit':appuifw.app.exit_key_handler
    })
  def listbox(self,items,callback=None):
      return Listbox(items, callback)
  def form(self,items,flags=0,save=None,menu=None):
    f=appuifw.Form(items,flags)
    if menu is not None:
      f.menu=menu
    if save is not None:
      f.save_hook=save
    f.execute()
    if save is None:
      return f
  def over_list(self,items):
    return appuifw.popup_menu(items)
  def __repr__(self):
    return  '<Interface; current screen: %s>'%self._active
  def error(self,text):
    appuifw.note(unicode(text),'error')
  def password(self,text):
    return appuifw.query(unicode(text),'code')
  def prompt(self,text):
    return appuifw.query(unicode(text),'text')
  def alert(self,text):
    appuifw.note(unicode(text),'info')
  def success(self,text):
    appuifw.note(unicode(text),'conf')
  def prompt2(self,label1,label2):
    return appuifw.multi_query(unicode(label1),unicode(label2))
  def confirm(self,text):
    return appuifw.query(unicode(text),'query')

I = None
def get_interface():
    global I
    if not I: I = Interface()
    return I
if __name__ == '__main__':
    get_interface()
    I.set_screen(I.create_screen(body=I.listbox([u'test'])))