import check
from res import *
from database import *

def findCheck(cur, indiv, rdfClass, indivDat):
    if indiv not in indivDat:
        indivDat[indiv] = [set(), set()]

    return check.checkClass(cur, indiv, rdfClass,
                            indivDat[indiv][0], indivDat[indiv][0])

def findClassRules(cur, superClass, indivs, indivDat):
    rules = dbClassSubBySuper(cur, superClass)

    for rule in rules:
        findClass(cur, rule.subClass, indivs, indivDat)

def findClassAtom(cur, atom, indivs, indivDat):
    facts = dbClassFactByClass(cur, atom)

    for fact in facts.keys():
        indivs.add(fact.indiv)
    
    findClassRules(cur, atom, indivs, indivDat)

def findClassInterStep(cur, inter, tmp, indivDat):
    if len(tmp) == 0:
        return tmp

    tmp2 = set()

    if isinstance(inter, ResInter):
        for indiv in tmp:
            if findCheck(cur, indiv, inter.first, indivDat):
                tmp2.add(indiv)
        return findClassInterStep(cur, inter.rest, tmp2, indivDat)

    for indiv in tmp:
        if findCheck(cur, indiv, inter, indivDat):
            tmp2.add(indiv)
    return tmp2

def findClassInter(cur, inter, indivs, indivDat):
    tmp = set()
    findClass(cur, inter.first, tmp, indivDat)
    tmp2 = findClassInterStep(cur, inter.rest, tmp, indivDat)
    indivs.update(tmp2)


def findClassRestr(cur, restr, indivs, indivDat):
    if isinstance(restr.pred, ResInv):
        facts = dbPropFactByPred(cur, rest.pred.pred)

        for fact in facts:
            indivs.add(cur, fact.obj)

    else:
        facts = dbPropFactByPred(cur, rest.pred)

        for fact in facts:
            indivs.add(cur, fact.subj)

    findClassRules(cur, restr, indivs, indivDat)

    if isinstance(restr.pred, ResInv):
        rules = dbPropSubBySuper(cur, restr.pred.pred)

        for rule in rules:
            findClassRestr(cur, ResRestr(rule.subProp, True),
                           indivs, indivDat)
    else:
        rules = dbPropSubBySuper(cur, restr.pred)

        for rule in rules:
            findClassRestr(cur, indiv, ResRestr(rule.subProp),
                           indivs, indivDat)

def findClass(cur, rdfClass, indivs=None, indivDat=None):
    funcs = {
        ResInter: findClassInter,
        ResRestr: findClassRestr,
        ResUri: findClassAtom,
        ResBot: findClassAtom,
    }

    if indivs is None:
        indivs = set()

    if indivDat is None:
        indivDat = {}

    funcs[type(rdfClass)](cur, rdfClass, indivs, indivDat)
    return indivs

def findIncon(cur, indivs=None, indivDat=None):
    return findClass(cur, ResBot(), indivs, indivDat)

def findPropForPred(cur, pred, looking=None, indivs=None):
    if indivs is None:
        indivs = set()

    if looking is not None:
        if pred in looking:
            return indivs
        looking.add(pred)
    else:
        looking = set()
        

    facts = dbPropFactByPred(cur, pred)

    for fact in facts.keys():
        indivs.add((fact.subj, fact.obj))

    facts = dbPropSubBySuper(cur, pred)

    for fact in facts:
        findPropForPred(cur, fact.subprop, looking, indivs)

    return indivs

def propSubForPredObj(cur, pred, obj, indivs):
    if (pred, obj) in indivs:
        return

    indivs.add((pred, obj))
    facts = dbPropSubBySub(cur, pred)

    for fact in facts:
        propSubForPredObj(cur, fact.superProp, obj, indivs)

def findPropForSubj(cur, subj, indivs=None):
    if indivs is None:
        indivs = set()

    facts = dbPropFactBySubj(cur, subj)

    for fact in facts.keys():
        propSubForPredObj(cur, fact.pred, fact.obj, indivs)

    return indivs

def propSubForPredSubj(cur, pred, subj, indivs):
    if (pred, subj) in indivs:
        return

    indivs.add((pred, subj))
    facts = dbPropSubBySub(cur, pred)

    for fact in facts:
        propSubForPredSubj(cur, fact.superProp, subj, indivs)

def findPropForObj(cur, obj, indivs=None):
    if indivs is None:
        indivs = set()

    facts = dbPropFactByObj(cur, obj)

    for fact in facts.keys():
        propSubForPredSubj(cur, fact.pred, fact.subj, indivs)

    return indivs

def findPropForPredSubj(cur, pred, subj, looking=None, indivs=None):
    if indivs is None:
        indivs = set()

    if looking is not None:
        if pred in looking:
            return indivs
        looking.add(pred)
    else:
        looking = set()
        

    facts = dbPropFactByPredSubj(cur, pred, subj)

    for fact in facts.keys():
        indivs.add(fact.obj)

    facts = dbPropSubBySuper(cur, pred)

    for fact in facts:
        findPropForPredSubj(cur, fact.subprop, subj, looking, indivs)

    return indivs

def findPropForPredObj(cur, pred, obj, looking=None, indivs=None):
    if indivs is None:
        indivs = set()

    if looking is not None:
        if pred in looking:
            return indivs
        looking.add(pred)
    else:
        looking = set()
        

    facts = dbPropFactByPredObj(cur, pred, obj)

    for fact in facts.keys():
        indivs.add(fact.subj)

    facts = dbPropSubBySuper(cur, pred)

    for fact in facts:
        findPropForPredObj(cur, fact.subprop, obj, looking, indivs)

    return indivs

def propSubForPred(cur, pred, indivs):
    if pred in indivs:
        return

    indivs.add(pred)
    facts = dbPropSubBySub(cur, pred)

    for fact in facts:
        propSubForPred(cur, fact.superProp, indivs)

def findPropForSubjObj(cur, subj, obj, indivs=None):
    if indivs is None:
        indivs = set()

    facts = dbPropFactBySubjObj(cur, subj, obj)

    for fact in facts.keys():
        propSubForPred(cur, fact.pred, indivs)

    return indivs
