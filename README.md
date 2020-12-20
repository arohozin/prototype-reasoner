# prototype-reasoner
A prototype reasoner for OWL

## How to use
### Requirements
The following are required: python3, postgresql, psycopg2, rdflib

These can be installed with

```
sudo apt install python3-dev libpq-dev
python -m pip install psycopg2 rdflib
```

Afterwards you will need to log into postgresql to create the database

```
sudo -i -u postgres
psql
create database rdftest;
```

Afterwards you will need to change the password (and/or username) in proto.py.
The prototype can be run with `./proto.py` and the ontology changed by editing test.ttl (or changed by loading a different file in proto.py).

The database (and accompanying types) can be deleted using

```
drop database rdftest;
DROP TYPE IF EXISTS exprtype;
```

## What has been done so far
So far the following has been completed:
 - Saving and loading to the database
 - Checking the validity of a class fact
 - Checking the validity of a property fact
 - Finding all the individuals of a class
 - Finding all the missing predicates, subjects, objects or combination for a property
 - Finding inconsistencies

Giving proper interpretation to the following predicates with special meaning to owl
 - rdf:type
 - rdfs:subClassOf
 - owl:equivalentClass
 - rdfs:subPropertyOf
 - rdfs:domain
 - rdfs:range
 - owl:disjointWith
 - owl:intersectionOf

## What still needs to be done
Datatype properties (properties about special types of data like numbers and text)

The remaining set-operator class constructors
  - owl:unionOf (not part of owl lite, used to define something 'or' something)
  - owl:complementOf (not part of owl lite, used to define 'not' something)

Complex classes making use of owl:Restriction
  - owl:hasValue (important because it would allow classes to be defined in terms of relation to some other thing by a property, but it is not part of owl lite)
  - owl:someValuesFrom (only class names are allowed in owl lite)
  - owl:allValuesFrom (only class names are allowed in owl lite)
  - owl:maxCardinality (owl lite only allow 0 or 1 as values)
  - owl:minCardinality (owl lite only allow 0 or 1 as values)
  - owl:cardinality (owl lite only allow 0 or 1 as values)

More advanced features of properties
  - owl:SymmetricProperty
  - owl:AsymmetricProperty
  - owl:propertyDisjointWith
  - owl:ReflexiveProperty
  - owl:IrreflexiveProperty
  - owl:FunctionalProperty
  - owl:InverseFunctionalProperty
  - owl:TransitiveProperty
  - owl:propertyChainAxiom
  - owl:equivalentProperty

Predicates expressing identity
  - owl:sameAs
  - owl:differentFrom

Aside from functionality, there are matters of efficiency to attend to
  - Currently only axioms are stored in the database, but commonly used inferences should be used as well
  - Efficiently finding all (named) classes an individual belongs using an inverted index from classes on the left side of a rule to the rule
  - Testing large ontologies, although this will have to wait since not enough functionality has been added yet (wine.owl cannot be loaded properly because it uses restriction classes)
  - A different parser should be used which does not load rdf into a graph

## Various consideration
Currently only abox facts contain information about if they are inferred or asserted, but I think it would be beneficial for tbox axioms to have that information as well. 
