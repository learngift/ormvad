DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS agent;
DROP TABLE IF EXISTS demande;
DROP TABLE IF EXISTS dmd_exam_cons_elevage;
DROP TABLE IF EXISTS piece;
DROP TABLE IF EXISTS histo;

CREATE TABLE user (
  email TEXT NOT NULL,
  password TEXT NOT NULL,
  name TEXT,
  surname TEXT,
  cin TEXT,
  address TEXT,
  phone TEXT,
  PRIMARY KEY (email)
);

CREATE TABLE demande (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  email TEXT NOT NULL,
  date_demande TEXT NOT NULL,
  designation TEXT NOT NULL, -- enum
  etat TEXT NOT NULL,
  FOREIGN KEY(email) REFERENCES user(email)
);

-- demande d'examen d'un projet de construction de batiment d'élevage
CREATE TABLE dmd_exam_cons_elevage (
  id INTEGER PRIMARY KEY,
  name TEXT,
  surname TEXT,
  raison_sociale TEXT,
  cin TEXT,
  douar TEXT,
  commune_rurale TEXT,
  cercle TEXT,
  Province TEXT,
  address TEXT, -- adresse de correspondance
  phone TEXT,
  objet TEXT,
  superficie TEXT,
  effectif TEXT -- effectif du cheptel
);

CREATE TABLE piece (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  dmd_id INTEGER NOT NULL,
  date_piece TEXT NOT NULL,
  filename TEXT NOT NULL,
  FOREIGN KEY(dmd_id) REFERENCES demande(id)
);

CREATE TABLE histo (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  who TEXT NOT NULL, -- email of user or name of agent
  date_histo TEXT NOT NULL, -- when
  dmd_id INTEGER,
  description TEXT NOT NULL
);

INSERT INTO user (email, password) VALUES
('agriculteur@example.com', 'e7');

CREATE TABLE agent (
  name TEXT NOT NULL,
  password TEXT NOT NULL,
  role TEXT NOT NULL, -- either guichet or technique or admin
  PRIMARY KEY (name)
);

-- ?? ('admin', 'admin', 'admin'),
INSERT INTO agent VALUES
('safae', 'safae', 'guichet'),
('jef', 'jef', 'technique')
;
