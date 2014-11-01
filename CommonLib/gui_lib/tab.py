from gui_lib.core import *

#__all__ = ['Tab', 'TabManager']

class Tab(Listenable):

    def __init__(self, manager, text=None):
        super(Tab, self).__init__()
        self.text = text
        self.manager = manager

    def set_text(self, text):
        self.text = unicode(text)
        if self.manager.tab_exists(self):
            # Update gui
            self.manager.draw()

    def get_text(self):
        return self.text

# TODO Event Bus system for tabs
class TabManager(Element):

    def __init__(self):
        super(TabManager, self).__init__()
        self.clear()

    def add_tab(self, tab, position=-1):
        if not isinstance(tab, Tab):
            raise TypeError("tab must be of type Tab")
        if position == -1:
            self.tabs.append(tab)
        else:
            if type(position) is not int:
                raise TypeError("Position given is not an int")
            self.tabs.insert(position, tab)
        self.draw()

    def _get_tab(self, index_or_tab):
        IT = index_or_tab
        if IT in self.tabs:
            return IT
        elif type(IT) is int and IT >= 0 and IT < len(self.tabs):
            return self.tabs[IT]
        else:
            return None

    def tab_exists(self, index_or_tab):
        return self._get_tab(index_or_tab) is not None

    def remove_tab(self, index_or_tab):
        tab = self._get_tab(index_or_tab)
        if tab is None:
            raise IndexError("Invalid tab or tab not added")
        self.tabs.remove(tab)
        self.draw()

    def switch_tab(self, index_or_tab):
        tab = self._get_tab(index_or_tab)
        if tab is None:
            raise IndexError("Tab does not exist")
        if tab == self.selected:
            return
        index = self.tabs.index(tab)
        appuifw.app.activate_tab(index)
        self.__handle(index)

    def get_selected_tab(self):
        return self.selected

    def __handle(self, index):
        self.selected = self.tabs[index]
        self.selected.trigger()

    def draw(self):
        appuifw.app.set_tabs(map(lambda tab: tab.get_text(), self.tabs), self.__handle)
        if self.selected is not None:
            self.switch_tab(self.selected)

    def clear(self):
        self.tabs = []
        self.selected = None
        self.draw()

    def hide(self):
        # Is this a good idea?
        appuifw.app.set_tabs([], lambda index: None)
