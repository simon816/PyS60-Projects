DEV_MODE = True

import sys
import re
if DEV_MODE:
    import dbcalendar as calendar
else:
    import calendar
from simon816.interface import Interface
from simon816.form import *
from simon816.time_util import *

lesson_len = Time(1, 5)
periods = [Time(9), Time(10, 5), Time(11, 30), Time(12, 35), Time(14, 10), Time(15, 15)]
subjects = {
    'Computing': ((1, 5), (1, 6), (3, 4), (5, 1)),
    'Electronics': ((1, 2), (1, 3), (2, 5), (4, 1)),
    'Maths': ((2, 4), (4, 5), (4, 6), (5, 4))
}

I = Interface()
class Gui:
    def __init__(self):
        a = ()
        if DEV_MODE: a = ('e:\\devcal.db', 'c')
        self.cal = calendar.open(*a)
        self.closegui = I.current('exit')
        self.main()
    def quit(self):
        if DEV_MODE:
            self.cal.__del__()
        self.closegui()
    def main(self):
        lb = I.listbox([
            (u'Add Homework', self.add_h),
            (u'Add Event', self.add_e),
            (u'Upcomming', self.upcomming)
        ])
        I.set_screen(I.create_screen(body=lb,exit=self.quit))

    def add_h(self):
        ts =  DateTime.now().getAsTimestamp()
        fSubj = ChoiceGroup('Subject', self.get_subjects())
        fDesc = TextField('Description', '', TextField.ANY)
        fDate = DateField('Due Date', DateField.DATE)
        fDate.setDate(ts)
        fTime = DateField('Due Time', DateField.TIME)
        fTime.setDate(ts)

        f = Form('Add Homework', [fSubj, fDesc, fDate, fTime])
        f.setEditable(True)
        f.setDoubleSpace(True)
        f.setMenu([(u'Find Time', lambda:self.find_time(f))])
        f.setSaveHandler(self.save_h)
        f.display()

    def save_h(self, f):
        fSubj = f.get(0)
        fDesc = f.get(1)
        fDate = f.get(2)
        fTime = f.get(3)

        subj = fSubj.getString(fSubj.getSelectedIndex())             
        e = self.cal.add_todo()

        e.content = '[HW] [' + subj + '] ' + fDesc.getString()
        date = DateTime.fromTimestamp(fDate.getDate()).date
        time = DateTime.fromTimestamp(fTime.getDate()).time
        datetime = DateTime(date, time)
        print datetime
        e.set_time(datetime.getAsTimestamp())
        e.commit()

    def add_e(self):
        ts =  DateTime.now().getAsTimestamp()
        fType = ChoiceGroup('Type', [u'General', u'Talk', u'Exam', u'Meeting'])
        fWhat = TextField('What', '', TextField.ANY)
        fWhere = TextField('Where', 'College', TextField.ANY)
        fDay = DateField('Day', DateField.DATE)
        fDay.setDate(ts)
        fWhen = DateField('When', DateField.TIME)
        fWhen.setDate(ts)

        f = Form('Add Event', [fType, fWhat, fWhere, fDay, fWhen])
        f.setEditable(True)
        f.setDoubleSpace(True)
        f.setSaveHandler(self.save_e)
        f.display()

    def save_e(self, f):
        fType = f.get(0)
        fWhat = f.get(1)
        fWhere = f.get(2)
        fDay = f.get(3)
        fWhen = f.get(4)

        type = fType.getString(fType.getSelectedIndex())

        e = self.cal.add_event()

        e.content = '[E] [' + type + '] ' + fWhat.getString()
        e.location = fWhere.getString()
        date = DateTime.fromTimestamp(fDay.getDate()).date
        time = DateTime.fromTimestamp(fWhen.getDate()).time
        datetime = DateTime(date, time)
        print datetime
        e.set_time(datetime.getAsTimestamp())
        e.commit()

    def get_subjects(self):
        return map(unicode, subjects)

    def find_time(self, f):
        fSubj = f.get(0)
        subj = fSubj.getString(fSubj.getSelectedIndex())
        times = self.get_subject(subj)
        now = time.localtime()
        l = []
        s = []
        for t in times:
           days = 7-((now.tm_wday +8) - t[0] )%7
           day = now.tm_mday + days
           tm = self.get_p_time(t[1])
           ts = time.localtime(time.mktime((now[0], now[1], day, tm[0], tm[1], tm[2], now[6], now[7], now[8])))
           s.append(ts)
           l.append(unicode(time.strftime('%a %d %b, %H:%M', (ts))))
       
        t = I.over_list(l)
        if t is not None:
            tm = time.mktime(s[t])
            f.get(2).setDate(tm)
            f.get(3).setDate(tm)
           

    def get_subject(self, s):
        return subjects[s]

    def get_p_time(self, p):
        if p == 1:
            return 9,0,0
        if p==2:
            return 10,5,0
        if p == 3:
            return 11,30,0
        if p == 4:
            return 12,35,0
        if p == 5:
           return 14,10,0
        if p == 6:
           return 15,15,0

    def upcomming(self):
        all = self.cal.find_instances(time.time() - (60*60), time.time() + (60*60*24*7), '')
        entrys = []
        for i in all:
            entrys.append(self.cal[i['id']])
        if len(entrys) == 0:
            I.alert('No recent entrys')
            return False
        items = []
        def mk_cb(e): return lambda:self.open_e(e)
        self._ent = entrys
        for e in entrys:
            e.timestr = unicode(time.strftime('%a %d %b, %H:%M', time.localtime(e.end_time)))
            
            items.append((e.content.replace('[HW] ', ''), e.timestr, mk_cb(e)))
        lb=I.listbox(items)
        I.set_screen(I.create_screen(body=lb, exit=self.main, menu=[
            (u'Mark as Done', self.h_done)
        ]))

    def open_e(self, e):
        m = re.match('\[(?:HW|St.*?ble)\]\ \[(\w+)\]\ (.*)', e.content)
        if not m: return
        f = Form('Entry')
        f.append(TextField('Subject', m.group(1), TextField.ANY))
        f.append(TextField('Description', m.group(2), TextField.ANY))
        f.append(TextField('Time', e.timestr, TextField.ANY))
        f.setDoubleSpace(True)
        f.setEditable(True)
        f.setMenu([(u'View Description', lambda:self.view_desc(f))])
        f.display()

    def h_done(self):
        lb = I.current('body')
        e = self._ent[lb.current()]
        del self.cal[e.id]
        if self.upcomming() == False:
            self.main()

    def view_desc(self, f):
        fDesc = f.get(1)
        from simon816.text import text
        t = text()
        t.loadText(fDesc.getString())
        t.bind('exit', I.current('exit'))
        t.display()

Gui()