DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS agent;

CREATE TABLE user (
  email TEXT NOT NULL,
  password TEXT NOT NULL,
  PRIMARY KEY (email)
);

INSERT INTO user VALUES
('e70838@gmail.com', 'e7');

CREATE TABLE agent (
  name TEXT NOT NULL,
  password TEXT NOT NULL,
  role TEXT NOT NULL, -- either guichet or technique
  PRIMARY KEY (name)
);

INSERT INTO agent VALUES
('safae', 'safae', 'guichet'),
('jef', 'jef', 'technique')
;
