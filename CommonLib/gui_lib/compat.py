"""
appuifw methods passes onto gui_lib
"""

def listbox(items, callback):
    listbox = new Listbox(ListboxType.SINGLE) ## detect type
    for item in items:
        listbox.add_item(item[0]) ## TODO args
    ## TODO callback
    return listbox


def form(items, flags=0):
    pass

