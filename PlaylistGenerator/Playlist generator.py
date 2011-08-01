import appuifw, e32
items=[u'New Playlist', u'Open Playlist']
def main():
    if menu.current()==0:
        add_list()
    elif menu.current()==1:
        open()

def quit():
    app_lock.signal()


def disp_menu():
    appuifw.app.exit_key_handler=quit
    appuifw.app.body=menu
    appuifw.app.title=u'Playlist Generator'
    appuifw.app.menu=[(u'Exit', quit)]


menu=appuifw.Listbox(items, main)
disp_menu()
files=[u'Add']


def compile():
    sure=appuifw.query(u'Are you Sure?', 'query')
    if sure==1:
        appuifw.app.body=None
        name=appuifw.query(u'Please enter a filename', 'text')
        if name==None:
            name='unnamed'
        appuifw.note(u'Proccessing...')
        del(files[0])
        m3u='\n'.join(map(str, files))
        location=u"e:\\sounds\digital\playlists/"+name+u".m3u"
        playlist=file(location, 'w')
        playlist.write("#M3U\n"+m3u+"\n")
        playlist.close()
        appuifw.note(u'Done!', 'conf')
        disp_menu()
def add():
    file_loc=appuifw.query(u'File Location', 'text')
    if file_loc:
        try:
            file(file_loc)
            files.append(file_loc)
            appuifw.app.menu=[(u'Done', compile),(u'Exit', quit)]
            add_list(selected.current())
        except IOError, reason:
            if reason.errno==2:
                appuifw.note(u'The file "'+file_loc+'" does not exist!', 'error')
    else:
        pass
def ref():
    selected=appuifw.Listbox(files, menu_callback)
    return selected
def add_list(curr=0):
    appuifw.app.exit_key_handler=disp_menu
    appuifw.app.body=ref()#+appuifw.Listbox([u'hello'], menu_callback)
def menu_callback(curr=0):
    item_selected=curr#ref().current()
    if item_selected==0:
        add()
    else:
        appuifw.popup_menu([u'Delete',u'Replace'],u'Options')
selected=appuifw.Listbox(files, menu_callback)

def open(location=''):
    appuifw.app.exit_key_handler=disp_menu
    location=appuifw.query(u'File location', 'text', location)
    if location:
        try:
            if location.rfind(".m3u")==-1:
                appuifw.note(u'Not a valid playlist!', 'error')
                open(location)
            else:
                f=file(location, 'r')
                files.extend(f.read().split(u'\n'))
                del(files[1])
                files.pop()
                add_list(selected.current())
                f.close()
        except IOError, reason:
            if reason.errno==2:
                appuifw.note(u"Playlist doesn't exist!", 'error')
                open(location)
    else:
        appuifw.app.exit_key_handler=quit
app_lock=e32.Ao_lock()
app_lock.wait()