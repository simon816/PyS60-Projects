import appuifw
from simon816.ExtendedEditor import ExtendedEditor
from HTMLParser import *#HTMLParser
from simon816.jsparser import JSParser
class HTMLHighlighter(HTMLParser):
 def do_highlighting(self,onstuff,html):
  self.do=onstuff
  self.feed(html)
  self.close()

 def apply_tag(self,tagname,attributes=[],end=""):
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

class JSHighlighter(JSParser):
 def __init__(self,do):
  self.do=do
 def handle_data(self,data):
  self.do('text',data)
 def handle_symbol(self,symbol):
  self.do('symbol',symbol)
 def handle_statement(self,statement):
  self.do('statement',statement)
 def handle_function(self,function):
  self.do('function',function)

class PHPHighlighter(HTMLHighlighter):
    def handle_php(self,php):
     self.do("php","<?php"+php+"?>")

class SyntaxHighlighter(ExtendedEditor):
 def highlighter(self):
  self.extend()
  self.languages={
   'HTML/XML':{
    'file_types':[".html",".htm",".xml"],
    'css':{
     'tag':{'color':'#1100DF'},
     'text':{'font-weight':'bold'},
     'attr':{'color':'#EE1111'},
     'attrval':{'color':'#4F4F4F'},
     'ent|char':{'font-style':'italic'},
     'pi':{'color':'#FF0000'},
     'decl':{'color':'#111111','background':'#D0D0FF'},
     'comment':{'color':'#207F20'}
    },
    'parser':HTMLHighlighter,
    'function':self.open_html
   },
   'PHP':{
    'file_types':[".php"],
    'css': {
     'php':{'color':'#FF0000'}
    },
    'inherits':"HTML/XML",
    'parser':PHPHighlighter,
    'function':self.open_php
   },
   'Javascript':{
    'file_types':[".js.test"],
    'css':{
     'text':{},
     'symbol':{'color':'#FF0000'},
     'statement':{'color':'#0000FF'},
     'function':{'color':'#00FF00'},
     'keyword_css':{'color':'#2F11EF','font-style':'italic'}
    },
    'parser':JSHighlighter,
    'function':self.open_javascript
   },
   'Text':{
    'file_types':["*"],
    'css':{},
    'parser':None,
    'function':self.open_text
   }
  }
  def mksw(n):return lambda:self.swtch(self.t.get(),n)
  self.menu.append((u'Language',
   tuple([(unicode(n),mksw(n)) for n in self.languages])
  ))
 def swtch(self,t, lang,i=False):
  settings=self.languages[lang]
  self.ignore=i
  if 'inherits' in settings:
   settings['css']=dict(
    self.languages[
     settings['inherits']
     ]['css'].items()+settings['css'].items()
    )
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

 def open_php(self,php,css,p):
  apply=lambda k,v:self.apply_css(css,k,v)
  p().do_highlighting(apply,self.toUnicode(php))

 def open_javascript(self,js,css,p):
  apply=lambda k,v:self.apply_css(css,k,v)
  p(apply).parse(js)
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

#"""
import e32,StringIO
lock=e32.Ao_lock()
editor=SyntaxHighlighter()
editor.highlighter()
s=StringIO.StringIO()
s.write("<html>text</html>")
s.seek(0)
editor.readFile(s,"test.html")
editor.bind("exit",lock.signal)
editor.inherit_indent()
editor.display()
lock.wait()
#"""