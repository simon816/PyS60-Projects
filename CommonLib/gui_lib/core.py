try:
    import appuifw2 as appuifw
except ImportError:
    import appuifw
import e32

class Listenable(object):

    def __init__(self):
        self.listeners = {}

    def add_listener(self, listener):
        if not callable(listener):
            raise TypeError("Listener must be callable")
        self.listeners[listener] = True

    def remove_listener(self, listener):
        del self.listeners[listener]

    def _clear(self):
        # Warning: could cause undesired behaviour
        self.listeners = {}

    def trigger(self, *args, **kwargs):
        for listener in self.listeners.iterkeys():
            try:
                listener(*args, **kwargs)
            except Exception, e:
                import traceback
                traceback.print_exc()

class EventBus(object):
    def __init__(self):
        self.__events = { }

    def post(self, key, *args, **kwargs):
        if key in self.__events:
            self.__events[key].trigger(*args, **kwargs)
        if '*' in self.__events:
            self.__events['*'].trigger(key, *args, **kwargs) # Note the key as first arg

    def subscribe(self, key, listener):
        if key not in self.__events:
            self.__events[key] = Listenable()
        self.__events[key].add_listener(listener)

    def unsubscribe(self, key, listener):
        if key not in self.__events:
            return
        self.__events[key].remove_listener(listener)

    def _unsub_all(self, key):
        if key not in self.__events:
            return
        self.__events[key]._clear()

class ManagedProperty(object):

    def __new__(cls, *args, **kwargs):
        inst = object.__new__(cls)
        inst.__constructing = True
        inst.init(*args, **kwargs)
        inst.__constructing = False
        return inst

    def set_attr(attr, is_final=True, check_can_set=None):
        def do_set(self, value):
            if not self.__constructing and is_final:
                raise AttributeError("can't set attribute")
            if callable(check_can_set):
                value = check_can_set(self, value)
            self.__setattr__('__' + attr, value)
        return do_set
    set_attr = staticmethod(set_attr)

    def get_attr(attr):
        return lambda self: getattr(self, '__' + attr)
    get_attr = staticmethod(get_attr)

class Element(object):

    def __init__(self):
        self.event_bus = EventBus()

    def draw(self):
        pass

    def erase(self):
        pass

class Screen(ManagedProperty):

    def init(self, inherit=None):
        self.__is_drawing = False
        if isinstance(inherit, Screen):
            self.title = inherit.title
            self.body = inherit.body
            self.menu = inherit.menu
            self.exit = inherit.exit
        else:
            self.title = TitleElement()
            self.body = None
            self.menu = MenuElement()
            self.exit = ExitElement()

    def draw(self):
        self.__is_drawing = True
        for element in [self.title, self.body, self.menu, self.exit]:
            element.event_bus.subscribe('draw', element.draw)
            element.draw()

    def remove(self):
        self.__is_drawing = False
        for element in [self.title, self.body, self.menu, self.exit]:
            element.event_bus.unsubscribe('draw', element.draw)
            element.erase()

    def __body_about_to_change(self, new_body):
        if not isinstance(new_body, BodyElement) and new_body is not None:
            raise TypeError("body can only be of type BodyElement or None")
        if new_body is None:
            new_body = BodyElement()
        if self.__is_drawing:
            new_body.event_bus.subscribe('draw', new_body.draw)
        new_body.event_bus.post('draw')
        return new_body

    get_attr = ManagedProperty.get_attr
    set_attr = ManagedProperty.set_attr

    title = property(get_attr('title'), set_attr('title'))
    body = property(get_attr('body'), set_attr('body', False, __body_about_to_change))
    menu = property(get_attr('menu'), set_attr('menu'))
    exit = property(get_attr('exit'), set_attr('exit'))


class TitleElement(Element):

    def __init__(self):
        super(TitleElement, self).__init__()
        self.value = u''

    def set(self, title):
        self.value = unicode(title)
        self.event_bus.post('draw')

    def get(self):
        return self.value

    def draw(self):
        appuifw.app.title = self.value

class BodyElement(Element):

    def draw(self):
        self._super_draw(None)

    def _super_draw(self, body):
        appuifw.app.body = body

class Button(Listenable, Element): # TODO this is useless ATM

    def __init__(self):
        super(Button, self).__init__()
        Element.__init__(self)

class ExitElement(Button):

    def draw(self):
        appuifw.app.exit_key_handler = self.trigger

# TODO screen management
class WindowManager:

    INSTANCE = None

    def __init__(self):
        if WindowManager.INSTANCE:
            raise Exception("Singleton only. use WindowManager.INSTANCE")
        WindowManager.INSTANCE = self
        self.__lock = e32.Ao_lock()
        self.tabs = TabManager() # Could be part of Screen?
        self.root_screen = self.current_screen = screen = Screen()
        screen.title.set('Root Window')
        screen.menu.add_item(MenuItem('Exit', self.exit))
        screen.exit.add_listener(self.exit)

    def show(self, screen):
        if not isinstance(screen, Screen):
            raise TypeError("Cannot show non-screen types")
        self.current_screen.remove()
        self.current_screen = screen
        self.draw()

    def draw(self):
        self.current_screen.draw()

    def exit(self):
        self.__lock.signal()

    def get_current_screen(self):
        return self.current_screen

    def is_showing(self, screen):
        return self.current_screen == screen

    def mainloop(self):
        self.__lock.wait()


from gui_lib.menu import *
from gui_lib.tab import *

WM = WindowManager()
