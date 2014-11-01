from gui_lib.core import *

#__all__ = ['MenuItem', 'MenuElement']

class MenuItem(Listenable):

    def __init__(self, text=u'', callback=None):
        super(MenuItem, self).__init__()
        self.items = []
        self._event_bus = EventBus()
        self.set_text(text)
        if callable(callback):
            self.add_listener(callback)

    def set_text(self, text):
        self.text = unicode(text)
        self._event_bus.post('redraw')

    def get_text(self):
        return self.text

    def get_item(self, index_or_item_or_value):
        IIV = index_or_item_or_value
        if IIV in self.items:
            return IIV
        if type(IIV) is int and IIV >= 0 and IIV < len(self.items):
            return self.items[IIV]
        for item in self.items:
            if item.get_text() == IIV:
                return item
        return None

    def clear(self):
        self.items = []
        self._event_bus.post('redraw')

    def add_item(self, item, position=-1):
        if not isinstance(item, MenuItem):
            raise TypeError("Item must be of type MenuItem")

        self.items.append(item)
        self._event_bus.post('redraw')

    def remove_item(self, index_or_item_or_value):
        item = self.get_item(index_or_item_or_value)
        if item is None:
            raise IndexError("Item not found")
        self.items.remove(item)
        self._event_bus.post('redraw')

    def _get_drawable(self):
        if len(self.items) > 0:
            return (self.text, tuple(map(lambda item: item._get_drawable(), self.items)))
        else:
            return (self.text, self.trigger)


class MenuElement(MenuItem, Element):

    def __init__(self):
        super(MenuElement, self).__init__()
        Element.__init__(self)

    def draw(self):
        map(lambda item: item._event_bus.subscribe('redraw', self.__draw_impl), self.items)
        self.__draw_impl()

    def __draw_impl(self):
        appuifw.app.menu = map(lambda item: item._get_drawable(), self.items)

    def erase(self):
        map(lambda item: item._event_bus.unsubscribe('redraw', self.__draw_impl), self.items)
