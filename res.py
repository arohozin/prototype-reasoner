class ResBot:
    def __str__(self):
        return "⊥"
    def __eq__(self, other):
        return isinstance(other, ResBot)
    def __hash__(self):
        return hash("⊥")

class ResUri:
    def __init__(self, uri):
        self.uri = str(uri)
    def __str__(self):
        return self.uri.split("#")[-1]
    def __eq__(self, other):
        return isinstance(other, ResUri) and self.uri == other.uri
    def __hash__(self):
        return hash(self.uri)

def resatom(string):
    print(string)
    if string == "http://www.w3.org/2002/07/owl#Nothing":
        return ResBot()
    return ResUri(string)

def interCompare(obj):
    return str(obj)

class ResInter:
    def __init__(self, first, rest):
        self.first = first

        if isinstance(rest, ResInter):
            lst = rest.list()
            lst.sort(key=interCompare)
            self.rest = ResInter(lst[0], lst[1:])
        elif isinstance(rest, list):
            if len(rest) == 1:
                self.rest = rest[0]
            else:
                self.rest = ResInter(rest[0], rest[1:])
        else:
            self.rest = rest
    def __str__(self):
        return str(self.first) + " ⨅ " + str(self.rest)
    def __eq__(self, other):
        return (isinstance(other, ResInter) and
                (self.first, self.rest) == (other.first, other.rest))
    def __hash__(self):
        return hash((self.first, self.rest))
    def list(self):
        if isinstance(self.rest, ResInter):
            return [self.first] + self.rest.list()
        return [self.first, self.rest]        

class ResInv:
    def __init__(self, pred):
        if isinstance(pred, ResInv):
            self.pred = pred.pred
        else:
            self.pred = pred
    def __str__(self):
        return str(self.pred) + "-"
    def __eq__(self, other):
        return isinstance(other, ResInv) and self.pred == other.pred
    def __hash__(self):
        return hash(self.pred)

class ResRestr:
    def __init__(self, pred, inverse=False):
        if inverse:
            self.pred = ResInv(pred)
        else:
            self.pred = pred
    def __str__(self):
        return "∃" + str(self.pred)
    def __eq__(self, other):
        return (isinstance(other, ResRestr) and self.pred == other.pred)
    def __hash__(self):
        return hash(self.pred)

class ClassFact:
    def __init__(self, indiv, rdfClass):
        self.rdfClass = rdfClass
        self.indiv = indiv
    def __str__(self):
        return str(self.rdfClass) + "(" + str(self.indiv) + ")"
    def __eq__(self, other):
        return (isinstance(other, ClassFact) and
                (self.rdfClass, self.indiv) == (other.rdfClass, other.indiv))
    def __hash__(self):
        return hash((self.rdfClass, self.indiv))

class PropFact:
    def __init__(self, pred, subj, obj):
        self.pred = pred
        self.subj = subj
        self.obj = obj
    def __str__(self):
        return str(self.pred) + "(" + str(self.subj) + ", " + str(self.obj) + ")"
    def __eq__(self, other):
        return (isinstance(other, PropFact) and
                (self.pred, self.subj, self.obj) ==
                (other.pred, other.subj, other.obj))
    def __hash__(self):
        return hash((self.pred, self.subj, self.obj))

class ClassSub:
    def __init__(self, subClass, superClass):
        self.subClass = subClass
        self.superClass = superClass
    def __str__(self):
        return str(self.subClass) + " ⊑ " + str(self.superClass)
    def __eq__(self, other):
        return (isinstance(other, ClassSub) and
                (self.subClass, self.superClass) ==
                (other.subClass, other.superClass))
    def __hash__(self):
        return hash((self.subClass, self.superClass))
    def left(self):
        return self.subClass
    def right(self):
        return self.superClass

class PropSub:
    def __init__(self, subProp, superProp):
        self.subProp = subProp
        self.superProp = superProp
    def __str__(self):
        return str(self.subProp) + " ≤ " + str(self.superProp)
    def __eq__(self, other):
        return (isinstance(other, PropSub) and
                (self.subProp, self.superProp) ==
                (other.subProp, other.superProp))
    def __hash__(self):
        return hash((self.subProp, self.superProp))
    def left(self):
        return self.subProp
    def right(self):
        return self.superProp
    def op1(self):
        if isinstance(self.subProp, ResInv):
            return self.subProp.pred, True
        return self.subProp, False
    def op2(self):
        if isinstance(self.superProp, ResInv):
            return self.superProp.pred, True
        return self.superProp, False
