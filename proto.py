#! /bin/python3
import rdflib
import psycopg2

import database
import parse
import res
import check
import find

postgresql_password = "postgres"
ontology = "test.ttl"

# load the ontology and save to database
def absorb(cur, filename):
    abox, tbox = parse.parse(filename)
    database.dbSave(cur, tbox)
    database.dbSave(cur, abox)
    
# Connect to database
conn = psycopg2.connect(dbname="rdftest", host='localhost',
                        user="postgres", password=postgresql_password)
cur = conn.cursor()
database.dbInit(cur)

# Save the ontology to the database
absorb(cur, ontology)

# Load all tbox axioms of all saved ontologies
# These will consist of class and property subsumption rules
tbox = database.dbTbox(cur)

print("Tbox axioms:")
for axiom in tbox:
    print("\t" + str(axiom))

# Load all abox axioms of all saved ontologies
# These will consist of class and property facts
abox = database.dbAbox(cur)

print("Abox axioms:")
for axiom, (asserted, inferred) in abox.items():
    print("\t" + str(axiom))
    # print("asserted: " + str(asserted) + ", inferred: " + str(inferred))

# Show which individuals have inconstant facts about them
print("Insistent individuals:")

for indiv in find.findIncon(cur):
    print("\t" + str(indiv))

# Show that dog eats myPizza infers dog consumes myPizza by property subsumption
print("Predicates applying to dog and myPizza:")
for x in find.findPropForSubjObj(cur, res.ResUri("http://example.com/owl#dog"),
                                 res.ResUri("http://example.com/owl#myPizza")):
    print("\t" + str(x))

conn.commit()
cur.close()
conn.close()
