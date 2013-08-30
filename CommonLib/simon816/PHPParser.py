# http://stackoverflow.com/a/431637
from simon816.Parser import *
p=parser()
p.set_keywords(['include','require','include_once','require_once','new','function','return','echo','exit','if','else','elseif','endif','for','while','foreach','class','int','null','true','false','as','fopen','fwrite','fread','fclose','print','print_r','var_dump','header','count','substr','strpos','scandir','serialize','unserialize','file_exists','file_get_contents','[Aa]rray','str_replace','preg_replace_callback','filesize','session_start','dirname','explode','implode','unset','isset','stripslashes','addslashes','curl_init','curl_setopt','curl_getinfo','curl_exec','curl_close','array_push','base64_encode','base64_decode','stripos','strlen'])

p.add_pattern(COMMENT,'comment')
p.add_pattern(QUOTE,'string')
p.add_pattern(re.compile('\$[a-zA-Z_]+[0-9a-zA-Z]*'),'variable')
p.add_pattern(NUMBER,'number')
p.add_pattern(SYMBOLS, 'operator')
p.set_default_text_name('plain')
p.set_default_keyword_name('keyword')
  
def string_variable(m,index):
    s=m.start()
    if m.group(1)=='"':
      off=s
      n=re.compile(r'(?<![\\])\$[a-zA-Z_]+[0-9a-zA-Z]*')
      for invar in n.finditer(m.group(2)):
        os=invar.start()+s+1;oe=invar.end()+s+1
        index[off]=('string',os)
        index[os]=('invar',oe)
        off=oe
      if off!=s:s=off
    return s
p.add_search_handle('string',string_variable)
def parse_php(php):
  return p.parse(php)
__all__=['parse_php']
if __name__=='__main__':
  PHP=r"""include "$root/php.classes/\$h/website.class.php";
// comment here $w, print
$w=new Website();
$str="he
llo";
/* 
bloc
k */
echo unserialize($w);
echo 'hello \'  world';
echo 5;
+=-&@
echo (int) "5";
function abc2()
$w->display_page();"""

  p=parse_php(PHP)
  for e in p:
    print e
