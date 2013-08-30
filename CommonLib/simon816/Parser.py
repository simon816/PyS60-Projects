import re
QUOTE=re.compile(r'(?<!\\)(?:\\\\)*("|\')((?:\\.|(?!\1)[^\\])*)\1',re.S)
COMMENT=re.compile('(//.*?\n)|(/\*.*?\*/)',re.S)
SYMBOLS=re.compile('[!@%&\|=\-+\*<>()\[\]{}]+')
NUMBER=re.compile('(?<![\w])[0-9]+(?![\w])')
class parser:
  def __init__(self):
    self.regex=[]
    self.keywords=[]
    self.handles={}
    self.deftext='DEFAULT'
    self.kwtext='WORD'
  def set_default_text_name(self,name):
    self.deftext=name
  def set_default_keyword_name(self,name):
    self.kwtext=name
  def add_pattern(self,pattern,label):
    self.regex.append((pattern,label))
  def add_keyword(self,word):
    self.keywords.append(word)
  def set_keywords(self,words):
    self.keywords=words
  def add_search_handle(self,label,function):
    self.handles[label]=function
  def parse(self,text):
    if type(text)==unicode:
      text=text.encode('utf8')
    index={}
    dontsearch=[]
    for matcher in self.regex:
      regex,label=matcher
      try:
        m=regex.search(text)
      except RuntimeError,e:
        print e,'while searching for',label
        m=None
      while m:
        e=m.end()
        s=m.start()
        if text[e-1]=='\n':e-=1
        if not s in dontsearch:
          dontsearch.extend(range(s,e))
          if label in self.handles:
            s=self.handles[label](m,index)
            if s is None:
              continue
          index[s]=(label,e,m.groups())
        try:
          m=regex.search(text,e)
        except RuntimeError,er:
          print er,'while searching for',label
          m=None
    for w in self.keywords:
      for o in re.finditer('\\b'+w+'\\b',text):
        if not o.start() in dontsearch:
          index[o.start()]=(self.kwtext,o.end())
    k=index.keys()
    k.sort()
    y=0
    i2=[]
    for i in k:
      if y<i:
        i2.append((self.deftext,text[y:i]))
      x=index[i]
      i2.append((x[0],text[i:x[1]]))
      y=x[1]
    if y!=len(text):
      i2.append((self.deftext,text[y:]))
    return i2
