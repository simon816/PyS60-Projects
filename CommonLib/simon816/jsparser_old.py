symbols=[
        '(', ')', '[', ']', '{', '}',
        '+', '-', '*', '/', '%',
        '!', '@', '&', '|', '^',
        '<', '>', '=',
        ',', ';', '?', ':']
keywords=[            'as', 'break', 'case', 'catch', 'continue', 'decodeURI', 'delete', 'do',
            'else', 'encodeURI', 'eval', 'finally', 'for', 'if', 'in', 'is', 'item',
            'instanceof', 'return', 'switch', 'this', 'throw', 'try', 'typeof', 'void',
            'while', 'write', 'with'
]
statements=[            'class', 'const', 'default', 'debugger', 'export', 'extends', 'false',
            'function', 'import', 'namespace', 'new', 'null', 'package', 'private',
            'protected', 'public', 'super', 'true', 'use', 'var']
functions=[            'alert', 'back', 'blur', 'close', 'confirm', 'focus', 'forward', 'home',
            'name', 'navigate', 'onblur', 'onerror', 'onfocus', 'onload', 'onmove',
            'onresize', 'onunload', 'open', 'print', 'prompt', 'scroll', 'status',
            'stop'
]
class JSParser:
 def __init__(self):
  pass
 def parse(self,js):  
  l=[]
  all=symbols+keywords+statements+functions
  for thing in all:
   nearest=0
   for i in range(js.count(thing)):
    found=js[nearest:].find(thing)
    if found !=-1:
     nearest+=found
     l.append([nearest,thing])
  l.sort()
  index=0
  for k in l:
   if k[0]>index:
    self.handle_data(js[index:k[0]])
    index=k[0]
   if k[1] in symbols:
    self.handle_symbol(k[1])
   elif k[1] in statements:
    self.handle_statement(k[1])
   elif k[1] in functions:
    self.handle_function(k[1])
   index+=len(k[1])
  #handle remaining data
  self.handle_data(js[index:])
 def handle_symbol(self,sy):
  pass
 def handle_statement(self, st):
  pass
 def handle_function(self,fn):
  pass
 def handle_data(self,dt):
  pass