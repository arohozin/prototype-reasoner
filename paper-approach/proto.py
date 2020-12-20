#! /bin/python3
import rdflib
import psycopg2

import database
import parse
import closure
import materialize

def absorb(cur, filename):
    abox, tbox = parse.parse(filename)
    dbTbox = database.dbTbox(cur)
    pc = closure.positiveClosure(tbox.union(dbTbox))
    tbox2 = tbox.union(pc)
    materialize.materialize(tbox, abox)
    database.dbSave(cur, tbox2)
    database.dbSave(cur, abox)
    

conn = psycopg2.connect(dbname="rdftest", host='localhost',
                        user="postgres", password="postgres")
cur = conn.cursor()
database.dbInit(cur)
absorb(cur, 'test.ttl')

tbox = database.dbTbox(cur)

for axiom in tbox:
    print(axiom)

abox = database.dbAbox(cur)

for axiom, (asserted, inferred) in abox.items():
    print(axiom)
    print("asserted: " + str(asserted) + ", inferred: " + str(inferred))


conn.commit()
cur.close()
conn.close()
