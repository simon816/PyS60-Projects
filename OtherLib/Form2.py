import appuifw
class MenuItem:
  def __init__(self, label='', callback=None):
    self.setLabel(label)
    self.setCallback(callback)
    self._i=[]
  def setLabel(self, label):
    self._l=unicode(label)
  def setCallback(self, cb):
    if not hasattr(cb, '__call__'):
      cb=lambda:None
    self._c=cb
  def _get(self):
    return (self._l, self._c)
  def addItem(self, item):
    self._i.append(item._get())
    if len(self._i)>1:
      self._c=tuple(self._i)
class Menu:
  def __init__(self, handle, clear=False):
    if clear:
      for m in range(len(handle)):del handle[0]
    self._menu=handle
  def addItem(self, item):
    self._menu.append(item._get())
class Form(object):
  TEXT = 'text'
  NUMBER = 'number'
  DATE = 'date'
  TIME = 'time'
  COMBO = 'combo'
  EDIT = appuifw.FFormEditModeOnly
  VIEW = appuifw.FFormViewModeOnly
  def __init__(self, unique=True):
    if unique:
      self._data={}
    else:
      self._data=[]
    self._flags=0
    self.menu=Menu([])
    self.unique=unique
    
  def add_field(self, type, label, data=None,i=0):
    label=unicode(label)
    if data == None:
      if type==self.COMBO:
        raise ValueError('Field type %r must have data'%type)
    else:
      if type==self.COMBO:
        data=(map(unicode, data),i)
    if self.unique:
      if label in self._data:
        raise ValueError('Form is unique but tried to add duplicate key')
      self._data[label]=(len(self._data), type, data)
    else:
      if data is None:
        self._data.append((label, type))
      else:
        self._data.append((label, type, data))
  def set_mode(self, mode):
    if mode == self.VIEW:
      self._flags|=self.EDIT
      self._flags-=self.EDIT
      self._flags|=mode
    if mode == self.EDIT:
      self._flags|=self.VIEW
      self._flags-=self.VIEW
      self._flags|=mode
  def display(self):
      if self.unique:
          data = [None] * len(self._data)
          for label,d in self._data.iteritems():
              if d[2] is not None:
                data[d[0]] = (label, d[1], d[2])
              else:
                data[d[0]] = (label, d[1])
      else:
          data=self._data
      print repr(data)
      self.f = appuifw.Form(data, self._flags)
      self.f.menu = self.menu._menu
      return self.f.execute()
  def get_value(self, key):
      if self.f:
          for fe in self.f:
              if key == fe[0] and len(fe) > 2:
                  return fe[2]
      if self.unique:
          return self._data[key][2]
  def set_value(self, key, value):
      if self.f:
          i=0
          for fe in self.f:
              if key == fe[0]:
                  self.f[i] = (fe[0], fe[1], value)
              i+=1
  def __setattr__(self, k, v):
     if k=='edit_labels':
       if v==True:
         self._flags|=appuifw.FFormAutoLabelEdit
       else:
         self._flags|=appuifw.FFormAutoLabelEdit
         self._flags-=appuifw.FFormAutoLabelEdit
     if k=='double_layer':
       if v==True:
         self._flags|=appuifw.FFormDoubleSpaced
       else:
         self._flags|=appuifw.FFormDoubleSpaced
         self._flags-=appuifw.FFormDoubleSpaced
     self.__dict__[k]=v

if __name__== '__main__':
  f=Form()
  f.edit_labels=False
  f.double_layer=True
  f.add_field(f.TEXT, 'test')
  f.add_field(f.TEXT, 'test2')
  #f.add_field(f.COMBO, 'combo')
  f.set_mode(f.EDIT)
  def cb():
    print [a for a in f._form]
    print dir(f._form)
  f.menu.addItem(MenuItem(u'qwerty', cb))
  f.menu.addItem(MenuItem(u'qwerty', cb))
  f.display()