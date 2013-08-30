from e32 import ao_sleep
from simon816.text import text
class ExtendedEditor(text):
 def extend(self):
  self.tabsize=4
  self.bind("key",self.keys)
  self.listen_keys={}
  del self.bindable[self.bindable.index("key")]
 def keys(self,code, properties):
  self.last_key=k=properties[1]
  if k in self.listen_keys:
   self.listen_keys[k](code,properties)
  elif code in self.listen_keys:
   self.listen_keys[code](code,properties)
 def change_color(self,r,g,b):
  self.t.color=self.rgb(r,g,b)
  self.t.add(u'')
 def keyword(self,word,callback):
  #calls callback if word found when typing
  def p(*a):
   existing=word[:-1];l=len(existing)
   if l>self.t.len():return
   before=self.t.get(self.t.get_pos()-l,l)
   if before==existing:callback()
  self.listen_keys[word[-1:]]=p
 def get_lines(self):
  return self.t.get()[:self.t.get_pos()].split(u'\u2029')
 def get_before_lines(self):
  cpos=self.t.get_pos()
  all_lines=self.t.get().split(u'\u2029')
  before=[]
  for line in all_lines:
   before.append(line)
   if len(u'\u2029'.join(before))>=cpos:
    break
  return before
 def get_line_no(self):
  return len(self.get_lines())-1
 def get_current_line(self):
  lineno=self.get_line_no()
  all_pre_lines=self.get_lines()
  return all_pre_lines[lineno]
 def get_pos_on_line(self):
  pass
 def inherit_indent(self):
  def on_enter(*a):
   current_line=self.get_current_line()
   indent=len(current_line)-len(current_line.lstrip())
   for begin,end in {'(':')','{':'}','[':']','<':'>'}.iteritems():
    begins=current_line.count(begin)
    ends=current_line.count(end)
    if begins>ends:
     indent+=self.tabsize
     break # ? could be a feature
    elif ends>begins:
     indent-=self.tabsize
     break # ? could be a feature
   spaces=u''.join([' ' for i in range(indent)])
   addindent=lambda:self.t.add(spaces)
   ao_sleep(0,addindent) # an almost 0 delay between keypress and resulting key action
  self.listen_keys[13]=on_enter
 def add(self,text,i=False):
  self.t.add(self.toUnicode(text,i))
"""
e=ExtendedEditor()
e.extend()
import e32
l=e32.Ao_lock()
e.bind('exit',l.signal)
e.loadText('<html>\n<head>\n</head>\n<body>\n</body>\n</html>')
e.inherit_indent()
e.display()
l.wait()
"""