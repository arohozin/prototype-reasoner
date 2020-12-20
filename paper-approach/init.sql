-- DROP TYPE exprtype;

CREATE TABLE IF NOT EXISTS classfact (
  class INTEGER,
  indiv INTEGER,
  asserted BOOLEAN NOT NULL,
  inferred BOOLEAN NOT NULL,
  PRIMARY KEY (class, indiv)
);

CREATE TABLE IF NOT EXISTS propfact (
  property INTEGER,
  domain INTEGER,
  range INTEGER,
  asserted BOOLEAN NOT NULL,
  inferred BOOLEAN NOT NULL,
  PRIMARY KEY (property, domain, range)
);

CREATE TABLE IF NOT EXISTS classsub (
  subclass INTEGER NOT NULL,
  superclass INTEGER NOT NULL,
  PRIMARY KEY (subclass, superclass)
);

CREATE TABLE IF NOT EXISTS propertysub (
  subproperty INTEGER NOT NULL,
  superproperty INTEGER NOT NULL,
  PRIMARY KEY (subproperty, superproperty)
);

DO $$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'exprtype') THEN
      CREATE TYPE exprtype AS ENUM ('bot', 'uri', 'inter', 'inv', 'restr');
  END IF;
END
$$;

CREATE TABLE IF NOT EXISTS restype (
  id SERIAL,
  type exprtype NOT NULL,
  PRIMARY KEY (id)
);

INSERT INTO restype (id, type) VALUES (0, 'bot')
ON CONFLICT DO NOTHING;

CREATE TABLE IF NOT EXISTS resuri (
  id INTEGER NOT NULL,
  uri TEXT NOT NULL,
  PRIMARY KEY (id, uri),
  UNIQUE (uri)
);

CREATE TABLE IF NOT EXISTS resinter (
  id INTEGER NOT NULL,
  first INTEGER NOT NULL,
  rest INTEGER NOT NULL,
  PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS resinv (
  id INTEGER NOT NULL,
  property INTEGER NOT NULL,
  PRIMARY KEY (id, property),
  UNIQUE (id)
);


CREATE TABLE IF NOT EXISTS resrestr (
  id INTEGER NOT NULL,
  property INTEGER NOT NULL,
  -- inverse BOOLEAN NOT NULL,
  PRIMARY KEY (id, property),
  UNIQUE (id)
);
