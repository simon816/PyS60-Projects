from simon816.DiffReader import DifferenceReader
import difflib
from simon816.util import select
import appuifw, e32
items=[
  (u'Select file 1',u''),
  (u'Select File 2',u'')
  ]
def click():
  f=select('file')
  i=list(items[lb.current()])
  i[1]=unicode(f)
  items[lb.current()]=tuple(i)
  lb.set_list(items)
lb=appuifw.Listbox(items,click)
appuifw.app.body=lb
def go():
  m=appuifw.app.menu
  dr=DifferenceReader()
  f1=open(items[0][1])
  f2=open(items[1][1])
  t1=f1.readlines()
  t2=f2.readlines()
  f1.close()
  f2.close()
  diff=difflib.unified_diff(t1,t2)
  difftext='\n'.join([l for l in diff][2:])
  diffs=dr.parseDifference(difftext)
  dr.setTextToDiff(diffs,dr._createTextObj())
  dr._lockThreadAndDisplay()
  appuifw.app.menu=m
appuifw.app.menu=[
  (u'Go',go)
  ]
lk=e32.Ao_lock()
appuifw.app.exit_key_handler=lk.signal
lk.wait()