import graphics
import e32
from sysinfo import display_pixels as scr
from topwindow import TopWindow

class loader:
 def __init__(self,img,ani_xy=100):
  self.status=0
  self.wait=0.01
  self.ani_xy=ani_xy
  self.img=graphics.Image.open(img).resize((self.ani_xy,self.ani_xy))
  self.gif=TopWindow()
  self.gif.size=(ani_xy, ani_xy)
  self.gif.position=self.get_mid((ani_xy,ani_xy))
  self.txt=TopWindow()
  self.blank=graphics.Image.new((1,1))
  self.ani_xy=ani_xy
 def get_mid(self, d):
  return ((scr()[0]-d[0])/2,(scr()[1]-d[1])/2)
 def addtext(self,text,update=0):
  size=self.img.measure_text(text)
  t_w,t_h=(size[0][2],(size[0][1]*-1)+size[0][3])
  self.text=graphics.Image.new((t_w,t_h))
  self.text.text((0,12), text)
  self.txt.size=(t_w,t_h)
  mid=self.get_mid((t_w,self.ani_xy))
  self.txt.position=(mid[0],mid[1]+self.ani_xy)
  if update:self.disp_text()
 def rotate(self):
  def rem():
   try:self.gif.remove_image(self.img, (0,0))
   except:pass
  e32.ao_sleep(self.wait,rem)
  self.img=self.img.transpose(graphics.ROTATE_90)
  self.gif.add_image(self.img, (0,0))
 def start(self):
  self.gif.show()
  self.txt.show()
  self.status=1
 def stop(self):
  self.gif.hide()
  self.txt.hide()
  self.status=0
 def disp_text(self):
  if not self.status:self.start()
  #self.txt.add_image(self.blank,(0,0))
  try:self.txt.remove_image(self.text);
  except ValueError,e:pass#print 'not removed e='+str(e)
  self.txt.images=[]
  self.txt.add_image(self.text,(0,0))
  self.gif.add_image(self.img, (0,0))
  del self.text
  self.rotate()
