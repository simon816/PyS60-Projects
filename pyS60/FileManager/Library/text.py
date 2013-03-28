import appuifw
import StringIO
class BinaryError(Exception):pass
#[[chr(i), i] for i in range(0,256)]
class text:
 def __init__(self):
  self.t=appuifw.Text()
  def make_callback(i):return lambda:self.onkey(i)
  for i in range(256):self.t.bind(i,make_callback(i))
  appuifw.app.menu=[]
  self.bindable=['error','save','saveas','exit','get_settings','save_settings','text_properties','key']
  self.name=""
  self.ch=None
  self.orig=""
  self.type=""
  self.menu=[
   (u'Save',self.saveFile),
   (u'Save As...',self.saveAs),
   (u'Goto',(
    (u'Top',self.toTop),
    (u'Bottom',self.toBottom),
    (u'Line...',self.toLine),
    (u'Line/Col...',self.linecol)
   )),
   (u'Find',(
    (u'Text...',self.find),
    (u'Next',self.next),
    (u'Previous',self.prev),
   )),
   (u'Replace',(
    (u'Text...',self.replace),
    (u'Next',self.replace_next),
    (u'All...',lambda:self.replace(-1))
   )),
   (u'Settings',self.settings)
   ]
  self.default()
 def default(self):
  self.bind('save',lambda f:None)
  self.bind('saveas',lambda n,f:None)
  self.bind('exit',lambda:None)
  self.bind('text_properties',lambda:{})
  self.bind("qwerty", lambda s:None)
  self.bind("get_settings", lambda:{
   'color':(0,0,0),
   'font':(appuifw.available_fonts()[0],20,0),
   'chunkbytes':1024
   })
  self.bind("save_settings", lambda s:None)
  self.bind("key", lambda i, l:None)
  self.css({},method='plain',apply=1)

 def onkey(self, i):
  if i in range(1,28):
   if not i in [8, 9, 27,15,13]:
    self.on("key", i, ['ctrl',chr(i+96)])
   else:
    if i==9:t="tab"
    elif i==27:t="esc"
    elif i==8:t="backspace"
    elif i==15:t="reserved"
    elif i==13:t="enter"
    self.on("key", i, [t,chr(i)])
  elif i in range(65, 91):
   self.on("key", i, ['upper',chr(i)])
  elif i in range(97, 123):
   self.on("key", i, ['lower',chr(i)])
  elif i in range(48, 58):
   self.on("key", i, ['number',int(chr(i))])
  else:
   self.on("key", i, ['other',chr(i)])

 def loadText(self,t,ignore=False):
  css=self.on("text_properties")
  self.css(css,default=1,apply=1)
  self.t.add(self.toUnicode(t,ignore))
  self.orig=self.getText()
  return self.t
 def toUnicode(self,string,ignore=False):
  try:uni=unicode(string);self.type="plain"
  except UnicodeError:
   try:uni=string.decode("utf-8");self.type="utf8"
   except UnicodeError:
    try:uni=string.decode("utf-16");self.type="utf16"
    except UnicodeError:
     if not ignore:raise BinaryError(1,"String is in binary")
     else:uni=string.decode("utf-8",'ignore');self.type="ignore utf8"
  return uni
 def getText(self):
  return self.t.get().replace(u"\u2029", u'\r\n')
 def saveText(self,callopenfile=None):
  newFile=StringIO.StringIO()
  if self.ch:
   self.ch[self.curr_chunk]=self.getText()
   text="".join(self.ch)
  else:text=self.getText()
  if self.type=="utf16":
   text=text.encode("utf-16")
  else:
   text=text.encode("utf-8")
  newFile.write(text)
  newFile.seek(0)
  if callopenfile:
   callopenfile(newFile)
   newFile.close()
  return newFile
 def chunks(self,fh,n,ignore=False):
   self.name=n
   appuifw.note(u"Split File!", "info")
   fh.seek(0)
   ch=[]
   while 1:
    buf=fh.read(self.on("get_settings")["chunkbytes"])
    if not buf:break
    ch.append(buf)
   fh.close()
   def makecall(x):return lambda:self.chunk(x,ignore)
   m=[(unicode(p+1),makecall(p)) for p in range(len(ch))]
   self.menu.insert(0,(u"File Chunks",tuple(m)))
   self.ch=ch
   self.curr_chunk=0
   self.loadText(ch[0],ignore)
   self.display()
   return 1

 def chunk(self,p,ignore=False):
  self.ch[self.curr_chunk]=self.getText()
  self.curr_chunk=p
  self.loadText(self.ch[p],ignore)
  self.display()

 def bind(self,fnstr,fn,args=[]):
  if not fnstr in self.bindable:return
  setattr(self,fnstr,fn)
  setattr(self,fnstr+"_args",args)

 def on(self,fnstr,*args):
  fn=getattr(self,fnstr)
  args=list(args)
  args.extend(getattr(self,fnstr+"_args"))
  return fn(*args)

 def readFile(self,fh,n='',ignore=False):
  try:
   self.t.clear()
   self.name=n
   self.loadText(fh.read(),ignore)
   fh.close()
   self.display()
   return 1
  except BinaryError,e:
   self.on('error',e)
  except SymbianError, e:
   if e.errno==-4:
    return self.chunks(fh,n,ignore)
   else:
    self.on('error',e)
  if not fh.closed:fh.close()

 def toTop(self):self.t.set_pos(0)
 def toBottom(self):self.t.set_pos(len(self.t.get()))
 def toLine(self,num=0):
  lines=self.getText().split('\r\n')
  num=num or appuifw.query(u'Goto line (1-%s)'%(len(lines)),'number',1)
  if not num:return [None]
  line=lines[num-1:]
  if not line:appuifw.note(u'Line number not in range','error');return [None]
  remaining_str=u'\u2029'.join(line)
  index=self.t.get().index(remaining_str)
  self.t.set_pos(index)
  return line
 def linecol(self):
  line,col=appuifw.multi_query(u'Line',u'Column') or (None,None)
  try:
   line=int(line)
   col=int(col)
  except:
   if line:appuifw.note(u'Line & column must be integers','error')
   return False
  line=self.toLine(line)[0]
  if not line:return False
  index=line[col:]
  if index:
   self.t.set_pos(self.t.get_pos()+col)
 def build_search(self,arr,s,key):
  try:ind=s.index(key,arr[len(arr)-1]+1)
  except ValueError:return arr[1:] or None
  arr.append(ind)
  return self.build_search(arr,s,key)
 def find(self,pretext='',string=''):
  if 'f' in dir(self) and not pretext:pretext=self.f
  if not string:string=appuifw.query(u'Find text','text',pretext)
  if not string:return
  self.f=string
  self.f_ind=self.build_search([0],self.t.get(),string)
  if self.f_ind:
   self.f_curr=0
   self.t.set_pos(self.f_ind[self.f_curr])
  else:
   if appuifw.query(u'Not found. Retry?','query'):
    self.find(string)
 def nav_find(self,d,onEnd):
  if not 'f_ind' in dir(self):self.find();return  
  if not self.f_ind:self.find();return
  if d=='next':self.f_curr+=1
  if d=='prev':self.f_curr=self.f_curr-1
  try:pos=self.f_ind[self.f_curr]
  except:
   onEnd()
   return
  self.t.set_pos(pos)
 def next(self):
  def ask():
   if appuifw.query(u'Reached the end, restart search?','query'):
    self.f_curr=-1
    self.next()
    return
  self.nav_find('next',ask)
 def prev(self):
  def ask():
   if appuifw.query(u'Reached the beginning, return to last occurence?','query'):
    self.f_curr=len(self.f_ind)
    self.prev()
  self.nav_find('prev',ask)
 def replace(self,limit=1,rep=None):
  if not rep:rep=appuifw.multi_query(u'Replace',u'With')
  if not rep:return
  self.r=rep
  t=self.t.get()
  t=t.replace(rep[0],rep[1],limit)
  self.t.set(t)
  self.r_ind=self.build_search([0],t,rep[1])
  if self.r_ind:
   self.t.set_pos(self.r_ind[-1])
 def replace_next(self):
  if 'r' in dir(self):self.replace(1,self.r)
  else:self.replace()
 def display(self):
  appuifw.app.body=self.t
  appuifw.app.menu=self.menu
  appuifw.app.exit_key_handler=self.askSave
 def shutdown(self):
  exit=self.exit;exit_args=self.exit_args
  self.default()
  self.t.clear()
  self.t.set(u"Exiting, please wait...")
  try:del self.orig,self.type
  except:pass
  exit(*exit_args)
  self.default()
 def saveFile(self):
  self.saveText(lambda f:self.on('save',f))
  self.orig=self.getText()
 def askSave(self):
  if self.orig !=self.getText():
   if appuifw.query(u'Save?','query'):self.saveFile()
  self.shutdown()
 def saveAs(self):
  fields=[(u'File Name','text',unicode(self.name)),(u'Encoding','combo',([u'UTF-8',u'UTF-16'],0))]
  form=appuifw.Form(fields,17)
  form.execute()
  namefield=form[0]
  if not len(namefield)==3:return
  encoding=form[1][2][0][form[1][2][1]]
  self.type=encoding.replace('-','').lower()
  self.on('saveas',namefield[2],self.saveText())
  self.orig=self.getText()
 def settings(self):
  def redirect():
   c=appuifw.app.body.current()
   if c==0: self.textsettings()
   elif c==1:self.advancedsettings()
  options=[
   (u'Text Settings',u'Change how text is displayed'),
   (u'Editor Settings',u'Change how the editor behaves')
  ]
  lb=appuifw.Listbox(options, redirect)
  appuifw.app.body=lb
 def textsettings(self):
  current=self.css(getcss=1)
  opts=[]
  for k in current:
   opts.append((unicode(k),'text',unicode(current[k])))
  f=appuifw.Form(opts,17)
  f.menu=[(u'Add css',lambda:None)]
  f.save_hook=self.read_form
  f.execute()
  self.display()
 def read_form(self, form):
  options=[v[2] for v in form]
  new={}
  new['color']=tuple([int(x) for x in options[0].split(",")])
  new['font']=(options[1],int(options[2]),int(options[3]))
  new['chunkbytes']=int(options[4])
  self.on("save_settings",new)
  self.refresh()
 def refresh(self):
  self.style()
  self.t.set(self.t.get())

 def rgb(self, r,g,b):
  return int("0x%d%d%d"%(r,g,b),16)
 def rgb2(self,r,g,b):
  def add0(n):
   if len(n)==1:return '0'+n
   return n
  return int('0x%s'%''.join([add0(hex(i)[2:]) for i in [r,g,b]]),16)

 def curr2internal(self):
  return {'style':self.t.style,'font':list(self.t.font),'color':self.rgb2(*self.t.color),'text':'','highlight_color':self.rgb2(*self.t.highlight_color)}

 def css(self,css={},**kw):
  if not 'method' in kw:kw['method']='inherit'
  meth=kw['method']
  if meth=='plain':internal={
   'style':0,
   'font':[None,None,16],
   'color':0,
   'highlight_color':0,
  }
  elif meth=='default':internal=self.css(self.on('text_properties'),method='plain')
  elif meth=='inherit':internal=self.curr2internal()
  else: raise AttributeError('invalid method to apply css')
  if 'text' in kw:internal['text']=kw['text']
  inter_keys=['font','style','color','highlight_color','text']
  current=self.curr2internal()
  for k in inter_keys:
   if not k in internal:internal[k]=current[k]
  def lam_if(a,o,b,t=1,f=0):
   if eval("%s%s%s"%(repr(a),o,repr(b))):return t
   else:return f
  bulkwith=lambda b,c,s:b.join(['' for x in range(c+1)])+s
  color2int=lambda c:int(c.replace("#","0x"),16)
  def int2color(i):
   h=hex(i).replace('0x','')
   return '#'+bulkwith('0',6-len(h),h)
  uifw=lambda v:getattr(appuifw,"STYLE_"+v.upper())
  all_properties={
   'font-family':{'access':[0,0],'operates':'=',
    'do':lambda v:unicode(v),
    'undo':lambda v:str(v)},
   'font-size':{'access':[0,1],'operates':'=',
    'do':lambda v:int(v),
    'undo':lambda v:str(v)},
   'font-flags':{'access':[0,2],'operates':'|=',
    'do':lambda v:int(v),
    'undo':lambda v:str(v)},
   'font-style':{'access':1,'operates':'|=',
    'do':lambda v:lam_if(v,"==","italic",uifw('italic')),
    'undo':lambda v:lam_if(v&uifw('italic'),'>','0','italic','')},
   'font-weight':{'access':1,'operates':'|=',
    'do':lambda v:lam_if(v,"==","bold",uifw('bold')),
    'undo':lambda v:lam_if(v&uifw('bold'),'>','0','bold','')},
   'text-decoration':{'access':1,'operates':'|=','multi':1,
    'do':lambda v:
     lam_if(v,"==","underline",uifw('underline'),
      lam_if(v,"==","line-through",uifw('strikethrough'))),
      'undo':lambda v:' '.join([lam_if(v&uifw(l[0]),'!=',0,l[1],'') for l in [['underline','underline'],['strikethrough','line-through']]])},
   'text-shadow':{'access':{'p':3,1:["|=",lambda:appuifw.HIGHLIGHT_SHADOW]},'operates':'=',
    'do':lambda v:color2int(v),
    'undo':lambda v:lam_if(internal['style']&appuifw.HIGHLIGHT_SHADOW,'>',0,int2color(v),'')},
   'text-transform':{'access':4,'operates':'=',
    'do':lambda v:
     lam_if(v,"==",'capitalize',
      " ".join([word.capitalize() for word in internal['text'].split(" ")]),
      lam_if(v,'==','lowercase',internal['text'].lower(),
       lam_if(v,'==','uppercase',internal['text'].upper(),internal['text']))),
       'undo':lambda v:internal['text']},
   'color':{'access':2,'operates':'=',
    'do':lambda v:color2int(v),
    'undo':lambda v:int2color(v)},
   'background':{'access':{'p':3,1:["|=",lambda:appuifw.HIGHLIGHT_STANDARD]},'operates':'=',
    'do':lambda v:color2int(v),
    'undo':lambda v:lam_if(internal['style']&appuifw.HIGHLIGHT_STANDARD,'>',0,int2color(v),'')}
  }
  im=inter_keys
  for prop,opts in all_properties.iteritems():
   ac=opts['access']
   s_ac="";cmd=""
   if type(ac)==list:
    p_ac=im[ac[0]]
    for i in ac[1:]:
     s_ac+="[%s]"%i
   elif type(ac)==dict:
    p_ac=im[ac['p']]
    del ac['p']
    for f in ac:
     cmd+="internal['%s']%s%s;"%(im[f],ac[f][0],ac[f][1]())
   else:
    if ac<len(im):p_ac=im[ac]
    else:p_ac=""
   if prop in css:
    cmd+="internal['%s']%s%s"%(p_ac,s_ac,opts['operates'])
    if 'multi' in opts:
     for value in css[prop].split(" "):
      res=repr(opts['do'](value))
      exec cmd+res in locals()
    else:
     res=repr(opts['do'](css[prop]))
     exec cmd+res in locals()
   elif 'getcss' in kw:
    res=eval("opts['undo'](internal['%s']%s)"%(p_ac,s_ac))
    if res.strip():css[prop]=res
  if 'apply' in kw:
   self.internal2curr(internal)
   return unicode(internal['text'])
  elif 'getcss' in kw:
   return css
  else:return internal
 def internal2curr(self,internal):
  self.t.font=tuple(internal['font'])
  self.t.color=internal['color']
  self.t.highlight_color=internal['highlight_color']
  try:self.t.style=internal['style']
  except TypeError, e:
   if e.args[0]=='Valid combination of flags for highlight style is expected':raise TypeError("Cannot set both shadow and background")

 def loadPackage(self, pack):
  if 'css' in pack:css=pack['css']
  else:css=self.css(getcss=1)
  txt=self.css(css,apply=1,text=pack['text'])
  self.t.add(txt)