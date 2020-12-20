import rdflib
import psycopg2
from res import *

def dbInit(cur):
    initFile = open("init.sql", "r")
    sql = initFile.read()
    initFile.close()
    cur.execute(sql)

def dbAbox(cur):
    facts = {}
    dbLoadClassFacts(cur, facts)
    dbLoadPropFacts(cur, facts)
    return facts

def dbTbox(cur):
    return dbLoadClassSubs(cur).union(dbLoadPropSubs(cur))

def dbLoadClassFacts(cur, facts):
    cur.execute("SELECT class, indiv, asserted, inferred FROM classfact")
    rows = cur.fetchall()
    
    for row in rows:
        rdfClass = dbLoadId(cur, row[0])
        indiv = dbLoadId(cur, row[1])
        facts[ClassFact(indiv, rdfClass)] = (row[2], row[3])

    return facts

def dbLoadPropFacts(cur, facts):
    cur.execute("SELECT pred, subj, obj, asserted, inferred FROM propfact")
    rows = cur.fetchall()
    
    for row in rows:
        pred = dbLoadId(cur, row[0])
        subj = dbLoadId(cur, row[1])
        obj = dbLoadId(cur, row[2])
        facts[PropFact(pred, subj, obj)] = (row[3], row[4])

    return facts

def dbLoadClassSubs(cur):
    facts = set()
    cur.execute("SELECT subclass, superclass FROM classsub")
    rows = cur.fetchall()
    
    for row in rows:
        subClass = dbLoadId(cur, row[0])
        superClass = dbLoadId(cur, row[1])
        facts.add(ClassSub(subClass, superClass))

    return facts

def dbLoadPropSubs(cur):
    facts = set()
    cur.execute("SELECT subprop, superprop FROM propsub")
    rows = cur.fetchall()
    
    for row in rows:
        subProp = dbLoadId(cur, row[0])
        superProp = dbLoadId(cur, row[1])
        facts.add(PropSub(subProp, superProp))

    return facts

def dbSave(cur, dat):
    funcs = {
        ClassSub: dbSaveClassSub,
        PropSub: dbSavePropSub,
        dict: dbSaveFacts,
    }

    if isinstance(dat, set):
        for i in dat:
            dbSave(cur, i)
        return

    funcs[type(dat)](cur, dat)

def dbSaveFacts(cur, facts):
    for fact, (asserted, inferred) in facts.items():
        if isinstance(fact, ClassFact):
            dbSaveClassFact(cur, fact, asserted, inferred)
        else:
            dbSavePropFact(cur, fact, asserted, inferred)

def dbSaveClassFact(cur, classFact, asserted, inferred):
    cur.execute(
        """
        INSERT INTO classfact VALUES (%s,%s,%s,%s)
        ON CONFLICT (class, indiv)
        DO UPDATE SET asserted = (EXCLUDED.asserted OR classfact.asserted), 
                      inferred = (EXCLUDED.inferred OR classfact.inferred)
        """, (dbGetId(cur, classFact.rdfClass),
              dbGetId(cur, classFact.indiv),
              asserted, inferred))

def dbSavePropFact(cur, propFact, asserted, inferred):
        cur.execute(
        """
        INSERT INTO propfact VALUES (%s,%s,%s,%s,%s)
        ON CONFLICT (pred, subj, obj)
        DO UPDATE SET asserted = (EXCLUDED.asserted OR propfact.asserted), 
                      inferred = (EXCLUDED.inferred OR propfact.inferred)
        """, (dbGetId(cur, propFact.pred), dbGetId(cur, propFact.subj),
              dbGetId(cur, propFact.obj),
              asserted, inferred))

def dbSaveClassSub(cur, subClass):
    cur.execute(
        """
        INSERT INTO classsub VALUES (%s,%s)
        ON CONFLICT (subclass, superclass) DO NOTHING
        """, (dbGetId(cur, subClass.subClass),
              dbGetId(cur, subClass.superClass)))

