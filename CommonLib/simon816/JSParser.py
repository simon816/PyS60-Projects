from simon816.Parser import *
p=parser()
p.set_keywords(['as', 'break', 'case', 'catch', 'continue', 'decodeURI', 'delete', 'do', 'else', 'encodeURI', 'eval', 'finally', 'for', 'if', 'in', 'is', 'item', 'instanceof', 'return', 'switch', 'this', 'throw', 'try', 'typeof', 'void', 'while', 'write', 'with', 'class', 'const', 'default', 'debugger', 'export', 'extends', 'false', 'function', 'import', 'namespace', 'new', 'null', 'package', 'private', 'protected', 'public', 'super', 'true', 'use', 'var', 'alert', 'back', 'blur', 'close', 'confirm', 'focus', 'forward', 'home', 'name', 'navigate', 'onblur', 'onerror', 'onfocus', 'onload', 'onmove', 'onresize', 'onunload', 'open', 'print', 'prompt', 'scroll', 'status', 'stop'])
p.add_pattern(COMMENT,'comment')
p.add_pattern(QUOTE,'string')
p.add_pattern(re.compile('([a-zA-Z_]+[0-9a-zA-Z]*)\s*='),'variable')
p.add_pattern(NUMBER,'number')
p.add_pattern(SYMBOLS, 'symbol')
p.set_default_text_name('plaintext')
p.set_default_keyword_name('keyword_css')
def var_search(m,index):
  s=m.start()
  index[s]=('variable',len(m.group(1))+s)
  index[m.end()-1]=('symbol',m.end())
p.add_search_handle('variable',var_search)
def parse_js(js):
  return p.parse(js)
__all__=['parse_js']
if __name__=='__main__':
  JS=r"""function hello () {
var t ="qwerty";
alert(t)
}
"""

  ps=parse_js(JS)
  for e in ps:
    print e
