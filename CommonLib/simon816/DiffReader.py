import re,simon816.text,e32

class DifferenceReader:

 def __init__(self):
  self.settings={
   'lineno':0,
   'deletecss':{'background':'#FFAAAA'},
   'insertcss':{'background':'#AAFFAA'},
   'equalcss':{'background':'#EEEEEE'},
   'linecoordcss':{'color':'#808080'},
   'filenamecss':{'font-weight':'bold','font-size':'16'}
   }

 def displayDifference(self,difftext):
  """does everything: parses diff, reads parsed diffs and displays using default settings"""
  self.textobj=self._createTextObj()
  if difftext.startswith('---'):
    difftext='diff --git\r\n\r\n'+difftext
  if difftext.startswith('diff --git'):
   files = self.parseMultiDifference(difftext)
  else:
   files=[{'lines':difftext,'oldname':'','newname':''}]
  for file in files:
   self._setcss('filename')
   if file['newname']!=file['oldname']:
    self.textobj.add(file['oldname']+' => ')
   if file['newname']:
    self.textobj.add(file['newname']+'\n')
   differences=self.parseDifference(file['lines'])
   self.setTextToDiff(differences,self.textobj)
  self._lockThreadAndDisplay()

 def parseDifference(self,difftext):
  """returns list/iterator of a diff text"""
  if type(difftext) == unicode:
   difftext = difftext.encode("ascii")
  patches = []
  if not difftext:return patches
  if type(difftext) is not list:
   text = difftext.splitlines()
  else:text=difftext
  while len(text) != 0:
   m = re.match("^@@ -(\d+),?(\d*) \+(\d+),?(\d*) @@", text[0])
   if not m:
    raise ValueError("Invalid patch string: " + text[0])
   def intOR1(v):
     try:return int(v)
     except:return 1
   s=map(intOR1, [m.group(1),m.group(3)])
   l=map(intOR1, [m.group(2),m.group(4)])
   patch = patch_obj(text[0],s+l)
   patches.append(patch)
   del text[0]
   while len(text) != 0:
    if text[0]:
     sign = text[0][0]
    else:
     sign = ''
    try:line = text[0][1:].decode("utf-8")
    except:line=text[0][1:].__repr__()
    if sign == '+':
     patch.append('insert', line)
    elif sign == '-':
     patch.append('delete', line)
    elif sign == ' ':
     patch.append('equal', line)
    elif sign == '@':
     break
    elif sign == '':
     pass
    else:
     raise ValueError("Invalid patch mode: '%s'\n%s" % (sign, line))
    del text[0]
  return patches

 def parseMultiDifference(self,multidiff):
  """returns list of file dictionarys on a multi difference text made by git diff"""
  text=multidiff.splitlines()
  i=-1
  files=[]
  while i<len(text)-1:
   i+=1
   if not text[i].startswith('diff --git'):
    files[-1]['lines'].append(text[i])
   else:
    i+=1
    action=text[i].split(' ')
    if action[0]=='index':
     action=''
    else:
     i+=1
    index=text[i]
    i+=1
    if text[i].startswith('---'):
     oldname=text[i][5:]
     newname=text[i+1][5:]
     i+=1
    elif text[i].startswith('Binary files'):
     newname=text[i]
     oldname=''
    else:
     newname=oldname=''
    files.append({
     'lines':[],
     'newname':newname,
     'oldname':oldname,
     'action':action,
      'index':index
    })
  return files

 def displayDiffObj(self,diffs):
  """creates new simon816.text.text instance, locks the main thread and replaces appuifw.app with difference text"""
  textobj=self._createTextObj()
  self.setTextToDiff(diffs,textobj)
  self._lockThreadAndDisplay()

 def _createTextObj(self):
  t=simon816.text.text()
  t.saveallowed=0
  def add(text):
   t.t.add(t.toUnicode(text))
  t.add=add
  t.bind('get_text_css',lambda:{'font-antialias':'on','font-size':'10'})
  def delete(pos):
    t.t.delete(pos,1)
  def onclick(code,prop):
   if prop[1]=='+':
     pass #zoom in
     t.t.clear()
     css=t.css(getcss=1)
     css['font-size']=str(int(css['font-size'])+1)
     t.css(css,apply=1,method='plain')
     self.textAddDiffObj(self.dfoj)
   elif prop[1]=='-':
    pass #zoom out
   pos=t.t.get_pos()
   if prop[0]=='backspace':t.add(' ')
   elif prop[0]=='ctrl':pass
   else:e32.ao_sleep(0,lambda:delete(pos))
  t.bind('key',onclick)
  bdy=simon816.text.appuifw.app.body
  x=simon816.text.appuifw.app.exit_key_handler
  def ex():
    simon816.text.appuifw.app.body=bdy
    simon816.text.appuifw.app.exit_key_handler=x
  t.bind('exit',ex)
  return t

 def _lockThreadAndDisplay(self):
  lock=e32.Ao_lock()
  exit,exit_args=self.textobj.exit,self.textobj.exit_args
  def onclose():
    lock.signal()
    exit(*exit_args)
  self.textobj.bind('exit',onclose)
  self.textobj.display()
  lock.wait()

 def textAddDiffObj(self,diffs):
  self.dfoj=diffs
  for diffobj in diffs:
   coord=diffobj.get_coord_str()
   if not coord.endswith('\n'):
     coord+='\n'
   self._setcss('diffhead')
   lineno=self.settings['lineno']
   self.textobj.add(' ...| '*lineno+coord)
   for difference in diffobj:
    linenumber,oldline,newline,type,line=difference
    text=''
    if lineno==1:
     text+='%3s'%(str(linenumber))+'|'
    elif lineno==2:
     text+='%3s'%(str(oldline))+'|'
     text+='%3s'%(str(newline))+'|'
    text += line
    self._setcss(type)
    self.textobj.add(text+'\n')

 def _setcss(self,type):
  if type=='diffhead':
   css=self.settings['linecoordcss']
  elif type=='delete':
   css=self.settings['deletecss']
  elif type=='insert':
   css=self.settings['insertcss']
  elif type=='equal':
   css=self.settings['equalcss']
  elif type =='filename':
   css=self.settings['filenamecss']
  else:
   css={}
  self.textobj.css(css,method='default',apply=1)

 def setTextToDiff(self,diffs, textobj):
  """sets the active intstance of simon816.text.text to the differences"""
  self.textobj=textobj
  self.textAddDiffObj(diffs)

 def changeSetting(self,setting,value):
  """changes the setting `setting` to `value`
  settings are:
   lineno:
    0 no line numbers are added
    1 modified and final line numbers are added
    2 2 colums, line before, line after
  deletecss,equalcss,insertcss,linecoordcss,filenamecss:
   dictionary of css
  """
  if setting in self.settings:
   self.settings[setting]=value
  else:
   raise KeyError('Cannot set setting: '+setting)


