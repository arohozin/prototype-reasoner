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
    dbLoadPropertyFacts(cur, facts)
    return facts

def dbTbox(cur):
    return dbLoadSubClasses(cur).union(dbLoadSubProperties(cur))

def dbLoadClassFacts(cur, facts):
    cur.execute("SELECT class, indiv, asserted, inferred FROM classfact")
    rows = cur.fetchall()
    
    for row in rows:
        rdfClass = dbLoadId(cur, row[0])
        indiv = dbLoadId(cur, row[1])
        facts[ClassFact(indiv, rdfClass)] = (row[2], row[3])

    return facts

def dbLoadPropertyFacts(cur, facts):
    cur.execute("SELECT property, domain, range, asserted, inferred FROM propfact")
    rows = cur.fetchall()
    
    for row in rows:
        pred = dbLoadId(cur, row[0])
        subj = dbLoadId(cur, row[1])
        obj = dbLoadId(cur, row[2])
        facts[PropFact(pred, subj, obj)] = (row[3], row[4])

    return facts

def dbLoadSubClasses(cur):
    facts = set()
    cur.execute("SELECT subclass, superclass FROM classsub")
    rows = cur.fetchall()
    
    for row in rows:
        subClass = dbLoadId(cur, row[0])
        superClass = dbLoadId(cur, row[1])
        facts.add(SubClass(subClass, superClass))

    return facts

def dbLoadSubProperties(cur):
    facts = set()
    cur.execute("SELECT subproperty, superproperty FROM propertysub")
    rows = cur.fetchall()
    
    for row in rows:
        subProperty = dbLoadId(cur, row[0])
        superProperty = dbLoadId(cur, row[1])
        facts.add(SubProperty(subProperty, superProperty))

    return facts

def dbSave(cur, dat):
    funcs = {
        SubClass: dbSaveSubClass,
        SubProperty: dbSaveSubProperty,
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
        ON CONFLICT (property, domain, range)
        DO UPDATE SET asserted = (EXCLUDED.asserted OR propfact.asserted), 
                      inferred = (EXCLUDED.inferred OR propfact.inferred)
        """, (dbGetId(cur, propFact.pred), dbGetId(cur, propFact.subj),
              dbGetId(cur, propFact.obj),
              asserted, inferred))

def dbSaveSubClass(cur, subClass):
    cur.execute(
        """
        INSERT INTO classsub VALUES (%s,%s)
        ON CONFLICT (subclass, superclass) DO NOTHING
        """, (dbGetId(cur, subClass.subClass),
              dbGetId(cur, subClass.superClass)))

def dbSaveSubProperty(cur, subProperty):
    cur.execute(
        """
        INSERT INTO propertysub VALUES (%s,%s)
        ON CONFLICT (subproperty, superproperty) DO NOTHING
        """, (dbGetId(cur, subProperty.subProperty),
              dbGetId(cur, subProperty.superProperty)))

def dbGetId(cur, expr):
    funcs = {
        ResBot: dbGetBot,
        ResUri: dbGetUri,
        ResInter: dbGetInter,
        ResInv: dbGetInv,
        ResRestr: dbGetRestr,
    }

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
        WHERE property = %s
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
            INSERT INTO resinv (id,property) 
            VALUES (%s,%s)
            """, (id[0], predId))

    return id[0]

def dbGetRestr(cur, restr):
    predId = dbGetId(cur, restr.pred)

    cur.execute(
        """
        SELECT id FROM resrestr 
        WHERE property = %s
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
            INSERT INTO resrestr (id,property) 
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
    cur.execute("SELECT property FROM resinv WHERE id = %s", (id,))
    results = cur.fetchone()
    return ResInv(dbLoadId(cur, results[0]))

def dbLoadRestr(cur, id):
    cur.execute("SELECT property FROM resrestr WHERE id = %s", (id,))
    results = cur.fetchone()
    return ResRestr(dbLoadId(cur, results[0]), False)
