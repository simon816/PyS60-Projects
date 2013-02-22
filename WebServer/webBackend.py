import BaseHTTPServer,os,sys
from mimetypes import guess_type as Ctype, add_type
from urllib import unquote
_stdout=sys.stdout
class out:
    def __init__(self):self.buf=""
    def write(self, buf):self.buf+=buf
    def clear(self):self.buf="";
out=out();
def _print():r=out.buf[:-1];out.clear();return r
add_type("image/jpeg", ".jpg")
add_type("image/png", ".png")
add_type("application/x-font-woff", ".woff")
def findall(text,find):
    index=0;li=list()
    while index<len(text):
        index=text.find(find,index)
        if index==-1:break
        li.append(index)
        index += len(find)
    return li
#####settings#####
IP   = "localhost"
PORT = 8080
htmldir='E:\\App'
index_names=["index", "default"]
index_types=["pyp", "html", "py", "htm"]
##################
class py:
    def __init__(self, s,h,p,a):self.s,self.h,self.p,self.a=s,h,p,a;s.send_header("Content-Type", "text/html");s.end_headers()
    def header(self,key,value):
        self.s.send_response(200)
        self.s.send_header(key, value)
        self.s.end_headers()
    def _parsePY_(self, get,form=None, post=None):
        ##### Bind methods #####
        def header(*args):self.header(*args)
        global _get
        global _POST
        global _form
        _form=form
        _POST=post
        _get=get
        global _SERVER
        _SERVER={"PY_SELF":self.p,
                 "PATH":self.h,
                 "HTTP_HOST":self.a[0],
                 "SERVER_NAME":self.a[0],
                 "DOCUMENT_ROOT":self.h,
                 "SERVER_PORT": self.a[1],
                 "REQUEST_URI":self.s.path,
                 "SCRIPT_NAME": self.p}
        _server=_SERVER
        ####### delete stuff #######
        #self=None
        try:execfile(_server["PATH"]+_SERVER["PY_SELF"])
        except BaseException, e:print type(e).__name__+": "+str(e)

def display(s,path):
    s.send_header("Content-Type", Ctype(htmldir+path, 0)[0])
    s.end_headers()
    data=open(htmldir+unquote(path), 'rb')
    while 1:
        line=data.readline()
        if not line:break
        s.wfile.write(line)
    data.close()

class MyHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    def do_HEAD(s):
        s.send_response(200)
        s.send_header("Content-Type", "text/html")
        s.end_headers()
    def do_GET(s):
        if s.path.find("?")>-1:
            req=s.path.find("?")+1
            path=s.path[:req-1]
        else:req=0;path=s.path
        try:
            if path.endswith("/"):
                for name in index_names:
                    for ext in index_types:
                        if os.path.exists(htmldir+unquote(path)+name+"."+ext):
                            path+=name+"."+ext
            s.send_response(200)
            if path.endswith(".py"):
                sys.stdout=out
                get={}
                if req:
                    for pair in s.path[req:].split("&"):
                        try:
                            key,value=pair.split("=")
                            if key in get.iterkeys():
                                get[key]=[get[key], value]
                            else:get[key]=value
                        except:pass
                py(s,htmldir,unquote(path), (IP,PORT))._parsePY_(get)

                s.wfile.write(_print())
                sys.stdout=_stdout;
            elif path.endswith(".pyp"):
                data=open(htmldir+unquote(path), 'r')
                text=data.read()
                data.close()
                sys.stdout=out
                get={}
                if req:
                    for pair in s.path[req:].split("&"):
                        try:key,value=pair.split("=");get[key]=value
                        except:pass
                fi=findall(text, "<?python")
                i=0
                if fi:
                  for se in fi:
                    off=text.find("?>", se)
                    seg=text[se+9:off]
                    f=open(htmldir+"\\temp.py", 'w');f.write(seg);f.close()
                    if i==0:print text[:se]
                    else:print text[fi[i-1]:se]
                    py(s,htmldir,"/temp.py", (IP,PORT))._parsePY_(get)
                    try:print text[off+2:fi[i+1]]
                    except IndexError: print text[off+3:]
                    i+=1
                  s.wfile.write(_print())
                  sys.stdout=_stdout;
                else:
                    display(s,path)
                try:os.unlink(htmldir+"/temp.py")
                except:pass
            else:
                display(s,path)
        except IOError, e:
            print e
            s.send_error(404)
    def do_POST(s):
        from pprint import pprint
        pprint(vars(s))
        del pprint
        if s.path.find("?")>-1:
            req=s.path.find("?")+1
            path=s.path[:req-1]
        else:req=0;path=s.path
        try:
            if path.endswith("/"):
                for name in index_names:
                    for ext in index_types:
                        if os.path.exists(htmldir+unquote(path)+name+"."+ext):
                            path+=name+"."+ext
                        #s.send_response(200)
                    print path
            if path.endswith(".py"):
                sys.stdout=out
                get={}
                if req:
                    for pair in s.path[req:].split("&"):
                        try:key,value=pair.split("=");get[key]=value
                        except:pass
                post={}
                _post=s.rfile.read()
                if _post:
                    for pair in _post.split("&"):
                        try:key,value=pair.split("=");post[key]=value
                        except:pass
                py(s,htmldir,unquote(path), (IP,PORT))._parsePY_(get,post)
                s.wfile.write(_print())
                sys.stdout=_stdout;
                s.rfile.close()
                s.wfile.close()
            else:display(s,path)
        except IOError, e:
            print e
            s.send_error(404)
if __name__=="__main__":
    server_class=BaseHTTPServer.HTTPServer
    httpd=server_class((IP,PORT), MyHandler)
    httpd.serve_forever()
