from appuifw import *
from graphics import *
import e32
class shapes:
 def __init__(self):
  self.lock=e32.Ao_lock()
  self.canvas=None
  self.running=0
  self.shape_id=0
  self.shapes=[]
  self.all_shapes={}
  self.b={}
  app.exit_key_handler=self.exit
  self.background=0xE4E4FF
 def create_body(self):
  from appuifw import Canvas
  self.canvas=Canvas(redraw_callback=self.redraw,event_callback=self.handle_event)
  self.draw=Draw(self.canvas)
  app.body=self.canvas
  self.canvas.clear(self.background)
  self.touch_handler = TouchHandler()
 def redraw(self, frame=None):
  i=0
  ontop=[]
  for shape in self.shapes:
    #if shape.top
   shape.canvas_draw()
   self.all_shapes[shape]=1
  self.shapes=[]
 def update(self):
  self.canvas.clear(self.background)
  self.shapes=self.all_shapes.keys()
  self.redraw()
 def exit(self):
  self.canvas=None
  self.lock.signal()

 def coord(self, dim, pos):
  x=dim[0]+pos[0]
  y=dim[1]+pos[1]
  return pos+(x,y)
  

 def rectangle(self,dim,pos=(0,0),color=0):
  obj=shapeObject('rectangle')
  obj.coords=self.coord(dim,pos)
  obj.color=color
  obj.draw=self.draw.rectangle
  self.shapes.append(obj)
  return obj
 def arc(self,dim,st,en):
  obj=shapeObject('arc')
  obj.coords=self.coord(dim,(0,0))
  obj.arg.extend([st,en])
  obj.draw=self.draw.arc
  self.shapes.append(obj)
  return obj
 def measure(self,text,font):
   s=self.draw.measure_text(text,font=font)
   return (s[0][2],(s[0][1]*-1)+s[0][3])
 def text(self,pos,text,color=None,font=None):
  obj=shapeObject('text')
  obj.coords=self.coord((0,0),pos)
  obj.arg.append(text)
  if font:obj.kw['font']=font
  if color:obj.kw['fill']=color
  obj.draw=self.draw.text
  self.shapes.append(obj)
  return obj
 def event(self,e):
   print e
   if 'scancode' in e:
     if e['scancode'] in self.b:
       if e['type']==EEventKey:
         self.b[e['scancode']]()
   elif 'pos' in e and e['type']==257:
     x,y=e['pos']
     for shape in self.all_shapes:
       c=shape.arg[0]
       if len(c)<4:continue
       if x in range(c[0],c[2]) and y in range(c[1],c[3]):
         shape.click(x-c[0],y-c[1])

 
 def handle_event(self, event):
      if event['type'] == 257:
          if self.touch_handler.is_held():
              self.touch_handler.release(None)
          self.touch_handler.press(event)
      elif event['type'] == 263:
          if not self.touch_handler.is_held():
              self.touch_handler.press(None)
          self.touch_handler.drag(event)
      elif event['type'] == 258:
          if not self.touch_handler.is_held():
              self.touch_handler.press(None)
          self.touch_handler.release(event)


class shapeObject(object):
 def __init__(self,  name,arg=[],kw={}):
  self.kw=kw or {}
  self.arg=arg or []
  self.__name__=name
  self.onclick=None
 def __repr__(self):
  return "shapeObject('%s',%s,%s)"%(self.__name__,str (self.arg),str(self.kw))
 def __setattr__(self, k, v):
  if k in ['color']:
   self.kw['fill']=v
  if k in ['coords']:
   self.arg.append(v)
  else:
   self.__dict__[k]=v
 def canvas_draw(self):
     #print 'draw', str(self)
     self.draw(*self.arg,**self.kw)
 def move(self, dir, step):
  c=list(self.arg[0])
  if dir=='right':
   c[0]+=step
   c[2]+=step
  elif dir=='left':
   c[0]-=step
   c[2]-=step
  elif dir=='up':
   c[1]-=step
   c[3]-=step
  elif dir=='down':
   c[1]+=step
   c[3]+=step
  self.arg[0]=tuple(c)
 def grow(self,size,time=0):
   l=list(self.arg[0])
   if type(size) == tuple:
     l[2]+=size[0]
     l[3]+=size[1]
   else:
     size=float(size)
     if time:
       final= int(l[2]*size)
       while l[2] < final:
         l[2]+=time/size
         l[3]+=time/size
         self.arg[0]=tuple(l)
         self.canvas_draw()
         e32.ao_sleep(0.001)
       return
     l[2]=int(l[2]*size)
     l[3]=int(l[3]*size)
   self.arg[0]=tuple(l)
   self.canvas_draw()
 def setColor(self,color):
   self.color=color
   self.canvas_draw()
 def click(self,x,y):
   if self.onclick:
     self.onclick(x,y)

