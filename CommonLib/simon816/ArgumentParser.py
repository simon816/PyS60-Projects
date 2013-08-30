from shlex import split as argsplit
class ArgumentParser:
 class InvalidArgument(Exception):pass
 class ExistsError(Exception):pass
 class ParseError(Exception):pass
 def __init__(self):
  self.args={}
 def createArgument(self,**properties):
  """ creates an argument object """
  # quick note: requiresdata attribute has 3 states
  # 0: never a data flag
  # 1: optional data flag
  # 2: must have data
  class Argument:
   def __init__(self,properties):
    for manditory in ['name','requiresdata']:
      if not manditory in properties:
       raise self.InvalidArgument('Missing attribute %r'%manditory)
    self.__dict__['props']=properties
   def __getattr__(self,attr):
    try:return self.__dict__['props'][attr]
    except KeyError:raise AttributeError
   def __setattr__(self,k,v):
    self.__dict__['props'][k]=v
   def __delattr__(self,attr):
    del self.props[attr]
   def __repr__(self):
    return '<Argument %r>'%self.name
  return Argument(properties)
 def RegisterArgument(self, argument):
  name=argument.name
  if name in self.args:
   raise self.ExistsError('argument %r already exists'%name)
  self.args[name]=argument
  if hasattr(argument, 'aliases'):
   for al in [a for a in argument.aliases]:
    if al in self.args:
     raise self.ExistsError('argument %r already exists while trying to add alias for %r'%(al,name))
    self.args[al]=argument
 def listArguments(self):
  lst=[]
  for arg,info in self.args.iteritems():
   if info.name != arg: # must be an alias
    continue
   fullarg=[arg]
   if hasattr(info,'aliases'):fullarg.extend(info.aliases)
   lst.append(fullarg)
  return lst
 def Parse(self,args):
  class ParsedArgument:
   def __init__(self,name,values):
    self.name=name
    self.values=values
   def last(self):
    return self.values[-1]
   def first(self):
    return self.values[0]
   def Values(self):return self.values
   def join(self,key=','):
    return key.join(self.values)
   def __repr__(self):
    return str(self.values)
  try:all=argsplit(str(args))
  except ValueError:
   raise self.ParseError('An error was encountered while trying to parse arguments')
  keys={'UNKNOWN':[]}
  stats={'argcount':len(all),'argorder':[],'argsmerged':{}}
  action=['next']
  def next(arg,action):
   if arg in self.args:
    data=self.args[arg]
    if data.name not in keys:
     keys[data.name]=ParsedArgument(arg,[])
    stats['argsmerged'][arg]=data.name
    if data.requiresdata:
     action=['jointo',data.name,arg]
   else:keys['UNKNOWN'].append(arg)
   return action
  for arg in all:
   stats['argorder'].append(arg)
   if action[0]=='next':
    action=next(arg,action)
   elif action[0]=='jointo':
    name=action[1]
    if arg in self.args and self.args[name].requiresdata==1:
     # the rule is if the argument is already registered and the previous 
     # argument was only optionally requiring data, assume it should skip
     # this would fail if eg an argument '--user' optionally wanted a username
     # and the username was of another argument say '--guest' was the
     # username and also a registered argument
     action=next(arg,action)
    else:
     keys[name].values.append(arg)
     action=['next']
  if action[0]=='jointo':
   if self.args[action[1]].requiresdata==2:
    raise AttributeError('Argument %r must have an attribute'%action[2])
  if not keys['UNKNOWN']:
   del keys['UNKNOWN']
  return keys,stats

 def getArgument(self,name):
  if not name in self.args:
   raise ValueError('Unknown argument %r'%name)
  return self.args[name]