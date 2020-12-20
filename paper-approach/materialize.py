from res import *

def infer(abox, fact):
    if fact in abox:
        abox[fact] = (abox[fact][0], True)
    else:
        abox[fact] = (False, True)

def getClassObj(rdfClass, abox, abox2):
    objs = set()

    for axiom in abox.keys():
        if isinstance(axiom, ClassFact) and axiom.rdfClass == rdfClass:
            objs.add(axiom.indiv)

    for axiom in abox2:
        if isinstance(axiom, ClassFact) and axiom.rdfClass == rdfClass:
            objs.add(axiom.indiv)

    return objs

def filterClassObj(objs, resClass, abox, abox2):
    filtered = set()

    for o in objs:
        classfact = ClassFact(o, resClass)

        if classfact in abox.keys() or classfact in abox2:
            filtered.add(o)

    return filtered

# Refers to rule 1
def subClassRule(subClass, abox, abox2):
    if isinstance(subClass.subClass, ResInter):
        objs = getClassObj(subClass.subClass.first, abox, abox2)

        for rdfClass in subClass.subClass.list()[1:]:
            objs = filterClassObj(objs, rdfClass, abox, abox2)

    else:
        objs = getClassObj(subClass.subClass, abox, abox2)

    for o in objs:
        classfact = ClassFact(o, subClass.superClass)

        if classfact not in abox:
            abox2.add(classfact)

def getPropFact(pred, abox, abox2):
    facts = set()

    for axiom in abox.keys():
        if isinstance(axiom, PropFact) and axiom.pred == pred:
            facts.add(axiom)

    for axiom in abox2:
        if isinstance(axiom, PropFact) and axiom.pred == pred:
            facts.add(axiom)

    return facts

def materialize(tbox, abox):
    while True:
        abox2 = set()

        for t in tbox:
            if isinstance(t, SubClass):
                # Rule 1
                subClassRule(t, abox, abox2)
            else:
                op1, inv1 = t.op1()
                op2, inv2 = t.op2()

                facts = getPropFact(op1, abox, abox2)

                for fact in facts:
                    if inv1 == inv2:
                        # Rule 3
                        fact2 = PropFact(op2, fact.subj, fact.obj)
                    else:
                        # Rule 4
                        fact2 = PropFact(op2, fact.obj, fact.subj)

                    if fact2 not in abox and fact2 not in abox2:
                        abox2.add(fact2)

        for a in abox.keys():
            if isinstance(a, PropFact):
                # Rule 2
                subj = ClassFact(a.subj, ResRestr(a.pred))
                obj = ClassFact(a.obj, ResRestr(a.pred, True))

                if subj not in abox:
                    abox2.add(subj)
                if obj not in abox:
                    abox2.add(obj)

        if len(abox2) == 0:
            break

        for fact in abox2:
            infer(abox, fact)

# def inferFrom(fact, tbox, abox):
#     return True

# def inferTo(fact, tbox, abox):
#     if fact in abox:
        
