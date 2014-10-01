import re
class CSV:
    def __init__(self, filename, has_header=True):
        self.f = open(filename)
        self.sep = ','
        self.quote = '\s*"(.*)"\s*'
        if has_header:
            #self.data = dict(map(lambda e:(e, []), self.read_entry()))
            self.head =  self.read_entry()
    def read_entry(self):
         line = '"'+self.f.readline()
         entries = line.strip().split(self.sep)
         r = []
         for entry in entries:
             m = re.match(self.quote, entry)
             if m:
                 r.append(m.group(1))
             else:
                 print line
         return r
    def close(self):
         self.f.close()
    def table(self, filename):
        f=open(filename, 'w')
        t = ['table']
        t.extend(['tr'] + map(lambda e:'th>'+e+'</th', self.head)+['/tr'])
        while self.f.read(1) != '':
            t.extend(['tr'] + map(lambda e:'td>'+e+'</td', self.read_entry())+['/tr'])
        f.write('\n'.join(map(lambda e:'<'+e+'>', t)))
        f.close()

if __name__ == '__main__':
    c=CSV('e:\\classes.csv')
    c.table('e:\\classes.html')
    c.close()