class gridManager:
  class slice:
    def __call__(self,*args):
      r=[]
      for i in self.itms:
        r.append(i.__getattribute__(self.a)(*args))
      return tuple(r)
    def __init__(self,itms):
      self.itms=itms
    def __getattr__(self,a):
      self.a=a
      return self
    def __str__(self):
      return str(self.itms)
  def __init__(self,l=[]):
    self.list=l
  def append(self,obj):
    self.list.append(obj)
  def __getitem__(self,i):
    return self.list[i]
  def __getslice__(self,*slice):
    return self.slice(self.list.__getslice__(*slice))
  def __setitem__(self,i,o):
    self.list[i]=o
  def __len__(self):
    return len(self.list)
  def __str__(self):
    return str(self.list)
  def copy(self):
    return gridManager(self.list[:])

class EventHandler(object):
    def __init__(self):
        self.evt_pool = {}

    def on(self, evt_name, callback):
        self.subscribe(evt_name, callback)

    def subscribe(self, name, callback):
        if type(name) != str:
            raise TypeError('Event names can only be strings')
        if not hasattr(callback, '__call__'):
            raise TypeError('Callback must be callable')
        if name not in self.evt_pool:
            self.evt_pool[name] = []
        self.evt_pool[name].append(callback)

    def trigger(self, name, event):
        if not name in self.evt_pool:
            return False
            #raise KeyError('Unkown event \'%s\'' % name)
        for callback in self.evt_pool[name]:
            callback.__call__(event)
        return True

    def make_event(self, **kwargs):
        class Event(object):
            def __init__(self,**kw):self.__dict__=kw
            def __str__(self):return str(self.__dict__)
            def __repr__(self):return repr(self.__dict__)
        event = Event(**kwargs)
        return event

class TouchHandler(EventHandler):
    def __init__(self):
        super(TouchHandler, self).__init__()
        self.holding = False
        self.drag_points = []

    def press(self, event):
        self.holding = True
        self.trigger('press', event)

    def drag(self, event):
        self.holding = True
        self.trigger('move', event)
        self.drag_points.append(event['pos'])

    def release(self, event):
        self.holding = False
        self.trigger('release', event)
        if len(self.drag_points) == 0:
            tap_event = self.make_event(pos=event['pos'])
            self.trigger('tap', tap_event)
            return
        swipe_event = self.make_event(
            from_pos=self.drag_points[0],
            to_pos=self.drag_points[-1],
            direction=self.calc_swipe_dir(),
            path=self.drag_points[:])
        self.trigger('swipe', swipe_event)
        self.drag_points = []

    def is_held(self):
        return self.holding

    def calc_swipe_dir(self):
        if len(self.drag_points) == 0:
            return None
        move_x, move_y = 0, 0
        prev_pos = self.drag_points[0]
        for point in self.drag_points[1:]:
            move_x += point[0] - prev_pos[0]
            move_y += point[1] - prev_pos[1]
            prev_pos = point
        if abs(move_x) > abs(move_y):
            dir_names = ('left', 'right')
            move_axis = move_x
        elif abs(move_x) < abs(move_y):
            dir_names = ('up', 'down')
            move_axis = move_y
        else:
            return 'diagonal'
        if move_axis < 0: return dir_names[0]
        if move_axis > 0: return dir_names[1]
        return None

if __name__=='__main__':
  s=shapes()
  s.create_body()
  g=gridManager()
  g.append(s.rectangle((10,10)))
  g.append(s.rectangle((10,10),(15,0)))
  g.append(s.rectangle((10,10),(0,15)))
  g[0:2].canvas_draw()
  s.lock.wait()
