CREATE DATABASE quiz;
use quiz;

CREATE TABLE user (
  username VARCHAR(200)
);

CREATE TABLE question (
  qid int NOT NULL,
  title VARCHAR(500),
  PRIMARY KEY (qid)
);

CREATE TABLE answer (
  aid int NOT NULL,
  title VARCHAR(100),
  question_id int NOT NULL,
  FOREIGN KEY (question_id) REFERENCES question(qid)
);

INSERT INTO user
  (username)
VALUES
  ("Marko");

INSERT INTO question
  (qid, title)
VALUES
  (0, 'What is the meaning of life?');

INSERT INTO answer
  (aid, title, question_id)
VALUES
  (0, '42', 0);

