from gui_lib.core import *

class FormItem(Element):

    def __init__(self, label=u'', value=None, _type=None):
        super(FormItem, self).__init__()
        self.label = unicode(label)
        self.value = value
        self._type = _type

    def event_bus_post(self, key, *args, **kwargs):
        self.event_bus.post(key, self, *args, **kwargs)

    def get_label(self):
        self.event_bus_post('get')
        return self.label

    def set_label(self, label):
        self.label = unicode(label)
        self.event_bus_post('set')

    def get_type(self):
        return self._type

    def get_value(self):
        self.event_bus_post('get')
        return self.value

    def to_tuple(self):
        return (self.get_label(), self.get_type(), self.get_value())

    def from_tuple(self, data):
        self.label = data[0]

class ChoiceGroup(FormItem):

    def __init__(self, label, values=[]):
        super(ChoiceGroup, self).__init__(label, _type='combo')
        self.elements = map(unicode, values)
        self.selected = 0

    def get_value(self):
        self.event_bus_post('get')
        return (map(unicode, self.elements), self.selected)

    def _validateIndex(self, index):
        if index < 0 or index > self.size() - 1:
            raise IndexError('Bad index')

    def add_choice(self, value,position=-1):
        if position == -1:
            self.elements.append(unicode(value))
        else:
            self.elements.insert(position, unicode(value))
        self.event_bus_post('set')

    def delete(self, elementNum):
        self._validateIndex(elementNum)
        self.elements.remove(elementNum)
        self.event_bus_post('set')

    def clear(self):
        self.elements = []
        self.event_bus_post('set')

    def get_selected_index(self):
        self.event_bus_post('get')
        return self.selected

    def get_string(self, elementNum):
        self._validateIndex(elementNum)
        self.event_bus_post('get')
        return self.elements[elementNum]

    def get_selected_value(self):
        return self.get_string(self.get_selected_index())

    def is_selected(self, elementNum):
        self._validateIndex(elementNum)
        return self.get_selected_index() == elementNum

    def set_selected_value(self, elementNum):
        self._validateIndex(elementNum)
        self.selected = elementNum
        self.event_bus_post('set')

    def size(self):
        self.event_bus_post('get')
        return len(self.elements)

    def from_tuple(self, data):
        super(ChoiceGroup, self).from_tuple(data)
        self.elements, self.selected = data[2]



class DateField(FormItem):

    DATE = 1
    TIME = 2

    def __init__(self, label, mode):
        super(DateField, self).__init__(label)
        self.set_input_mode(mode)

    def get_date(self):
        return self.get_value()

    def get_input_mode(self):
        self.event_bus_post('get')
        return self.mode

    def set_date(self, date):
     #   if self.mode == self.TIME:
            # date must be less than 1 day from 0 epoch
      #  elif self.mode == self.DATE:
            # Ignore time value
        self.value = date
        self.event_bus_post('set')

    def set_input_mode(self, mode):
        if mode not in [self.DATE, self.TIME]:
            raise TypeError('Invalid mode')
        self.mode = mode
        if mode == self.DATE:
            self._type = 'date'
        elif mode == self.TIME:
            self._type = 'time'
        self.event_bus_post('set')

    def from_tuple(self, data):
        super(DateField, self).from_tuple(data)
        if data[1] == 'date':
            self.set_input_mode(self.DATE)
        elif data[1] == 'time':
            self.set_input_mode(self.TIME)
        self.set_date(data[2])


class TextField(FormItem):

    ANY = 0
    NUMERIC = 1

    def __init__(self, label, text, constraints):
        super(TextField, self).__init__(label)
        self.set_constraints(constraints)
        self.set_string(text)

    def delete(self, offset, length):
        raise NotImplementedError()

    def get_constraints(self):
        self.event_bus_post('get')
        return self.constraints

    def get_string(self):
        return self.get_value()

    def insert(self, data, offset, length, position):
        raise NotImplementedError()

    def set_constraints(self, constraints):
        if constraints not in [self.ANY, self.NUMERIC]:
            raise TypeError('Invalid constraint')
        self.constraints = constraints
        if constraints == self.ANY:
            self._type = 'text'
        elif constraints == self.NUMERIC:
            self._type = 'number'
        self.event_bus_post('set')

    def set_string(self, text):
        if self.constraints == self.ANY:
            text = unicode(text)
        elif self.constraints == self.NUMERIC:
            text = int(text)
        self.value = text
        self.event_bus_post('set')

    def size(self):
        self.event_bus_post('get')
        return len(self.text)

    def from_tuple(self, data):
        super(TextField, self).from_tuple(data)
        if data[1] == 'text':
            self.set_constraints(self.ANY)
        elif data[1] == 'number':
            self.set_constraints(self.NUMERIC)
        self.set_string(data[2])