def dbSavePropSub(cur, subProp):
    cur.execute(
        """
        INSERT INTO propsub VALUES (%s,%s)
        ON CONFLICT (subprop, superprop) DO NOTHING
        """, (dbGetId(cur, subProp.subProp),
              dbGetId(cur, subProp.superProp)))

def dbGetId(cur, expr):
    funcs = {
        ResBot: dbGetBot,
        ResUri: dbGetUri,
        ResInter: dbGetInter,
        ResInv: dbGetInv,
        ResRestr: dbGetRestr,
    }

    if isinstance(expr, int):
        print(expr)

    return funcs[type(expr)](cur, expr)

def dbLoadId(cur, id):
    funcs = {
        'bot': dbLoadBot,
        'uri': dbLoadUri,
        'inter': dbLoadInter,
        'inv': dbLoadInv,
        'restr': dbLoadRestr,
    }

    cur.execute("SELECT type FROM restype WHERE id = %s", (id,))
    restype = cur.fetchone()

    if restype == None:
        return None

    return funcs[restype[0]](cur, id)

def dbGetBot(cur, bot):
    return 0

def dbGetUri(cur, uri):
    cur.execute(
        """
        SELECT id FROM resuri WHERE uri = %s
        """, (uri.uri,))

    id = cur.fetchone()

    if id == None:
        cur.execute(
            """
            INSERT INTO restype (type) VALUES ('uri') RETURNING id
            """)

        id = cur.fetchone()

        cur.execute(
            """
            INSERT INTO resUri (id,uri) 
            VALUES (%s,%s)
            """, (id[0], uri.uri))

    return id[0]

def dbGetInter(cur, inter):
    firstId = dbGetId(cur, inter.first)
    restId = dbGetId(cur, inter.rest)

    cur.execute(
        """
        SELECT id FROM resinter WHERE first = %s AND rest = %s
        """, (firstId, restId))

    id = cur.fetchone()

    if id == None:
        cur.execute(
            """
            INSERT INTO restype (type) VALUES ('inter') RETURNING id
            """)

        id = cur.fetchone()

        cur.execute(
            """
            INSERT INTO resinter (id,first,rest) VALUES (%s,%s,%s)
            """, (id[0], firstId, restId))

    return id[0]

def dbGetInv(cur, inv):
    predId = dbGetId(cur, inv.pred)

    cur.execute(
        """
        SELECT id FROM resinv
        WHERE prop = %s
        """, (predId,))

    id = cur.fetchone()

    if id == None:
        cur.execute(
            """
            INSERT INTO restype (type) VALUES ('inv') RETURNING id
            """)

        id = cur.fetchone()

        cur.execute(
            """
            INSERT INTO resinv (id,prop) 
            VALUES (%s,%s)
            """, (id[0], predId))

    return id[0]

def dbGetRestr(cur, restr):
    predId = dbGetId(cur, restr.pred)

    cur.execute(
        """
        SELECT id FROM resrestr 
        WHERE prop = %s
        """, (predId,))

    id = cur.fetchone()

    if id == None:
        cur.execute(
            """
            INSERT INTO restype (type) VALUES ('restr') RETURNING id
            """)

        id = cur.fetchone()

        cur.execute(
            """
            INSERT INTO resrestr (id,prop) 
            VALUES (%s,%s)
            """, (id[0], predId))

    return id[0]

def dbLoadBot(cur, id):
    return ResBot()

def dbLoadUri(cur, id):
    cur.execute("SELECT uri FROM resuri WHERE id = %s", (id,))
    return ResUri(cur.fetchone()[0])


def dbLoadInter(cur, id):
    cur.execute("SELECT first, rest FROM resinter WHERE id = %s", (id,))
    results = cur.fetchone()
    return ResInter(dbLoadId(cur, results[0]), dbLoadId(cur, results[1]))

def dbLoadInv(cur, id):
    cur.execute("SELECT prop FROM resinv WHERE id = %s", (id,))
    results = cur.fetchone()
    return ResInv(dbLoadId(cur, results[0]))

