import appuifw

class Displayable(object):
    def getTitle(self):
        pass

    def setTitle(self, title):
        pass

class Form(Displayable):
    def __init__(self, title=None, items=[]):
        self.setTitle(title)
        self.items = []
        self.flags = 0
        self.setMenu([])
        self.setEditable(False)
        self.setDoubleSpace(False)
        self.setEditLabels(False)
        self._active = False
        self.setSaveHandler(lambda f:None)
        for item in items:
            self.append(item)

    def _validateItem(self, item):
        if not item:
            raise ValueError('Null values not allowed')
        if not isinstance(item, Item):
            raise TypeError('Not a valid Item type')
        if item in self.items:
            raise ReferenceError('Item already exists')

    def _validateIndex(self, index):
        if index < 0 or index > self.size() - 1:
            raise IndexError('Bad index')

    def append(self, item):
        self._validateItem(item)
        self.items.append(item)
        if self._active:
            self.form.insert(self.size() - 1, item._mk_tuple())
        return self.size() - 1

    def delete(self, itemNum):
        self._validateIndex(itemNum)
        self.items.remove(itemNum)

    def deleteAll(self):
        self.items = []

    def get(self, itemNum):
        self._validateIndex(itemNum)
        if self._active:
            self.items[itemNum]._update(self.form[itemNum][2])
        return self.items[itemNum]

    def insert(self, itemNum, item):
        self._validateItem(item)
        if itemNum == self.size():
            self.append(item)
            return
        self._validateIndex(itemNum)
        self.items.insert(itemNum, item)
        if self._active:
            self.form.insert(itemNum, item._mk_tuple())

    def set(self, itemNum, item):
        self._validateItem(item)
        self._validateIndex(itemNum)
        self.items[itemNum] = item
        if self._active:
            self.form[itemNum] = item._mk_tuple()

    def setItemStateListener(self, iListener):
        pass

    def size(self):
        return len(self.items)

    def setSaveHandler(self, handler):
        if hasattr(handler, '__call__'):
            self._saveHandler = handler
            return
        raise TypeError('Save handler must be callable')

    def _updateAndSave(self, f):
        for item in self.items:
            item._update(f[item._form[1]][2])
            item.lock_update = True
        self._saveHandler(self)
        for item in self.items:
            item.lock_update = False

    def display(self):
        items = []
        for item in self.items:
            items.append(item._mk_tuple())
        form = appuifw.Form(items, self.flags)
        for i in range(self.size()):
            self.items[i]._form = (form, i)
        form.menu = self.menu
        form.save_hook = self._updateAndSave
        self.form = form
        self._active = True
        form.execute()
        for item in self.items:
            item._update(form[item._form[1]][2])
            item._form = None
        self._active = False
        self.form = None

    def setEditable(self, editable):
        self.flags |= appuifw.FFormEditModeOnly
        self.flags |= appuifw.FFormViewModeOnly
        if editable:
            self.flags -= appuifw.FFormViewModeOnly
        else:
            self.flags -= appuifw.FFormEditModeOnly

    def setEditLabels(self, editable):
        self.flags |= appuifw.FFormAutoLabelEdit
        if not editable:
            self.flags -= appuifw.FFormAutoLabelEdit

    def setDoubleSpace(self, doubleSpace):
        self.flags |= appuifw.FFormDoubleSpaced
        if not doubleSpace:
            self.flags -= appuifw.FFormDoubleSpaced

    def setMenu(self, menu):
        self.menu = menu

class Item(object):
    def __init__(self):
        self.label = ''
        self._form = None
        self.lock_update = False

    def getLabel(self):
        return unicode(self.label)

    def setLabel(self, label):
       if label == None:
           self.label = ''
       if type(label) not in (str, unicode):
           raise TypeError('Invalid label type')
       self.label = str(label)

    def _mk_tuple(self):
        raise NotImplementedError()

    def _update(self, f_data):
        raise NotImplementedError()

    def _updateForm(self):
        if self._form:
            item = self._mk_tuple()
            self._form[0][self._form[1]] = item

