class Component(object):
    def __init__(self, value):
        if type(value) not in [int, float]:
            raise TypeError('Component must be a number')
        self.value = value

    def getValue(self, **kw):
        return self.value

    def __repr__(self, indent=0):
        return (' ' * indent) + repr(self.value) + '\n'

    def __str__(self):
        return str(self.value)

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        return self.value == other.value


class Holder(Component):
    def __init__(self, *components):
        self.components = []
        self.extend(*components)

    def extend(self, *components):
        for component in components:
            if not isinstance(component, Component):
                component = Component(component)
            self.components.append(component)
        return self

    def getValue(self, **kw):
        value = 0
        for component in self.components:
            value += component.getValue(**kw)
        return value

    def __repr__(self, indent=0):
        spaces = ' ' * indent
        return spaces + self.__class__.__name__ + ' {\n' + ''.join(map(lambda c:c.__repr__(indent + 4), self.components)) + spaces + '}\n'

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        return self.components == other.components



class Operation(Holder):
    def operate(self, a, b):
        raise NotImplementedError("cannot operate a " + self.__class__.__name__ + " operation")

    def getValue(self, **kw):
        value = self.components[0].getValue(**kw)
        for component in self.components[1:]:
            value = self.operate(value, component.getValue(**kw))
        return value

    def getSymbol(self):
        raise NotImplementedError("No symbol defined for " + self.__class__.__name__)

    def __str__(self):
        return '(%s)' % (' ' + self.getSymbol() + ' ').join(map(str, self.components))

class Multiply(Operation):
    def operate(self, a, b):
        return a * b

    def getSymbol(self):
        return '*'


class Add(Operation):
    def operate(self, a, b):
        return a + b

    def getSymbol(self):
        return '+'


class Subtract(Operation):
    def operate(self, a, b):
        return a - b

    def getSymbol(self):
        return '-'


class Divide(Operation):
    def operate(self, a, b):
        result = float(a) / float(b)
        if result == int(result):
            return int(result)
        return result

    def getSymbol(self):
        return '/'


class Power(Operation):
    def operate(self, a, b):
        return a ** b

    def getSymbol(self):
        return '^'


class Variable(Component):
    def __init__(self, name):
        self.name = name

    def getValue(self, **kw):
        return kw[self.name]

    def __repr__(self, indent=0):
        return (' ' * indent) + self.__class__.__name__ + '(' + str(self.name) + ')\n'

    def __str__(self):
        return str(self.name)

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        return self.name == other.name




class Function(Holder):
    def __init__(self, name, *variables):
        super(Function, self).__init__()
        self.name = name
        self.variables = []
        for variable in map(str, variables):
            if variable in self.variables != -1:
                raise Exception("Duplicate variable name '" +  variable + "'")
            self.variables.append(variable)

    def __call__(self, *variables):
        if len(variables) is not len(self.variables):
            raise NameError("variable mismatch")
        kw = {}
        for i in range(len(self.variables)):
            kw[self.variables[i]] = variables[i]
        return self.getValue(**kw)

    def __getitem__(self, variables):
        if type(variables) is not tuple:
            variables = (variables,)
        return self.__call__(*variables)

    def __repr__(self, indent=0):
        title = 'Function[%s] (%s)' % (self.name, ', '.join(self.variables))
        spaces = ' ' * indent
        return spaces + title + ' {\n' + ''.join(map(lambda c:c.__repr__(indent + 4), self.components)) + spaces + '}\n'

    def __str__(self):
        return '%s(%s) = %s' % (self.name, ', '.join(map(str, self.variables)), ''.join(map(str, self.components)))

    def __eq__(self, other):
        return super(Function, self).__eq__(other) and self.name == other.name and self.variables == other.variables

f = Function('f', 'x')

f.extend(
    Power(Variable('x'), 2)
)

def getOperation(op):
    if op == '*':
        return Multiply()
    elif op == '+':
        return Add()
    elif op == '/':
        return Divide()
    elif op == '-':
        return Subtract()
    elif op == '^':
        return Power()
    else:
        raise TypeError("Unknown operation '%s'" % op)

BIDMAS = ('()', '^', '/', '*', '+', '-')

