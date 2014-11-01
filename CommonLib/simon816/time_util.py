import time

class TimeBounding:

    def __init__(self, raw_value, max=-1, upper_bounding=None):
        self.max = max
        self.upper = upper_bounding
        self.set(raw_value)
 
    def getValue(self):
        return self.value

    def set(self, value):
        if value < self.max or self.max == -1:
            self.value = int(value)
            return
        elif value >= self.max:
            if self.upper == None:
                raise OverflowError("Value is > max and no upper bounding exists")
            else:
                self.value = int(value % self.max)
                self.upper.add(value / self.max)

    def add(self, value):
        self.set(self.value + value)

    def cascadeValue(self):
        value = self.value
        if self.upper:
            upper_value = self.upper.cascadeValue()
            value += upper_value * self.max
        return value


class Time(object):
    def __init__(self, h=0, m=0, s=0, ms=0):
        self.hours = TimeBounding(h)
        self.minutes = TimeBounding(m, 60, self.hours)
        self.seconds = TimeBounding(s, 60, self.minutes)
        self.milliseconds = TimeBounding(ms, 1000, self.seconds)

    def now(limit_24hour = True):
        i = time.time()
        t = time.localtime(i)
        now = Time(t.tm_hour, t.tm_min, t.tm_sec, (i * 1000) % 1000)
        if limit_24hour:
            now.setHours(now.getHours() % 24)
        return now
    now = staticmethod(now)

    def getHours(self):
        return self.hours.getValue()

    def getMinutes(self):
        return self.minutes.getValue()

    def getSeconds(self):
        return self.seconds.getValue()

    def getMilliseconds(self):
        return self.milliseconds.getValue()

    def setHours(self, hours):
        self.hours.set(hours)

    def setMinutes(self, minutes):
        self.minutes.set(minutes)

    def setSeconds(self, seconds):
        self.seconds.set(seconds)

    def setMilliseconds(self, milliseconds):
        self.milliseconds.set(milliseconds)

    def addHours(self, hours):
        self.hours.add(hours)

    def addMinutes(self, minutes):
        self.minutes.add(minutes)

    def addSeconds(self, seconds):
        self.seconds.add(seconds)

    def addMilliseconds(self, milliseconds):
        self.milliseconds.add(milliseconds)

    def getAsMinutes(self):
        return self.minutes.cascadeValue()

    def getAsSeconds(self):
        return self.seconds.cascadeValue()

    def getAsMilliseconds(self):
        return self.milliseconds.cascadeValue()

    def __str__(self):
        return "%02d:%02d:%02d.%03d" % (
            self.getHours(), self.getMinutes(),
            self.getSeconds(), self.getMilliseconds())

    def __repr__(self):
        return str(self)

class Date(object):

    def __init__(self, y=0, m=1, d=1):
        self.years = TimeBounding(y)
        self.months = TimeBounding(m, 12, self.years)
        self.days = TimeBounding(d, -1, self.months)
        self._systemAdjust()

    def getDaysInMonth(self):
        month = self.months.getValue()
        if month in [1, 3, 5, 7, 8, 10, 12]:
           return 31
        if month == 2:
            return 28
        return 30

    def now():
        t = time.localtime()
        now = Date(t.tm_year, t.tm_mon, t.tm_mday)
        return now
    now = staticmethod(now)

    def getYears(self):
        return self.years.getValue()

    def getMonths(self):
        return self.months.getValue()

    def getDays(self):
        return self.days.getValue()

    def _systemAdjust(self):
        tstrt = time.localtime(time.mktime((
            self.getYears(), self.getMonths(), self.getDays(),
            0, 0, 0, 0, 0, 0
        )))
        self.years.set(tstrt.tm_year)
        self.months.set(tstrt.tm_mon)
        self.days.set(tstrt.tm_mday)
        self.days.max = self.getDaysInMonth()

    def setYears(self, years):
        self.years.set(years)
        self._systemAdjust()

    def setMonths(self, months):
        self.months.set(months)
        self._systemAdjust()

    def setDays(self, days):
        self.days.add(days)
        self._systemAdjust()

    def addYears(self, years):
        self.years.add(years)
        self._systemAdjust()

    def addMonths(self, months):
        self.months.add(months)
        self._systemAdjust()

    def addDays(self, days):
        self.days.add(days)
        self._systemAdjust()

    def getAsMonths(self):
        return self.months.cascadeValue()

    def getAsDays(self):
        return self.days.cascadeValue()

    def __str__(self):
        return "%02d/%02d/%04d" % (
            self.getDays(), self.getMonths(), self.getYears())

    def __repr__(self):
        return str(self)


class DateTime(Date, Time):

    def __init__(self, dateObj=None, timeObj=None):
        dateObj = dateObj or Date()
        timeObj = timeObj or Time()
        self.years = dateObj.years
        self.months = dateObj.months
        self.days = dateObj.days
        self.hours = timeObj.hours
        self.hours.upper = self.days
        self.hours.max = 24
        self.hours.set(self.hours.getValue())
        self.minutes = timeObj.minutes
        self.seconds = timeObj.seconds
        self.milliseconds = timeObj.seconds
        self.time = timeObj
        self.date = dateObj

    def fromTimestamp(timestamp):
        i = timestamp
        t = time.localtime(i)
        d = Date(t.tm_year, t.tm_mon, t.tm_mday)
        tm = Time(t.tm_hour, t.tm_min, t.tm_sec, (i * 1000) % 1000)
        return DateTime(d, tm)
    fromTimestamp = staticmethod(fromTimestamp)

    def now():
        return DateTime.fromTimestamp(time.time())
    now = staticmethod(now)

    def getAsHours(self):
        return self.hours.cascadeValue()

    def getAsTimestamp(self):
        return time.mktime((
            self.getYears(), self.getMonths(), self.getDays(),
            self.getHours(), self.getMinutes(), self.getSeconds(),
            0, 0, 0
        ))

    def __str__(self):
        return "%s %s" % (self.time, self.date)
