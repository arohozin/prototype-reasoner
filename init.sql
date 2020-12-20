-- DROP TYPE exprtype;

CREATE TABLE IF NOT EXISTS classfact (
  class INTEGER,
  indiv INTEGER,
  asserted BOOLEAN NOT NULL,
  inferred BOOLEAN NOT NULL,
  PRIMARY KEY (class, indiv)
);

CREATE TABLE IF NOT EXISTS propfact (
  pred INTEGER,
  subj INTEGER,
  obj INTEGER,
  asserted BOOLEAN NOT NULL,
  inferred BOOLEAN NOT NULL,
  PRIMARY KEY (pred, subj, obj)
);

CREATE TABLE IF NOT EXISTS classsub (
  subclass INTEGER NOT NULL,
  superclass INTEGER NOT NULL,
  PRIMARY KEY (subclass, superclass)
);

CREATE TABLE IF NOT EXISTS propsub (
  subprop INTEGER NOT NULL,
  superprop INTEGER NOT NULL,
  PRIMARY KEY (subprop, superprop)
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
  prop INTEGER NOT NULL,
  PRIMARY KEY (id, prop),
  UNIQUE (id)
);


CREATE TABLE IF NOT EXISTS resrestr (
  id INTEGER NOT NULL,
  prop INTEGER NOT NULL,
  -- inverse BOOLEAN NOT NULL,
  PRIMARY KEY (id, prop),
  UNIQUE (id)
);
