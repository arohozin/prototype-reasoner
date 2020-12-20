from res import *
from database import *

def checkClassRules(cur, indiv, superClass, looking, found):
    rules = dbClassSubBySuper(cur, superClass)

    for rule in rules:
        if checkClass(cur, indiv, rule.subClass, looking, found):
            return True

    return False

def checkClassAtom(cur, indiv, atom, looking, found):
    classfact = ClassFact(indiv, atom)

    if dbContains(cur, classfact):
        found.add(classfact)
        return True

    return checkClassRules(cur, indiv, atom, looking, found)

def checkClassInter(cur, indiv, inter, looking, found):
    return (checkClass(cur, indiv, inter.first, looking, found) and
            checkClass(cur, indiv, inter.rest, looking, found))

def checkClassRestr(cur, indiv, restr, looking, found):
    if isinstance(restr.pred, ResInv):
        if dbInRange(cur, restr.pred.pred, indiv):
            found.add(restr)
            return True
    elif dbInDomain(cur, restr.pred, indiv):
        found.add(restr)
        return True

    if checkClassRules(cur, indiv, restr, looking, found):
        return True

    if isinstance(restr.pred, ResInv):
        rules = dbPropSubBySuper(cur, restr.pred.pred)

        for rule in rules:
            if checkClassRestr(cur, indiv, ResRestr(rule.subProp, True),
                               looking, found):
                return True
    else:
        rules = dbPropSubBySuper(cur, restr.pred)

        for rule in rules:
            if checkClassRestr(cur, indiv, ResRestr(rule.subProp),
                               looking, found):
                return True

    return False
    

def checkClass(cur, indiv, rdfClass, looking=None, found=None):
    funcs = {
        ResInter: checkClassInter,
        ResRestr: checkClassRestr,
        ResUri: checkClassAtom,
        ResBot: checkClassAtom,
    }

    if looking == None:
        looking = set()

    if found == None:
        found = set()

    if rdfClass in found:
        return True

    if rdfClass in looking:
        return False

    looking.add(rdfClass)

    return funcs[type(rdfClass)](cur, indiv, rdfClass, looking, found)

def checkProp(cur, pred, subj, obj, looking=None):
    if dbContains(cur, PropFact(pred, subj, obj)):
        return True

    if looking is None:
        looking = set()

    looking.add(pred)
    facts = dbPropSubBySuper(cur, pred)

    for fact in facts:
        if fact.subProp in looking:
            continue

        if checkProp(cur, fact.subProp, subj, obj, looking):
            return True

    return False
