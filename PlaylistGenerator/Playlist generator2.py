import appuifw, e32, os
from simon816 import util
items=[u'New Playlist', u'Open Playlist']
def main():
    if menu.current()==0:
        files=[u'Add']
        add_list()
    elif menu.current()==1:
        open_m3u()

def quit():
    app_lock.signal()

files=[u'Add']
def disp_menu():
    files=[u'Add']
    appuifw.app.exit_key_handler=quit
    appuifw.app.body=menu
    appuifw.app.title=u'Playlist Generator'
    appuifw.app.menu=[(u'Exit', quit)]


menu=appuifw.Listbox(items, main)
disp_menu()


def compile():
    sure=appuifw.query(u'Are you Sure?', 'query')
    if sure==1:
        appuifw.app.body=None
        name=appuifw.query(u'Please enter a filename', 'text')
        if name==None:
            name='unnamed'
        appuifw.note(u'Proccessing...')
        del(files[0])
        m3u='\n'.join(files)
        location=u"e:\\sounds\digital\playlists/"+name+u".m3u"
        playlist=open(location, 'w')
        playlist.write('\xef\xbb\xbf'+("#M3U\n"+m3u+"\n").encode('utf8'))
        playlist.close()
        appuifw.note(u'Done!', 'conf')
        disp_menu()
last='\\Videos\\My Videos\\MCMV'
def add(pos=0):
    global last
    file_loc=util.select('file',last,'E:',extwhitelist=["mp3","mp4","3gp","mid","m4a"])
    if file_loc:
        last =os.path.dirname(file_loc)[2:]
        if pos:
            files[pos]=file_loc
        else:
             files.append(file_loc.encode('utf8').decode('utf8'))
        appuifw.app.menu=[(u'Done', compile),(u'Exit', quit)]
        add_list()
        return 1
    else:
        return 0
def ref():
    selected=appuifw.Listbox(files, menu_callback)
    return selected
def sure():
    if appuifw.query(u"Exit without saving?","query"):
        disp_menu()
    else:
        pass

def add_list():
    appuifw.app.exit_key_handler=sure
    appuifw.app.body=ref()
def menu_callback():
    item_selected=appuifw.app.body.current()
    if item_selected==0:
        add()
    else:
        current=appuifw.app.body.current()
        choice=appuifw.popup_menu([u'Delete',u'Replace'],u'Options')
        if choice==0:
            del(files[current])
            add_list()
        elif choice==1:
            add(current)
    selected=appuifw.Listbox(files, menu_callback)

def open_m3u(location=''):
    appuifw.app.exit_key_handler=disp_menu
    location=util.select('file','\\Sounds\Digital\playlists','E:',extwhitelist=["m3u"])
    if location:
        f=file(location, 'r')
        files.extend(f.read().decode('utf8').split(u'\n'))
        del(files[1])
        files.pop()
        add_list()
        f.close()
    else:
        appuifw.app.exit_key_handler=quit
app_lock=e32.Ao_lock()
app_lock.wait()