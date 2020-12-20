#! /bin/python3
import rdflib
from res import *

def parse(filename):
    tboxPred = {
        "http://www.w3.org/2000/01/rdf-schema#subClassOf": tboxClassSub, 
        "http://www.w3.org/2002/07/owl#equivalentClass": tboxClassEquiv,
        "http://www.w3.org/2000/01/rdf-schema#subPropertyOf": tboxPropSub,
        "http://www.w3.org/2000/01/rdf-schema#domain": tboxDomain,
        "http://www.w3.org/2000/01/rdf-schema#range": tboxRange,
        "http://www.w3.org/2002/07/owl#disjointWith": tboxDisjoint
    }

    g = rdflib.Graph()
    g.parse(filename, format=rdflib.util.guess_format(filename))
    abox = {}
    tbox = set()

    for subj, pred, obj in g:
        # print((subj, pred, obj))
        if str(pred) in tboxPred:
            tboxPred[str(pred)](tbox, getExpr(g, subj), getExpr(g, obj))
        elif isinstance(subj, rdflib.term.BNode):
            continue
        elif str(pred) == "http://www.w3.org/1999/02/22-rdf-syntax-ns#type":
            abox[ClassFact(ResUri(subj), ResUri(obj))] = (True, False)
        else:
            # assume prop facts deal with uris for now
            abox[PropFact(ResUri(pred),
                          ResUri(subj), ResUri(obj))] = (True, False)

    return abox, tbox

def getExpr(graph, node):
    if node == rdflib.term.URIRef("http://www.w3.org/2002/07/owl#Nothing"):
        return ResBot()

    rdfinter = rdflib.term.URIRef("http://www.w3.org/2002/07/owl#intersectionOf")
    rdfrestr = rdflib.term.URIRef("http://www.w3.org/2002/07/owl#Restriction")

    if isinstance(node, rdflib.term.URIRef):
        return ResUri(str(node))

    for (pred, obj) in graph.predicate_objects(node):
        if pred == rdfinter:
            return NodeInter(graph, obj)

    print("I have not yet figured out how to deal with these types of values")
    # for (pred, obj) in graph.predicate_objects(node):
    #     print(pred)
    return None

def NodeInter(graph, listNode):
    rdfnil = rdflib.term.URIRef('http://www.w3.org/1999/02/22-rdf-syntax-ns#nil')
    rdffirst = rdflib.term.URIRef('http://www.w3.org/1999/02/22-rdf-syntax-ns#first')
    rdfrest = rdflib.term.URIRef('http://www.w3.org/1999/02/22-rdf-syntax-ns#rest')
    first = None
    rest = None

    if listNode == rdfnil:
        return None

    # check for errors here later like multiple firsts or rests
    for o in graph.objects(subject=listNode, predicate=rdffirst):
        first = getExpr(graph, o)
        for r in graph.objects(subject=listNode, predicate=rdfrest):
            rest = NodeInter(graph, r)
            if rest is None:
                return first
            break
        break

    return ResInter(first, rest)

def tboxClassSub(tbox, subClass, superClass):
    if isinstance(superClass, ResInter):
        tboxClassSub(tbox, subClass, superClass.first)
        tboxClassSub(tbox, subClass, superClass.rest)
    else:
        tbox.add(ClassSub(subClass, superClass))

def tboxClassEquiv(tbox, class1, class2):
    tboxClassSub(tbox, class1, class2)
    tboxClassSub(tbox, class2, class1)

def tboxPropSub(tbox, subProp, superProp):
    tbox.add(PropSub(subProp, superProp))

def tboxDomain(tbox, pred, rdfClass):
    tboxClassSub(tbox, ResRestr(pred, False), rdfClass)

def tboxRange(tbox, pred, rdfClass):
    tboxClassSub(tbox, ResRestr(pred, True), rdfClass)

def tboxDisjoint(tbox, class1, class2):
    tboxClassSub(tbox, ResInter(class1, class2), ResBot())
