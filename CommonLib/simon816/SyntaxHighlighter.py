import appuifw
from simon816.ExtendedEditor import ExtendedEditor
from HTMLParser import *#HTMLParser
from simon816.JSParser import parse_js
from simon816.PHPParser import parse_php,p
class HTMLHighlighter(HTMLParser):
 def do_highlighting(self,onstuff,html):
  self.do=onstuff
  self.JS=False
  self.feed(html)
  self.close()

 def apply_tag(self,tagname,attributes=[],end=""):
  if tagname=='script':
   at=dict(attributes)
   if 'type' in at:
    if at['type']=='text/javascript':
     self.JS=True
   elif 'language' in at:
     if at['language']=='javascript':
       self.JS=True
   elif len(attributes)==0:
     self.JS=True
  elif tagname=='/script':
   self.JS=False
  self.do("tag","<"+tagname)
  raw=self.get_starttag_text()[1:-1]
  attrstr=raw[len(tagname)+1:]
  for attr in attributes:
   value=attr[1] is not None
   try:p=attrstr[attrstr.index(attr[0]):] # limit to first val
   except ValueError:p=attrstr #rare chance of not finding
   try:qu=p[:p.index("=")+2][-1:] # find character past '='
   except ValueError:qu='"' # malformed html catch
   if value:attrstr=p[p.index(attr[1])+len(attr[1]):] #shift past vals
   if not qu in ["'",'"']:qu="" #set what quotation to use

   if value:s=u" %s="%attr[0]
   else:s=unicode(" "+attr[0])
   self.do("attr",s)
   if value:
    self.do("attrval",qu+attr[1]+qu)
  self.do("tag",end+">")

 def handle_pi(self,pi):
  self.do("pi","<?"+pi+">")
 def handle_comment(self,comment):
  self.do("comment","<!--"+comment+"-->")
 def handle_decl(self,decl):
  self.do("decl","<!"+decl+">")
 def handle_entityref(self,entity):
  self.do("ent|char","&"+entity+";")
 def handle_charref(self,char):
  self.do("ent|char","&"+char+";")
 def handle_starttag(self,tag,attrs):
  self.apply_tag(tag,attrs)
 def handle_endtag(self,tag):
  self.apply_tag("/"+tag)
 def handle_startendtag(self,tag,attrs):
  self.apply_tag(tag,attrs," /")
 def handle_data(self,data):
  if self.JS:
   for e in parse_js(data):
    self.do(*e)
  else:
   self.do("text",data)
 def unknown_starttag(self,tag,attrs):
  self.handle_starttag(tag,None,attrs)
 def unknown_endtag(self,tag):
  self.handle_endtag(tag,None)
 def unknown_charref(self,char):
  self.handle_entity(char)
  def unknown_decl(self,decl):
   self.handle_decl(decl)
  def unknown_entityref(self, entity):
   self.handle_entityref(entity)

class PHPHighlighter(HTMLHighlighter):
    def handle_php(self,php):
      p=parse_php(php)
      self.do("php","<?php")
      for e in p:
        self.do(*e)
      self.do("php","?>")

class SyntaxHighlighter(ExtendedEditor):
 def highlighter(self):
  self.extend()
  self.keyword('\t',lambda:self.add(' '*self.tabsize))
  # this may go in to ExtendedEditor base class
  self.languages={
   'HTML/XML':{
    'file_types':[".html",".htm",".xml"],
    'css':{
     'tag':{'background': '#FFFFFF', 'color': '#0000FF'},
     'text':{'background': '#FFFFFF', 'color': '#000000', 'font-weight': 'bold'},
     'attr': {'background': '#FFFFFF', 'color': '#FF0000'},
     'attrval':{'background': 'FEFDE0', 'color': 'FF8000'},
     'ent|char':{'font-style':'italic'},
     'pi':{'color':'#FF0000'},
     'decl': {'background': '#A6CAF0', 'color': '#000000'},
     'comment':{'background': '#FFFFFF', 'color': '#008000'}
    },
    'parser':HTMLHighlighter,
    'function':self.open_html,
    'inherits':"Javascript"
   },
   'PHP':{
    'file_types':[".php"],
    'css': {
     'php':{'color':'#FF0000'},
     'keyword':{'font-weight': 'bold', 'background': '#FEFCF5', 'color': '#0000FF'},
     'plain':{'background': 'FEFCF5', 'color': '000000'},
     'variable':{'background': '#FEFCF5', 'color': '#000080'},
     'string': {'background': '#FEFCF5', 'color': '#808080'},
     'comment':{'background': '#FEFCF5', 'color': '#008000'},
     'number': {'background': 'FEFCF5', 'color': 'FF8000'},
     'invar': {'background': 'FEFCF5', 'color': '808080', 'font-weight': 'bold'},
     'operator':{'background': '#FEFCF5', 'color': '#8000FF'}
     },
    'inherits':"HTML/XML",
    'parser':PHPHighlighter,
    'function':self.open_php
   },
   'Javascript':{
    'file_types':[".js", '.java'],
    'css':{
     'plaintext':{},
     'symbol':{'color':'#FF0000'},
     'statement':{'color':'#0000FF'},
     'function':{'color':'#00FF00'},
     'keyword_css':{'color':'#2F11EF','font-style':'italic'},
     'string': {'color':'#808080'},
     'comment':{'color':'#008000'},
     'number': {'color':'#FF8000'},
     'variable':{'color':'#000080'},
    },
    'parser':None,
    'function':self.open_javascript
   },
   'Text':{
    'file_types':["*"],
    'css':{'Plain Text':self.on('get_text_css')},
    'parser':None,
    'function':self.open_text
   }
  }
  def mksw(n):return lambda:self.swtch(self.t.get(),n)
  self.menu.append((u'Language',
   tuple([(unicode(n),mksw(n)) for n in self.languages])
  ))
 def inherit_css(self,lanset,c):
   if 'inherits' in lanset:
     l=self.languages[lanset['inherits']]
     c.update(l['css'])
     return self.inherit_css(l,c)
   return c
 def swtch(self,t, lang,i=False):
  self.clanguage=lang
  settings=self.languages[lang]
  self.ignore=i
  """
  if 'inherits' in settings:
   settings['css']=dict(
    self.languages[
     settings['inherits']
     ]['css'].items()+settings['css'].items()
    )
  """
  settings['css']=self.inherit_css(settings,settings['css'])
  self.t.clear()
  settings['function'](t,settings['css'],settings['parser'])
  self.orig=self.getText()

 def open_text(self,t,css,parser):
  self.css(css,method='default',apply=1)
  self.add(t,self.ignore)

 def apply_css(self, css, key, value):
  self.css(css[key],method='plain',apply=1)
  try:self.add(value,self.ignore)
  except SymbianError, e:
   if e.errno==-4:print 'file too big!'
   else:raise

 def open_html(self,html,css,p):
  apply=lambda k,v:self.apply_css(css,k,v)
  p().do_highlighting(apply,self.toUnicode(html))
  apply('text','')

 def open_php(self,php,css,p):
  apply=lambda k,v:self.apply_css(css,k,v)
  p().do_highlighting(apply,self.toUnicode(php))
  apply('text','')

 def open_javascript(self,js,css,p):
  apply=lambda k,v:self.apply_css(css,k,v)
  p=parse_js(js)
  for a in p:
    apply(*a)