def dbLoadRestr(cur, id):
    cur.execute("SELECT prop FROM resrestr WHERE id = %s", (id,))
    results = cur.fetchone()
    return ResRestr(dbLoadId(cur, results[0]), False)

def dbContains(cur, dat):
    funcs = {
        ClassFact: dbContainsClassFact,
        PropFact: dbContainsPropFact,
        ClassSub: dbContainsClassSub,
        PropSub: dbContainsPropSub
    }

    if isinstance(dat, set):
        for i in dat:
            if not dbContains(cur, i):
                return 0
            return 1

    return funcs[type(dat)](cur, dat)

def dbContainsClassFact(cur, fact):
    cur.execute(
        """
        SELECT EXISTS (SELECT 1 FROM classfact
        WHERE class = %s AND indiv = %s)
        """, (dbGetId(cur, fact.rdfClass), dbGetId(cur, fact.indiv)))
    row = cur.fetchone()
    return row[0]

def dbContainsPropFact(cur, fact):
    cur.execute(
        """
        SELECT EXISTS (SELECT 1 FROM propfact
        WHERE pred = %s AND subj = %s AND obj = %s)
        """, (dbGetId(cur, fact.pred), dbGetId(cur, fact.subj),
              dbGetId(cur, fact.obj)))
    row = cur.fetchone()
    return row[0]

def dbContainsClassSub(cur, fact):
    cur.execute(
        """
        SELECT EXISTS (SELECT 1 FROM classsub
        WHERE subclass = %s AND superclass = %s)
        """, (dbGetId(cur, fact.subClass), dbGetId(cur, fact.superClass)))
    row = cur.fetchone()
    return row[0]

def dbContainsPropSub(cur, fact):
    cur.execute(
        """
        SELECT EXISTS (SELECT 1 FROM propsub
        WHERE subprop = %s AND superprop = %s)
        """, (dbGetId(cur, fact.subProp), dbGetId(cur, fact.superProp)))
    row = cur.fetchone()
    return row[0]

def dbClassFactByClass(cur, rdfClass):
    facts = {}
    cur.execute(
        """
        SELECT indiv, asserted, inferred FROM classfact
        WHERE class = %s
        """, (dbGetId(cur, rdfClass),))
    rows = cur.fetchall()

    for row in rows:
        indiv = dbLoadId(cur, row[0])
        facts[ClassFact(indiv, rdfClass)] = (row[1], row[2])

    return facts

def dbClassFactByIndiv(cur, indiv):
    facts = {}
    cur.execute(
        """
        SELECT class, asserted, inferred FROM classfact
        WHERE indiv = %s
        """, (dbGetId(cur, indiv),))
    rows = cur.fetchall()

    for row in rows:
        rdfClass = dbLoadId(cur, row[0])
        facts[ClassFact(indiv, rdfClass)] = (row[1], row[2])

    return facts

def dbPropFactByPred(cur, pred):
    facts = {}
    cur.execute(
        """
        SELECT subj, obj, asserted, inferred FROM propfact
        WHERE pred = %s
        """, (dbGetId(cur, pred),))
    rows = cur.fetchall()

    for row in rows:
        subj = dbLoadId(cur, row[0])
        obj = dbLoadId(cur, row[1])
        facts[PropFact(pred, subj, obj)] = (row[2], row[3])

    return facts

def dbPropFactBySubj(cur, subj):
    facts = {}
    cur.execute(
        """
        SELECT pred, obj, asserted, inferred FROM propfact
        WHERE subj = %s
        """, (dbGetId(cur, subj),))
    rows = cur.fetchall()

    for row in rows:
        pred = dbLoadId(cur, row[0])
        obj = dbLoadId(cur, row[1])
        facts[PropFact(pred, subj, obj)] = (row[2], row[3])

    return facts

