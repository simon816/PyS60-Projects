import struct,gzip
class InputStream:
  def __init__(self, filename):
    self.fh=open(filename)
  def read(self, *args):
    if not args or args[0]==1:
      return self.fh.read(1)
    if type(args[0]) is int:
      return self.fh.read(args[0])
    if type(args[0]) is list:
      d=fh.read(len(args[0]))
      for i in range(len(d)):
        args[0][i] = d[i]
  def close(self):
    self.fh.close()
  def readAll(self):
    return self.fh.read()
    
class DataInputStream:
  def __init__(self,instr):
    self.debug=0
    self._str=instr
  def __unpack(self,fmt):
    s=struct.calcsize(fmt)
    try:
      r=struct.unpack(fmt, self._str.read(s))[0]
    except struct.error:
      raise IOError("Could not unpack from data stream")
    if self.debug:
      print fmt,r
    return r
  def readFloat(self):
    return self.__unpack('>f')
  def readInt(self):
    return self.__unpack('>i')
  def read(self, l=1):
    if l==1:
      return self.__unpack('>B')
    return self._str.read(l)
  def readShort(self):
    return self.__unpack('>H')
  def readUTF(self):
    return unicode(self._str.read(self.readShort()))

class DataOutputStream:
  def __init__(self,outstr):
    self.f=outstr
  def close(self):
    self.f.close()
  def write(self, d):
    if type(d)==int:
      if d > 255:
        raise IOError()
      self.f.write(chr(d))
    else:
      self.f.write(d)
      """
    r=repr(d)
    if len(r)>200:
      print 'write',len(d),'bytes'
    else:
     print 'write', r"""
  def writeInt(self, i):
    self.write(struct.pack('>i', i))
  def writeFloat(self,f):
    self.write(struct.pack('>f', f))
  def writeShort(self, sh):
    self.write(struct.pack('>H', sh))
  def writeUTF(self, u):
    self.write(struct.pack('>H', len(u)))
    self.write(u)


class OutputStream:
  def __init__(self, filename):
    self.fh=open(filename, 'w')
  def write(self, bytes):
    self.fh.write(bytes)
  def close(self):
    self.fh.close()

class GZIPInputStream(InputStream):
  def __init__(self, filename):
    self.fh=gzip.open(filename)
    
class GZIPOutputStream(OutputStream):
  def __init__(self, filename):
    self.fh=gzip.GzipFile(filename='', fileobj=open(filename, 'wb'), mode='w')


