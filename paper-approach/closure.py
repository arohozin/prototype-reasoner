#! /bin/python3
import rdflib
import parse
from collections import defaultdict
from res import *

def positiveClosure(tbox):
    pc = set()
    used = set()
    rhs = defaultdict(list)

    # add positive inclusion axioms
    for axiom in tbox:
        if not(isinstance(axiom, SubClass) and axiom.superClass == ResBot()):
            pc.add(axiom)
            rhs[axiom.right()].append(axiom.left())

    while True:
        pc2 = set()

        for axiom in pc:
            left = axiom.left()
            if isinstance(left, ResInter):
                if left not in used:
                    for B in left.list():
                        rel = SubClass(left, B)
                        if rel not in pc and rel not in pc2:
                            pc2.add(rel)
                            rhs[B].append(left)
                    used.add(left)

                rhsReplace(rhs, pc, pc2, set(), left, axiom.right())
            elif isinstance(axiom, SubProperty) and axiom not in used:
                right = axiom.right()
                rel = SubClass(ResRestr(left, False), ResRestr(right, False))
                relinv = SubClass(ResRestr(left, True), ResRestr(right, True))

                if rel not in pc and rel not in pc2:
                    pc2.add(rel)
                    rhs[rel.right()].append(rel.left())
                if relinv not in pc:
                    pc2.add(relinv)
                    rhs[rel.right()].append(rel.left())

                used.add(axiom)

        if len(pc2) == 0:
            break

        pc.update(pc2)
    return pc

def resCompare(obj):
    return str(obj)

def setInter(s):
    lst = list(s)
    lst.sort(key=resCompare)
    prev = None
    for B in lst:
        if prev is not None:
            prev = ResInter(B, prev)
        else:
            prev = B
    return prev

def pcClassSub(tmp, pc, pc2, subClass, superClass):
    if isinstance(superClass, ResInter):
        pcClassSub(tmp, pc, subClass, superClass.first)
        pcClassSub(tmp, pc, subClass, superClass.rest)
    else:
        rel = SubClass(subClass, superClass)
        if rel not in pc and rel not in pc2:
            pc2.add(rel)
            tmp.append(rel)

def rhsReplace(rhs, pc, pc2, prior, rest, right):
    if isinstance(rest, ResInter):
        copy = prior.copy()
        copy.add(rest.first)
        lst = rhsReplace(rhs, pc, pc2, copy, rest.rest, right)

        for B in rhs[rest.first]:
            copy = prior.copy()
            if isinstance(B, ResInter):
                for B2 in B.list():
                    copy.add(B2)
            else:
                copy.add(B)
            rhsReplace(rhs, pc, pc2, copy, rest.rest, right)
    else:
        copy = prior.copy()
        copy.add(rest)
        tmp = []
        pcClassSub(tmp, pc, pc2, setInter(copy), right)

        for B in rhs[rest]:
            copy = prior.copy()

            if isinstance(B, ResInter):
                for B2 in B.list():
                    copy.add(B2)
                pcClassSub(tmp, pc, pc2, setInter(copy), right)
            else:
                copy.add(B)
                pcClassSub(tmp, pc, pc2, setInter(copy), right)
        for rel in tmp:
            rhs[rel.right()].append(rel.left())
