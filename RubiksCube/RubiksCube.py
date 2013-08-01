from simon816.shapes import *
RED=(255,0,0)
GREEN=(0,200,0)
BLUE=(0,0,255)
YELLOW=(255,255,0)
WHITE=(255,255,255)
ORANGE=(255,140,0)
class RubiksCube:
  def __init__(self):
    self.s=shapes()
    self.g=gridManager()
    self.top='y'
    self.bottom='g'
    self.front='w'
    self.sides={
      'r':{
        'colors':[RED]*9,
        'left':'b','right':'w'
      },
      'g':{
        'colors':[GREEN]*9,
        'left':'r','right':'o'
      },
      'b':{
        'colors':[BLUE]*9,
        'left':'o','right':'r'
      },
      'y':{
        'colors':[YELLOW]*9,
        'left':'r','right':'o'
      },
      'o':{
        'colors':[ORANGE]*9,
        'left':'w','right':'b'
      },
      'w':{
        'colors':[WHITE]*9,
        'left':'r','right':'o'
      }
    }
  def siderepr(self):
    if self.side=='r':return 'Red'
    if self.side=='g':return 'Green'
    if self.side=='b':return 'Blue'
    if self.side=='y':return 'Yellow'
    if self.side=='o':return 'Orange'
    if self.side=='w':return 'White'
  def run(self):
    self.side='r'
    side=self.sides[self.side]['colors']
    s=100
    g=5
    c=(20,50)
    i=0
    self.s.create_body()
    def m(a,b):
      return lambda c,d:self.clicked(a,b,c,d)
    for rows in range(3):
      for cols in range(3):
        r=self.s.rectangle((s,s),(c[0]+(s+g)*cols,c[1]+(s+g)*rows),side[i])
        r.onclick=m(rows,cols)
        self.g.append(r)
        i+=1
    self.t=self.s.text((50,25),u'Current face: %s'%self.siderepr(),font='title')
    self.t.onclick=self.rt
    self.s.redraw()
    app.title=u'Rubiks Cube'
    app.menu=[
      (u'Left',lambda:self.clicked(1,0,0,0)),
      (u'Right',lambda:self.clicked(1,2,0,0)),
      (u'Top',lambda:self.clicked(0,1,0,0)),
      (u'Bottom',lambda:self.clicked(2,1,0,0)),
      (u'Middle',lambda:self.clicked(1,1,0,0)),
      (u'Rotate',lambda:self.rt(0,0))
    ]
    self.s.lock.wait()
  def rt(self,x,y):
    self.side=self.sides[self.side]['left']
    self.t.arg[1]=u'Current face: %s'%self.siderepr()
    self.update()
  def clicked(self, row, col, x, y):
    if row ==1 and col ==0:
      self.rotateFace(self.sides[self.side]['left'])
    if row ==0 and col ==1:
      self.rotateFace(self.top)
    if row ==1 and col ==2:
      self.rotateFace(self.sides[self.side]['right'])
    if row ==2 and col ==1:
      self.rotateFace(self.bottom)
    if row ==1 and col ==1:
      self.rotateFace(self.side)
    self.update()
  def update(self):
    i=0
    for c in self.sides[self.side]['colors']:
      #print self.g[i].color,c
      self.g[i].color=c
      i+=1
    self.s.update()
  def rotateFace(self,face):
    if face not in self.sides:
      raise Exception('Invalid face %r'%face)
    f=self.sides[face]
    c=f['colors']
    n=[]
    n.append(c[6])
    n.append(c[3])
    n.append(c[0])
    n.append(c[7])
    n.append(c[4])
    n.append(c[1])
    n.append(c[8])
    n.append(c[5])
    n.append(c[2])
    self.sides[face]['colors']=n
    self._print(c,n)
    fl=self.sides[f['left']]
    fr=self.sides[f['right']]
    ft=self.sides[self.top]
    fb=self.sides[self.bottom]
    cl=fl['colors']
    cl[2]=fb['colors'][6]
    cl[5]=fb['colors'][1]
    cl[8]=fb['colors'][0]
    ct=ft['colors']
    ct[6]=fl['colors'][8]
    ct[7]=fl['colors'][5]
    ct[8]=fl['colors'][2]
    cr=fr['colors']
    cr[0]=ft['colors'][6]
    cr[3]=ft['colors'][7]
    cr[6]=ft['colors'][8]
    cb=fb['colors']
    cb[0]=fr['colors'][6]
    cb[3]=fr['colors'][3]
    cb[6]=fr['colors'][0]
    fl['colors']=cl
    ft['colors']=ct
    fr['colors']=cr
  def prcl(self,t):
    for k,v in globals().iteritems():
      if v == t:
        return k
    return str(t)
  def _print(self,*args):
    for f in args:
      print '|'.join(map(self.prcl,f[0:3]))+'\n'
      print '|'.join(map(self.prcl,f[3:6]))+'\n'
      print '|'.join(map(self.prcl,f[6:9]))+'\n\n'
r=RubiksCube()
r.run()
#print r.sides