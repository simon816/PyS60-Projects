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
  self.canvas=Canvas(redraw_callback=self.redraw,event_callback=self.event)
  self.draw=Draw(self.canvas)
  app.body=self.canvas
  self.canvas.clear(self.background)
 def redraw(self, frame=None):
  i=0
  for shape in self.shapes:
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
 def event(self,e):
  if e['scancode'] in self.b:
   if e['type']==EEventKey:
    self.b[e['scancode']]()

class shapeObject(object):
 def __init__(self,  name,arg=[],kw={}):
  self.kw=kw or {}
  self.arg=arg or []
  self.__name__=name
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



s=shapes()
s.create_body()
x,y=s.canvas.size
for h in range(1,5):
 for i in range(x/50):
  s.rectangle((50,50),(i*50+i,y-(h*50)-h),0x00DD00)
c=s.rectangle((50,90),(0,(50*4)-5),0xBBBBFF)
s.redraw(())
def j():
 c.move('down',60)
 s.update()
def k(d):
 if d=='up':
  for x in range(1,7):
   c.move(d,10)
   e32.ao_sleep(0.05)
  s.update()
  e32.ao_sleep(0.5,j)
 else:
  c.move(d,5)
 s.update()
s.b[17]=lambda:k('down')
s.b[16]=lambda:k('up')
s.b[14]=lambda:k('left')
s.b[15]=lambda:k('right')
"""Make checkerboard
size=20
gap=1
screen=s.canvas.size
off_x=0
i=0
color='black'
while off_x+size*2 < screen[0]:
 off_x=(i*size)+(i*gap)
 off_y=0
 i2=0
 while off_y+size*2 < screen[1]:
  off_y=(i2*size)+(i2*gap)
  if color=='white':
   color='black'
   mixer=i*5
   col=(mixer*off_x,mixer*off_x,mixer*off_x)
  else:
   color='white'
   mixer=i2*5
   col=(mixer*off_y,mixer*off_y,mixer*off_y)
  s.rectangle((size,size),(off_x,off_y),col)
  i2+=1
 i+=1
s.redraw(())
"""
s.lock.wait()