class patch_obj:
  def __init__(self,coordstr,coordtup):
    self.diffs = []
    self.coordstr=coordstr
    self.coords=coordtup
    self.line_index=coordtup[0]
    self.oldline=coordtup[0]
    self.newline=coordtup[0]
  def append(self,type,line):
    a=b=''
    if type=='delete':
      self.oldline+=1
      a=self.oldline
    elif type=='equal':
      self.oldline+=1
      self.newline+=1
      a=self.oldline
      b=self.newline
    elif type=='insert':
      self.newline+=1
      b=self.newline
    self.diffs.append((self.line_index,a,b,type,line))
    if type != 'delete':
     self.line_index+=1
  def get_diff(self,index):
    if index < len(self.diffs):
     return self.diffs[index]
    else:
     return []
  def get_diffs(self):
    return self.diffs
  def get_coord_str(self):
   return self.coordstr
  def __iter__(self):
    self.iterline=-1
    return self
  def next(self):
   self.iterline+=1
   try:return self.diffs[self.iterline]
   except IndexError:raise StopIteration

if __name__=='__main__':
  dr=DifferenceReader()
  dr.changeSetting('lineno',2)
  dr.displayDifference('@@ -1 +1 @@\n+ Hello')
  #files=dr.parseMultiDifference(diff)
  #dr.displayDifference('\n'.join(files[4]['lines']))