from gui_lib import *

def form_test():
    form = Form()
    text_field = TextField('Text field', 'Hi', TextField.ANY)
    numb_field = TextField('Number field', 30.5, TextField.NUMERIC)
    import time
    time_field = DateField('Time', DateField.TIME)
    time_field.set_date(time.time())
    date_field = DateField('Date', DateField.DATE)
    date_field.set_date(time.time())
    combo_field = ChoiceGroup('Choice Group')
    def change():
        value = Popup.prompt('New value')
        if value is None:
            return
        text_field.set_string(value)
    def add():
        index = Popup.prompt('Index', form.size())
        if index is None:
            return
        form.add_item(TextField('Test Field', '', TextField.ANY), int(index))
    def delete():
        index = Popup.prompt('Index', form.size() - 1)
        if index is None:
            return
        form.delete_item(int(index))
    form.add_item(text_field)
    form.add_item(numb_field)
    form.add_item(time_field)
    form.add_item(date_field)
    form.set_editable(True)
    form.set_double_spaced(True)
    form.menu.add_item(MenuItem('Get value 1', lambda: Popup.alert(text_field.get_string())))
    form.menu.add_item(MenuItem('Get value 2', lambda: Popup.alert(numb_field.get_string())))
    form.menu.add_item(MenuItem('Change value', change))
    form.menu.add_item(MenuItem('Add field', add))
    form.menu.add_item(MenuItem('Delete field', delete))
    WM.show(form)
    WM.mainloop()


def listbox_test():
    test_screen = Screen(WM.get_current_screen())
    def say_hi():
        Popup.alert('Hi')
    test_screen.menu.clear()
    test_screen.menu.add_item(MenuItem('Hi', say_hi))
    lb1 = Listbox(ListboxType.SINGLE)
    def missing_callback(index, value):
        Popup.error('Item %d "%s" did not have a callback' % (index, value))
    lb1.default_callback(missing_callback)
    lb1.add_item('No Callback')
    lb1.add_item('Say Hello', lambda: Popup.success('Hello'))
    lb2 = Listbox(ListboxType.DOUBLE)
    lb2.default_callback(missing_callback)
    lb2.add_item('Line 1', 'Line 2')
    lb2.add_item('Hello', 'World', lambda: Popup.alert('Hello World'))
    def set_listbox(lb):
        test_screen.body = lb
    lb_menu = MenuItem('Listboxes')
    lb_menu.add_item(MenuItem('1', lambda: set_listbox(lb1)))
    lb_menu.add_item(MenuItem('2', lambda: set_listbox(lb2)))
    test_screen.menu.add_item(lb_menu)
    WM.show(test_screen)
    WM.mainloop()
    


if __name__ == '__main__':
    listbox_test()
