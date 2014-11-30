from gui_lib import *
from simon816.time_util import *

lesson_len = Time(1, 5)
periods = [Time(9), Time(10, 5), Time(11, 30), Time(12, 35), Time(14, 10), Time(15, 15)]
subjects = {
    'Computing': ((1, 5), (1, 6), (3, 4), (5, 1)),
    'Electronics': ((1, 2), (1, 3), (2, 5), (4, 1)),
    'Maths': ((2, 4), (4, 5), (4, 6), (5, 4))
}

DEV_MODE = True

if DEV_MODE:
    import dbcalendar as calendar
else:
    import calendar

class Planner:

    def __init__(self):
        if DEV_MODE:
            self.calendar = calendar.open('E:\\devcal.db', 'c')
        else:
            self.calendar = calendar.open()

        self.make_screens()
        self.show_main()

    def quit(self):
        if DEV_MODE:
            self.calendar.__del__()
        WM.exit()

    def make_screens(self):
        self.main_screen = screen = Screen()
        screen.body = lb = Listbox(ListboxType.SINGLE)
        screen.title.set('Planner')
        lb.add_item('Add Homework', self.add_homework)
        lb.add_item('Add Event',  self.add_event)
        lb.add_item('Upcomming', self.show_upcomming)
        screen.exit.add_listener(self.quit)

        self.new_homework_screen = screen = Form()
        screen.title.set('Add Homework')
        screen.add_item(ChoiceGroup('Subject', self.get_subjects()))
        screen.add_item(TextField('Description', '', TextField.ANY))
        screen.add_item(DateField('Due Date', DateField.DATE))
        screen.add_item(DateField('Due Time', DateField.TIME))
        screen.menu.add_item(MenuItem('Find Time', self.find_time))
        screen.set_editable(True)
        screen.set_double_spaced(True)
        screen.exit.add_listener(self.save_homework)
        screen.exit.add_listener(self.show_main)

        self.new_event_screen = screen = Form()
        screen.title.set('Add Event')
        screen.add_item(ChoiceGroup('Type', ['General', 'Talk', 'Exam', 'Meeting']))
        screen.add_item(TextField('What', '', TextField.ANY))
        screen.add_item(TextField('Where', 'College', TextField.ANY))
        screen.add_item(DateField('Day', DateField.DATE))
        screen.add_item(DateField('When', DateField.TIME))
        screen.set_editable(True)
        screen.set_double_spaced(True)
        screen.exit.add_listener(self.show_main)
        screen.save.add_listener(self.save_event)

        self.upcomming_screen = screen = Screen()
        screen.title.set('Upcomming Events')
        screen.body = Listbox(ListboxType.DOUBLE)
        screen.menu.add_item(MenuItem('Mark as Done', self.mark_done))
        screen.exit.add_listener(self.show_main)

        self.event_view_screen = screen = Form()
        screen.title.set('View Entry')
        screen.add_item(TextField('Subject', '', TextField.ANY))
        screen.add_item(TextField('Description', '', TextField.ANY))
        screen.add_item(TextField('Time', '', TextField.ANY))
        screen.set_editable(True)
        screen.set_double_spaced(True)
        screen.menu.add_item(MenuItem('View Description', self.view_description))
        #screen.exit.add_listener(self.show_upcomming)
        screen.save.add_listener(lambda save_event: save_event.cancel())

    def show_main(self):
        WM.show(self.main_screen)

    def add_homework(self):
        now = DateTime.now().getAsTimestamp()
        form = self.new_homework_screen
        form.get_item(2).set_date(now)
        form.get_item(3).set_date(now)
        WM.show(form)

    def save_homework(self, form_save_event=0):
        screen = WM.get_current_screen()
        form = screen#form_save_event.form

        subject = form.get_item(0).get_selected_value()
        description = form.get_item(1).get_value()
        date = DateTime.fromTimestamp(form.get_item(2).get_value()).date
        time = DateTime.fromTimestamp(form.get_item(3).get_value()).time
        datetime = DateTime(date, time)

        if description == '':
            return
        form.get_item(1).set_string('')

        entry = self.calendar.add_todo()

        entry.content = '[HW] [%s] %s' % (subject, description)
        entry.set_time(datetime.getAsTimestamp())

        entry.commit()

    def add_event(self):
        now = DateTime.now().getAsTimestamp()
        form = self.new_event_screen
        form.get_item(3).set_date(now)
        form.get_item(4).set_date(now)
        WM.show(form)

    def save_event(self, form_save_event):
        form = form_save_event.form

        type = form.get_item(0).get_selected_value()
        what = form.get_item(1).get_value()
        where = form.get_item(2).get_value()
        date = DateTime.fromTimestamp(form.get_item(3).get_value()).date
        time = DateTime.fromTimestamp(form.get_item(4).get_value()).time
        datetime = DateTime(date, time)

        entry = self.calendar.add_event()

        entry.content = '[E] [%s] %s' % (type, what)
        entry.location = where
        entry.set_time(datetime.getAsTimestamp())

        entry.commit()

    def get_upcomming_entries(self):
        from_time = DateTime.now()
        from_time.addHours(-1)
        from_time = DateTime(Date(2014), Time())
        to_time = DateTime.now()
        to_time.addDays(7)

        instances = self.calendar.find_instances(
            from_time.getAsTimestamp(),
            to_time.getAsTimestamp(), '')

        entries = []
        for inst in instances:
            entries.append(self.calendar[inst['id']])
        return entries

    def show_upcomming(self):
        entries = self.get_upcomming_entries()
        if len(entries) == 0:
            Popup.alert('No recent entries')
            return False
        listbox = self.upcomming_screen.body

        self.__entries = entries

        listbox.clear()
        import time
        for entry in entries:
            line1 = entry.content.replace('[HW] ', '')
            line2 = time.strftime('%a %d %b, %H:%M', time.localtime(entry.end_time))
            listbox.add_item(line1, line2)

        listbox.default_callback(self.show_entry)

        WM.show(self.upcomming_screen)
        return True

    def get_subjects(self):
        return subjects.keys()

    def find_time(self):
        form = WM.get_current_screen()
        if not isinstance(form, Form):
            Popup.error('Current body is not the form')
            return

        subject = form.get_item(0).get_selected_value()
        subj_periods = subjects[subject]

        times = []
        times_popup_list = []

        import time as time_
        st_time = time_.localtime()

        for period_tpl in subj_periods:
            day, period = period_tpl

            date = Date(st_time.tm_year, st_time.tm_mon, (7 - ((st_time.tm_wday + 8) - day) % 7) + st_time.tm_mday)
            time = periods[period - 1]

            datetime = DateTime(date, time)
            timestamp = datetime.getAsTimestamp()

            times_popup_list.append(time_.strftime('%a %d %b, %H:%M',
                                                   time_.localtime(timestamp)))
            times.append(timestamp)

        selected = Popup.menu(times_popup_list, 'Times for %s' % subject)
        if selected is None:
            return
        form.get_item(2).set_date(times[selected])
        form.get_item(3).set_date(times[selected])

    def show_entry(self, index, value):
        content, time = value
        import re
        #m = re.match('\[HW\]\ \[(\w+)\]\ (.*)', content)
        m = re.match('\[(\w+)\]\ (.*)', content)
        if not m:
            Popup.error('Failed to match')
            return
        form = self.event_view_screen
        form.get_item(0).set_string(m.group(1))
        form.get_item(1).set_string(m.group(2))
        form.get_item(2).set_string(time)
        import thread
        #thread.start_new_thread(WM.show, (form, ))
        import e32
        #e32.ao_sleep(0, lambda:WM.show(form))
        WM.show(form)

    def view_description(self):
        form = WM.get_current_screen()
        description = form.get_item(1).get_value()
        #form.exit.remove_listener(self.show_upcomming)
        from simon816.text import text
        t = text()
        t.loadText(description)
        t.bind('exit', self.show_upcomming)
        t.display()

    def mark_done(self):
        listbox = WM.get_current_screen().body
        entries = self.__entries
        entry = entries[listbox.get_selected_index()]

        del self.calendar[entry.id]

        if self.show_upcomming() == False:
            # No more entries
            self.show_main()

if __name__ == '__main__':
    p = Planner()
    WM.mainloop()