class ChoiceGroup(Item):
    def __init__(self, label, stringElements=[]):
        super(ChoiceGroup, self).__init__()
        self.setLabel(label)
        self.elements = []
        self.selected = 0
        for element in stringElements:
            self.append(element)

    def _validateIndex(self, index):
        if index < 0 or index > self.size() - 1:
            raise IndexError('Bad index')

    def _validateString(self, string):
        if type(string) not in (str, unicode):
            raise TypeError('Invalid element type')

    def append(self, stringPart):
        self. _validateString(stringPart)
        self.elements.append(stringPart)
        return self.size() - 1
        self._updateForm()

    def delete(self, elementNum):
        self._validateIndex(elementNum)
        self.elements.remove(elementNum)
        self._updateForm()

    def deleteAll(self):
        self.elements = []
        self._updateForm()

    def getSelectedIndex(self):
        return self.selected

    def getString(self, elementNum):
        self._validateIndex(elementNum)
        return self.elements[elementNum]

    def getSelectedValue(self):
        return self.getString(self.getSelectedIndex())

    def insert(self, elementNum, stringPart):
        self._validateIndex(elementNum)
        self. _validateString(stringPart)
        self.elements.insert(elementNum, stringPart)
        self._updateForm()

    def isSelected(self, elementNum):
        self._validateIndex(elementNum)
        return self.getSelectedIndex() == elementNum

    def set(self, elementNum, stringPart):
        self._validateIndex(elementNum)
        self. _validateString(stringPart)
        self.elements[elementNum] = stringPart
        self._updateForm()

    def setSelectedIndex(self, elementNum):
        self._validateIndex(elementNum)
        self.selected = elementNum
        self._updateForm()

    def size(self):
        return len(self.elements)

    def _mk_tuple(self):
        return (self.getLabel(), 'combo', (map(unicode, self.elements), self.getSelectedIndex()))

    def _update(self, f_data):
        if self.lock_update: return
        self.elements = f_data[0]
        self.selected = f_data[1]

class DateField(Item):
    DATE = 1
    TIME = 2
    def __init__(self, label, mode):
        super(DateField, self).__init__()
        self.setInputMode(mode)
        self.setLabel(label)
        self.date = None

    def getDate(self):
        return self.date

    def getInputMode(self):
        return self.mode

    def setDate(self, date):
     #   if self.mode == self.TIME:
            # date must be less than 1 day from 0 epoch
      #  elif self.mode == self.DATE:
            # Ignore time value
        self.date = date
        self._updateForm()

    def setInputMode(self, mode):
        if mode not in [self.DATE, self.TIME]:
            raise TypeError('Invalid mode')
        self.mode = mode
        self._updateForm()

    def _mk_tuple(self):
        if self.mode == self.DATE: type = 'date'
        elif self.mode == self.TIME: type = 'time'
        return (self.getLabel(), type, self.getDate())

    def _update(self, f_data):
        if self.lock_update: return
        self.setDate(f_data)

class TextField(Item):
    ANY = 0
    NUMERIC = 1
    def __init__(self, label, text, constraints):
        super(TextField, self).__init__()
        self.setLabel(label)
        self.setConstraints(constraints)
        self.setString(text)

    def delete(self, offset, length):
        pass

    def getChars(self, data):
        if type(data) != list:
            raise TypeError('data must be list')
        if len(data) < self.size():
            raise IndexError('data smaller than text size')
        for i in range(self.size()):
            data[i] = self.text[i]

    def getConstraints(self):
        return self.constraints

    def getString(self):
        return self.text

    def insert(self, data, offset, length, position):
        pass

    def setChars(self, data, offset, length):
        pass

    def setConstraints(self, constraints):
        if constraints not in [self.ANY, self.NUMERIC]:
            raise TypeError('Invalid constraint')
        self.constraints = constraints

    def setString(self, text):
        if self.constraints == self.ANY:
            text = unicode(text)
        elif self.constraints == self.NUMERIC:
            text = int(text)
        self.text = text
        self._updateForm()

    def size(self):
        return len(self.text)

    def _mk_tuple(self):
        if self.constraints == self.ANY:
            type = 'text'
            fn = unicode
        elif self.constraints == self.NUMERIC:
            type = 'number'
            fn = int
        return (self.getLabel(), type, fn(self.getString()))

    def _update(self, f_data):
        if self.lock_update: return
        if f_data == self.text: return
        print 'update from', self.text, 'to', f_data
        self.text = f_data

if __name__ == '__main__':
    f = Form()
    field = TextField('Test', 'Example', TextField.ANY)
    f.append(field)
    f.insert(0, ChoiceGroup('Selection', ['A', 'B', 'C']))
    f.setEditable(True)
    def save(f):
        f.get(1).setString('Modified')
        print 'save(' + f.get(1).getString() + ')'
    f.setSaveHandler(save)
    f.display()
    print 'end', f.get(1).getString()
