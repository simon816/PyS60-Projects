class Node:
    def __init__(self, label):
        self.label = label

    def __str__(self):
        return 'Node(%s)' % self.label
    def __repr__(self):
        return str(self)

class Link:
    def __init__(self, node1, node2, weight=None):
        self.n1 = node1
        self.n2 = node2
        self.w = weight

class Tree:
    def __init__(self, *links):
        self.links = links

    def route(self, from_, to):
        start = NodeMarker(self.links[0].n1, 0)
        self.p = [start.n]
        adj = self.getAdjNodes(start)
        print start
        while adj.hasNodes():
            next = adj.shortest(pop=True)
            next.permanent()
            self.p.append(next.n)
            print next
            if next.n == to:
                break
            adj.combine(self.getAdjNodes(next))
        
    def getAdjNodes(self, node):
        nodes = []
        for link in self.links:
            if link.n1 == node.n and not link.n2 in self.p:
                nodes.append((link.n2, link.w))
            elif link.n2 == node.n and not link.n1 in self.p:
                nodes.append((link.n1, link.w))
        return NodeList(nodes)

class NodeList:
    def __init__(self, nodes):
        self.nodes = nodes

    def shortest(self, pop=False):
        closest = self.nodes[0]
        for node in self.nodes[1:]:
            if node[1] < closest[1]:
                closest  = node
        if pop:
            self.nodes.remove(closest)
        return NodeMarker(closest[0], closest[1])

    def combine(self, nList):
        self.nodes.extend(nList.nodes)
    def hasNodes(self):
        return len(self.nodes) > 0

    def __str__(self):
        return 'NodeList(%s)' % self.nodes

class NodeMarker:
    def __init__(self, node, weight):
        self.n = node
        self.w = weight
        self.p = False
    def __str__(self):
        return 'Marker[node=%s,weight=%s]' % (self.n, self.w)


    def permanent(self):
        self.p = True

A = Node('A')
B = Node('B')
C = Node('C')
D = Node('D')

T = Tree(
    Link(A, B, weight=2),
    Link(B, C, weight=5),
    Link(A, C, weight=3),
    Link(C, D, weight=1)
)
T.route(A, D)