def parse(s):
    import re
    decl, func = re.split('\s*=\s*', s)
    name, varStr = re.match('([A-Za-z]+)\s*\((.+)+\)', decl).groups()
    vars = re.split('\s*,\s*', varStr)
    function = Function(name, *vars)
    level = 0
    expect = 'value'
    components = {}
    operations = {}
    for m in re.finditer('(?:(?P<var>[A-Za-z]+)|(?P<op>[\*+/\^]|-(?!\d))|(?P<num>(?:-)?(?:\d+\.\d+|\d+))|(?P<bracket>[\(\[]|[\)\]]))', func):
        if len(m.groups()) - list(m.groups()).count(None) is not 1:
            raise Exception("Invalid Expression: Match multiple groups")
        bracket = m.group('bracket')
        if not level in components:
            components[level] = None
        if not level in operations:
            operations[level] = None
        component = components[level]
        operation = operations[level]
        if bracket in ['(', '[']:
            level += 1
            #print 'inc', repr(operation)
            #operation = None
        elif bracket in [')', ']']:
#            if operation is not None:
 #               component = operation
  #              operation = None
            operations[level] = None
            level -= 1
            #print 'drop', component
            if operation is not None:
                if operations[level] is not None:
                    operations[level].extend(operation)
                else:
                    components[level] = operation
            if component is not None:
                if components[level] is not None:
                    components[level].extend(component)
                else:
                    components[level] = component
        if bracket is not None:
            continue
        var = m.group('var')
        num = m.group('num')
        op = m.group('op')

        if expect == 'value':
            if var is not None:
                component = Variable(var)
            elif num is not None:
                component = float(num)
                if int(component) == component:
                    component = int(num)
            else:
                raise Exception("Invalid Exression: expecting value")
            if operation is not None:
                #print 'extend', repr(operation), component
                operation.extend(component)
                component = None
            expect = 'operation'
        elif expect == 'operation':
            if op is None:
                if var is None:
                    raise Exception("Invalid Expression: expecting operation")
                op = '*'
            if operation is None or op != operation.getSymbol():
                oldop = operation
                operation = getOperation(op)
                if oldop:
                    operation.extend(oldop)
            if component is not None:
                operation.extend(component)
            component = None
            if var is not None:
                operation.extend(Variable(var))
                expect = 'operation'
            else:
                expect = 'value'
        components[level] = component
        operations[level] = operation
    if level is not 0:
        raise Exception("Invalid Expression")
    #print components, operations
    if components[0] is not None:
        function.extend(components[0])
    if operations[0] is not None:
        function.extend(operations[0])
    return function

Function('f', 'x').extend(Add(1,2), Subtract(3,4))

while False:
    s = 'f(x) = ' + raw_input('f(x) = ')
    try:
        print parse(s)
    except KeyboardInterrupt:
        break
    except Exception, e:
        print e
        pass

f = parse('f(x) = ((x ^ -2.1) - -3)')
g = parse('g(x) = (x^3)+(2*(x^2)) + (6x) - 3')
if __name__ == '__main__':
    class Env(dict):
        def __init__(self):
            super(Env, self).__init__(globals())
        def __getitem__(self, a):
            print a
            return super(Env, self).__getitem__(a)
        def __setitem__(self, a, v):
            print a
            globals()[a] = v
    from simon816.console import Console
    m = Console()
    env =Env()
    m.console('> ')
    m.bodystyle['input'] = {
        'font-size': 20
    }
    m.bodystyle['printer'] = {
        'font-size': 20,
        'color': '#0000FF'
    }
    m.bodystyle['output'] = {
        'font-size': 17,
        'color': '#Ff7f00',
        'font-weight': 'bold',
        'font-style': 'italic'
    }
    def e(c):
        if c.startswith('structure'):
            m.output(repr(globals()[c.split(' ')[1]]))
            return
        try:
            __f = parse(c)
            globals()[__f.name] = __f
            print __f
        except:
            exec '__ret = ' + c in env
            print env['__ret']
    m.bind('exec_cmd', e)
    m.shell_run('structure f')
    c = Console()
    c.console('-> ')
    def do(s):
        try:
            f = parse(s)
            print ('%r%s' % (f, f)).replace('\\n', '\n')
        except Exception, e:
            import sys
            sys.stderr.write(str(e) + '\n')
    c.bind('exec_cmd', do)
    #c.shell_run('f(x) = ')
    