# overrides
 def loadText(self, t, ignore=False):
  ext='.'+self.name.split(".")[-1]
  l=None;stars=[];all_langs=self.languages
  for lang in all_langs:
   if ext in all_langs[lang]['file_types']:l=lang
   if '*' in all_langs[lang]['file_types']:stars.append(lang)
  if not l:l=stars[0]
  self.swtch(t,l,ignore)
 def textsettings(self):
  self.lanmenu=[unicode(l) for l in self.languages]
  appuifw.app.body=appuifw.Listbox(self.lanmenu,self.languagesettings)
  appuifw.app.exit_key_handler=self.settings
  appuifw.app.menu=[(u'Select',self.languagesettings),(u'Back',self.settings)]
 def languagesettings(self):
  appuifw.app.menu=[(u'Select',self.langpropcss),(u'Back',self.textsettings)]
  self.csses=self.languages[self.lanmenu[appuifw.app.body.current()]]['css']
  appuifw.app.exit_key_handler=self.textsettings
  self.lanmenu=[unicode(n) for n in self.csses]
  appuifw.app.body=appuifw.Listbox(self.lanmenu,self.langpropcss)
 def langpropcss(self):
  prop=self.lanmenu[appuifw.app.body.current()]
  css=self.csses[prop]
  if css=={}:
   appuifw.note(u'Currently no CSS settings','info')
   k,v=self.availcss(css)
   css[k]=v
  self.cssSettings(css,
   lambda f:None)
if __name__=='__main__':
  import e32,StringIO
  lock=e32.Ao_lock()
  editor=SyntaxHighlighter()
  editor.highlighter()
  s=StringIO.StringIO()
  s.write("<html>\n<?php\nfunction test($var='test') {\n//comment\nprint($var);\n/*\n  comment\n  block\n*/\necho \"hello \\\"w\\\\orl'd'\\\"\";\nprint \"\\$qwerty\";\nreturn new Test($var,9000);\n}\n?>\n<p style='display:none'>\ntext\n</p>\n<script>print \"hi\";</script></html>")
  s.seek(0)
  editor.readFile(s,"test.php")
  editor.bind("exit",lock.signal)
  editor.inherit_indent()
  k=editor.key
  def kp(code,inf):
    k(code,inf)
    if inf[0]=='backspace' or inf[0]=='enter':
      return
    def evaluate(pos):
      l=editor.get_current_line()
      editor.t.delete(p-len(l)+1,len(l))
      s=editor.languages[editor.clanguage]
      pp=parse_php(l)
      for e in pp:
        editor.apply_css(s['css'],*e)
      #editor.add(l)
    p=editor.t.get_pos()
    e32.ao_sleep(0,lambda:evaluate(p))
  #editor.key=kp
  def kw(w):
    editor.t.delete((editor.t.get_pos()-len(w))+1,len(w)-1)
    s=editor.languages[editor.clanguage]
    editor.apply_css(s['css'],'keyword',w[:-1])
    editor.apply_css(s['css'],'text','')
  for k in p.keywords:
    editor.keyword(k,kw,k)
  editor.display()
  lock.wait()