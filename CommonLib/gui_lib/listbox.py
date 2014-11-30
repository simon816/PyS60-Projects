from gui_lib.core import *

#__all__ = ['ListboxType', 'Listbox']

class ListboxType(object):
    SINGLE = property(lambda s: 'single')
    DOUBLE = property(lambda s: 'double')
    SINGLE_GRAPHIC = property(lambda s: 'sing_graph')
    DOUBLE_GRAPHIC = property(lambda s: 'doub_graph')

ListboxType = ListboxType()

class Listbox(ManagedProperty, BodyElement):

    def __init__(self, *args, **kwargs):
        # BodyElement has no init args
        super(Listbox, self).__init__()

    def init(self, list_type):
        if list_type not in [ListboxType.SINGLE, ListboxType.DOUBLE,
                        ListboxType.SINGLE_GRAPHIC, ListboxType.DOUBLE_GRAPHIC]:
            raise TypeError("Invalid listbox type")
        self.type = list_type
        self.__list = []
        self._default_calback = None
        self._selected = None

    def add_item(self, arg0, arg1=None, arg2=None, arg3=None):
        """
            overloading:
            SINGLE
                add_item(String value)
                add_item(String value, Callable callback)
            DOUBLE
                add_item(String value1, String value2)
                add_item(String value1, String value2, Callable callback)
            SINGLE_GRAPHIC
                add_item(String value, Icon graphic)
                add_item(String value, Icon graphic, Callable callback)
            DOUBLE_GRAPHIC
                add_item(String value1, String value2, Icon graphic)
                add_item(String value1, String value2, Icon graphic, Callable callback)
        """
        callback = None
        value = None
        if self.type == ListboxType.SINGLE:
            if arg2 or arg3:
                raise TypeError("Wrong argument count passed into single listbox")
            callback = arg1
            value = unicode(arg0)
        elif self.type == ListboxType.DOUBLE:
            if arg3:
                raise TypeError("Wrong argument count passed into double listbox")
            if arg1 is None:
                raise TypeError("Missing line two for double listbox item")
            value = tuple(map(unicode, [arg0, arg1]))
            callback = arg2
        elif self.type == ListboxType.SINGLE_GRAPHIC:
            if arg3:
                raise TypeError("Wrong argument count passed into single graphic listbox")
            if arg1 is None:
                raise TypeError("Missing graphic for single graphic listbox item")
            if not isinstance(arg1, Icon):#TODO: Icon
                raise TypeError("Must be icon type")
            value = (unicode(arg0), arg1)
            callback = arg2
        elif self.type == ListboxType.DOUBLE_GRAPHIC:
            if arg1 is None:
                raise TypeError("Missing line two for double graphic listbox item")
            if arg2 is None:
                raise TypeError("Missing graphic for double graphic listbox item")
            if not isinstance(arg2, Icon):#TODO: Icon
                raise TypeError("Must be icon type")
            value = tuple(map(unicode, [arg0, arg1]) + [arg2])
            callback = arg3
        if callback and not callable(callback):
            raise TypeError("Callback must be None or callable")
        self.__list.append({'callback': callback, 'value': value})
        self.event_bus.post('list_update')

    def clear(self):
        while len(self.__list):
            self.__list.pop()

    def draw(self):
        get_items = lambda: map(lambda item: item['value'], self.__list)
        listbox = appuifw.Listbox(get_items(), lambda: self.__handle(listbox))
        self.event_bus.subscribe('list_update', lambda: listbox.set_list(get_items(), listbox.current()))
        self.event_bus.subscribe('set_selected', lambda index: listbox.set_list(get_items(), index))
        self.event_bus.subscribe('get_selected', lambda: setattr(self, '_selected', listbox.current()))
        self._super_draw(listbox)
        self.event_bus.post('set_selected', self._selected)

    def erase(self):
        self.event_bus._unsub_all('list_update')
        self.event_bus._unsub_all('set_selected')
        self.event_bus._unsub_all('get_selected')
        print 's', self._selected
        #self._selected = None

    def get_value_at(self, index):
        return self.__list[index]

    def get_selected_index(self):
        self.event_bus.post('get_selected')
        return self._selected

    def set_selected(self, index):
        if type(index) is not int or index < 0 or index >= len(self.__list):
            raise TypeError("Invalid index")
        self.event_bus.post('set_selected', index)

    def default_callback(self, callback):
        if callback is not None and not callable(callback):
            raise TypeError("Callback must be callable or None")
        self._default_calback = callback

    def __handle(self, listbox):
        current = self._selected = listbox.current()
        item = self.__list[current]
        if item['callback']:
            item['callback']()
        elif self._default_calback:
            self._default_calback(current, item['value'])

    type = property(ManagedProperty.get_attr('type'), ManagedProperty.set_attr('type'))
    __list = property(ManagedProperty.get_attr('__list'), ManagedProperty.set_attr('__list'))
