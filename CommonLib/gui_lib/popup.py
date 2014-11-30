try:
    import appuifw2 as appuifw
except ImportError:
    import appuifw

#__all__ = ['Popup']

class Popup:

    def alert(text):
        appuifw.note(unicode(text), 'info')
    alert = staticmethod(alert)

    def success(text):
        appuifw.note(unicode(text), 'conf')
    success = staticmethod(success)

    def error(text):
        appuifw.note(unicode(text), 'error')
    error = staticmethod(error)

    def prompt(label, initial=''):
        return appuifw.query(unicode(label), 'text', unicode(initial))
    prompt = staticmethod(prompt)

    def hidden(label, initial=''):
        return appuifw.query(unicode(label), 'code', unicode(initial))
    hidden = staticmethod(hidden)

    def prompt2(label1, label2):
        return appuifw.multi_query(unicode(label1), unicode(label2))
    prompt2 = staticmethod(prompt2)

    def confirm(label):
        return appuifw.query(unicode(label), 'query')
    confirm = staticmethod(confirm)

    def menu(items, label=u''):
        return appuifw.popup_menu(map(unicode, items), unicode(label))
    menu = staticmethod(menu)

    def menu2(items, label=u''):
        return appuifw.popup_menu(map(lambda item:
                                      (unicode(item[0]), unicode(item[1])), items),
                                  unicode(label))
    menu2 = staticmethod(menu2)