def dbPropFactByObj(cur, obj):
    facts = {}
    cur.execute(
        """
        SELECT pred, subj, asserted, inferred FROM propfact
        WHERE pred = %s
        """, (dbGetId(cur, obj),))
    rows = cur.fetchall()

    for row in rows:
        pred = dbLoadId(cur, row[0])
        subj = dbLoadId(cur, row[1])
        facts[PropFact(pred, subj, obj)] = (row[2], row[3])

    return facts

def dbPropFactByPredSubj(cur, pred, subj):
    facts = {}
    cur.execute(
        """
        SELECT obj, asserted, inferred FROM propfact
        WHERE pred = %s AND subj = %s
        """, (dbGetId(cur, pred), dbGetId(cur, subj)))
    rows = cur.fetchall()

    for row in rows:
        obj = dbLoadId(cur, row[0])
        facts[PropFact(pred, subj, obj)] = (row[1], row[2])

    return facts

def dbPropFactByPredObj(cur, pred, obj):
    facts = {}
    cur.execute(
        """
        SELECT subj, asserted, inferred FROM propfact
        WHERE pred = %s AND obj = %s
        """, (dbGetId(cur, pred), dbGetId(cur, obj)))
    rows = cur.fetchall()

    for row in rows:
        subj = dbLoadId(cur, row[0])
        facts[PropFact(pred, subj, obj)] = (row[1], row[2])

    return facts

def dbPropFactBySubjObj(cur, subj, obj):
    facts = {}
    cur.execute(
        """
        SELECT pred, asserted, inferred FROM propfact
        WHERE subj = %s AND obj = %s
        """, (dbGetId(cur, subj), dbGetId(cur, obj)))
    rows = cur.fetchall()

    for row in rows:
        pred = dbLoadId(cur, row[0])
        facts[PropFact(pred, subj, obj)] = (row[1], row[2])

    return facts

def dbClassSubBySuper(cur, superClass):
    facts = set()
    cur.execute(
        """
        SELECT subclass FROM classsub
        WHERE superclass = %s
        """, (dbGetId(cur, superClass),))
    rows = cur.fetchall()

    for row in rows:
        subClass = dbLoadId(cur, row[0])
        facts.add(ClassSub(subClass, superClass))

    return facts

def dbClassSubBySub(cur, subClass):
    facts = set()
    cur.execute(
        """
        SELECT superclass FROM classsub
        WHERE subclass = %s
        """, (dbGetId(cur, subClass),))
    rows = cur.fetchall()

    for row in rows:
        superClass = dbLoadId(cur, row[0])
        facts.add(ClassSub(subClass, superClass))

    return facts

def dbPropSubBySuper(cur, superProp):
    facts = set()
    cur.execute(
        """
        SELECT subprop FROM propsub
        WHERE superprop = %s
        """, (dbGetId(cur, superProp),))
    rows = cur.fetchall()

    for row in rows:
        subProp = dbLoadId(cur, row[0])
        facts.add(PropSub(subProp, superProp))

    return facts

def dbPropSubBySub(cur, subProp):
    facts = set()
    cur.execute(
        """
        SELECT superprop FROM propsub
        WHERE subprop = %s
        """, (dbGetId(cur, subProp),))
    rows = cur.fetchall()

    for row in rows:
        superProp = dbLoadId(cur, row[0])
        facts.add(PropSub(subProp, superProp))

    return facts

def dbInDomain(cur, pred, subj):
    cur.execute(
        """
        SELECT EXISTS (SELECT 1 FROM propfact
        WHERE pred = %s AND subj = %s)
        """, (dbGetId(cur, pred), dbGetId(cur, subj)))
    row = cur.fetchone()
    return row[0]

def dbInRange(cur, pred, obj):
    cur.execute(
        """
        SELECT EXISTS (SELECT 1 FROM propfact
        WHERE pred = %s AND obj = %s)
        """, (dbGetId(cur, pred), dbGetId(cur, obj)))
    row = cur.fetchone()
    return row[0]