class Form(Screen):

    class SaveEvent(object):

        def __init__(self, form_data):
            self.data = form_data
            self.__cancelled = False

        def cancel(self):
            self.__cancelled = True

        def is_cancelled(self):
            return self.__cancelled

    class FormMenu(MenuElement):

        def draw(self, form):
            form.menu = map(lambda item: item._get_drawable(), self.items)

    def init(self, inherit=None):
        self.menu = self.FormMenu()
        if isinstance(inherit, Screen):
            self.title = inherit.title
            self.menu.items = inherit.menu.items
            self.exit = inherit.exit
        else:
            self.title = TitleElement()
            self.exit = Listenable()
        self.save = Listenable()
        self.body = None # from Screen
        self.items = []
        self.editable = False
        self.double_spaced = False
        self.edit_labels = False
        self.__event_bus = EventBus() # Events to do with the form itself (items, properties etc.)

    def add_item(self, item, position=-1):
        if not isinstance(item, FormItem):
            raise TypeError("Not a valid item type")
        if position == -1:
            position = self.size()
            self.items.append(item)
        else:
            self.items.insert(position, item)
        self.__event_bus.post('insert', position, item)

    def delete_item(self, item_or_index):
        II = item_or_index
        index = None
        if II in self.items:
            index = self.items.index(II)
        elif type(II) is int and II >= 0 and II < len(self.items):
            index = II
        else:
            raise IndexError("Item or index does not exist")
        del self.items[index]
        self.__event_bus.post('delete', index)

    def clear(self):
        self.items = []
        self.__event_bus.post('clear')

    def get_item(self, index):
        if type(index) is int and index >= 0 and index < len(self.items):
            return self.items[index]
        return None

    def size(self):
        return len(self.items)

    def set_editable(self, editable):
        self.editable = not not editable
        # TODO __form_listener ?

    def set_edit_labels(self, edit_labels):
        self.edit_labels = not not edit_labels
        # TODO __form_listener ?

    def set_double_spaced(self, double_space):
        self.double_spaced = not not double_space
        # TODO __form_listener ?

    def draw(self):
        items = map(lambda item: item.to_tuple(), self.items)

        flags = 0
        if self.editable:
            flags += appuifw.FFormEditModeOnly
        else:
            flags += appuifw.FFormViewModeOnly
        if self.edit_labels:
            flags += appuifw.FFormAutoLabelEdit
        if self.double_spaced:
            flags += appuifw.FFormDoubleSpaced

        form = appuifw.Form(items, flags)
        self.menu.draw(form)

        def try_to_save(form_data):
            event = self.SaveEvent(form_data)
            self.save.trigger(event)
            return not event.is_cancelled()

        form.save_hook = try_to_save
        self.title.draw()

        def on_item_bus_post(key, item, *args, **kwargs):
            index = self.items.index(item)
            item.event_bus.unsubscribe('*', on_item_bus_post)
            if key == 'get':
                form_tuple = form[index]
                item.from_tuple(form_tuple)
            elif key == 'set':
                form[index] = item.to_tuple()
            item.event_bus.subscribe('*', on_item_bus_post)

        buses = map(lambda item: item.event_bus, self.items)

        map(lambda event_bus: event_bus.subscribe('*', on_item_bus_post), buses)

        def on_form_change(key, *args, **kwargs):
            if key == 'insert':
                position, item = args
                form.insert(position, item.to_tuple())
            elif key == 'delete':
                index = args[0]
                form.pop(index)
            elif key == 'clear':
                while len(form):
                    form.pop()
        self.__event_bus.subscribe('*', on_form_change)
        form.execute()
        self.__event_bus.unsubscribe('*', on_form_change)

        map(lambda event_bus: event_bus.unsubscribe('*', on_item_bus_post), buses)
        self.exit.trigger()

    save = property(ManagedProperty.get_attr('save'), ManagedProperty.set_attr('save'))
    body = property(ManagedProperty.get_attr('body'), ManagedProperty.set_attr('body'))
