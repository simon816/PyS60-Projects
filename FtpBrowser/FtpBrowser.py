import appuifw, e32, StringIO
from ftplib import FTP
#import unicodedata

f=file('e://python//pass.txt', 'r')
p=unicode(f.read())
f.close()
def exit():
    ftp.quit()
    appuifw.note(u"disconnecting...")
    app_lock.signal()
ftp = FTP('simon816.hostzi.com')
ftp.set_pasv('true')
ftp.login('a6915081', p)
ftp.cwd('public_html')
appuifw.app.exit_key_handler=exit

appuifw.note(unicode(ftp.getwelcome()))
appuifw.app.title=unicode(ftp.pwd())
def getwd(fo):
    f=fo.nlst()
    l=[]
    for a in f:
        if "." in a:
            if a.find(".")==0:
                l.append(unicode(">"+a))
            else:
                l.append(unicode(a))
        else:
            l.append(unicode(">"+a))
    l.sort()
    return l
def cback():
    cback()
list=appuifw.Listbox(getwd(ftp), cback)
appuifw.app.body=list
def back():
    appuifw.app.body=None
    appuifw.app.body=list
    appuifw.app.exit_key_handler=exit
def cback():
    s = lambda s: s.encode('utf-8')
    l=getwd(ftp)
    list=appuifw.app.body
    sel=l[list.current()]
    if sel.find('>')==0:
        dir=sel[sel.find(">")+1:]
        ftp.cwd(dir)
        appuifw.note(u'chaning directory to '+dir)
        appuifw.app.title=unicode(ftp.pwd())
        list=appuifw.Listbox(getwd(ftp), cback)
        appuifw.app.body=None
        appuifw.app.body=list
    else:
        appuifw.app.exit_key_handler=back
        t=appuifw.Text()
        def download(text):
            appuifw.app.title=unicode(sel)
            t.set(unicode(text))
        def save():
            st=t.get()
            output = StringIO.StringIO()
            output.write(s(st.replace(u"\u2029", u'\r\n')))
            output.seek(0)
            try:
                ftp.storbinary('STOR '+sel, output, 1024)
                appuifw.note(u'Saved!')
            except e:
                appuifw.note(unicode(e), 'error')
            output.close()
        ftp.retrbinary('RETR '+sel, download)
        appuifw.app.body=None
        appuifw.app.body=t
        appuifw.app.menu=[(u'Save', save)]
app_lock=e32.Ao_lock()
app_lock.wait()