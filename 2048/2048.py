import random
import appuifw

from simon816 import shapes

class Column(object):
    pass

class GridCell(object):
    WIDTH = 80
    HEIGHT = 80
    MARGIN = 10

    def __init__(self, shape_factory, x, y):
        self.rect = shape_factory.rectangle(
            (self.WIDTH, self.HEIGHT),
            (x * (self.WIDTH + self.MARGIN), y * (self.HEIGHT + self.MARGIN)),
            0xFAFAFA)
        self.x, self.y, self.shape_factory = x, y, shape_factory
        self.value = 0
        self.text = None

    def setNumber(self, num):
        self.value = num
        if self.text and 1:
            #print self.text
            shapes = self.shape_factory.all_shapes
            if self.text in shapes:
                del shapes[self.text]
            #print self.shape_factory.all_shapes
            shapes = self.shape_factory.shapes
            if self.text in shapes:
                del shapes[shapes.index(self.text)]
            #print self.shape_factory.shapes
            self.text = None
        if num == 0:
            return
        print num, (self.x, self.y)
        num = unicode(num)
        font = (None, self.HEIGHT / max(3-(4-len(num)),1), 0)
        w, h =  self.shape_factory.measure(num, font)
        self.text = self.shape_factory.text(
            (self.x * (self.WIDTH + self.MARGIN) - (w/2) + (self.WIDTH / 2), self.y * (self.HEIGHT + self.MARGIN) + (h/2) + (self.HEIGHT / 2)),
            num,
            0x5050FF,
            font)
    def __str__(self):
        return 'Cell(%s)' % self.value

cells = []

def print_grid(cells=cells):
    for x in range(len(cells)):
        print map(str, cells[x])

appuifw.app.screen = 'large'
appuifw.app.directional_pad = False

s = shapes.shapes()

s.create_body()
def swipped(event):
    print event.direction
    #moved = []
    do_x = lambda x: x
    do_y = lambda y: y
    if event.direction == 'left':
        do_x = lambda x: x - 1
    elif event.direction == 'right':
        do_x = lambda x: x + 1
    elif event.direction == 'up':
        do_y = lambda y: y - 1
    elif event.direction == 'down':
        do_y = lambda y: y + 1
    else:
        return
    for x in range(4):
        for y in range(4):
            #if (x, y) in moved:
            #    continue
            dx, dy = do_x(x), do_y(y)
            if dy < 0 or dx < 0 or dx > 3 or dy > 3:
                continue
            adj = cells[dx][dy]
            cell = cells[x][y]
            if cell.value == 0:
                continue
            while adj.value == 0:
                print (x,y), (dx,dy)
                print 'move free space'
                adj.setNumber(cell.value)
                cell.setNumber(0)
                #moved.append((dx, dy))
                #continue
                dx, dy = do_x(dx), do_y(dy)
                if dy < 0 or dx < 0 or dx > 3 or dy > 3:
                    break
                cell = adj
                adj = cells[dx][dy]
            if adj.value != cell.value:
                continue
            print (x,y), (dx,dy)
            print 'merge value'
            adj.setNumber(adj.value * 2)
            cell.setNumber(0) 
    s.redraw()
    s.update()
    for sh in s.all_shapes.keys():
        if sh.__name__ == 'text':
            sh.canvas_draw()
    def p(a):print a
    #map(p, old)
    #print_grid()
    randcell()
s.touch_handler.on('swipe', swipped)


for x in range(4):
    cells.append([])
    for y in range(4):
        cells[x].append(GridCell(s, x, y))

def randcell():
    rx, ry = random.randint(0, 3), random.randint(0, 3)
    while cells[rx][ry].value != 0:
        rx, ry = random.randint(0, 3), random.randint(0, 3)
    cells[rx][ry].setNumber(2)

def swipped_e(d):
    swipped(s.touch_handler.make_event(direction=
        d))

def s_up():
    swipped_e('up')
def s_left():
    swipped_e('left')
def s_down():
    swipped_e('down')
def s_right():
    swipped_e('right')

appuifw.app.menu = [(u'Up', s_up), (u'Left', s_left), (u'Down', s_down), (u'Right', s_right)]
randcell()
s.redraw()
#print_grid()
s.lock.wait()