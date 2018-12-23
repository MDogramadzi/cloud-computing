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
  correct BOOLEAN,
  question_id int NOT NULL,
  FOREIGN KEY (question_id) REFERENCES question(qid)
);

INSERT INTO user
  (username)
VALUES
  ("Marko"),
  ("Goce");

INSERT INTO question
  (qid, title)
VALUES
  (0, 'Which of these is NOT a NOSQL Document Database?'),
  (1, 'Google App Engine is an example of which *aaS?'),
  (2, 'Which of these is an AWS example service from IaaS?'),
  (3, 'What is Hadoop named after?'),
  (4, 'Which of these is the open-source version of Pregel?'),
  (5, 'Which of these scaling types involves decomposing by function?'),
  (6, 'Where does the majority of power go in a modern data centre?'),
  (7, 'Which of these best describes MapReduce?'),
  (8, 'Which of these is considered the most serious threat in Cloud Security?'),
  (9, 'Which of these IaC tools NOT open-source?');


INSERT INTO answer
  (aid, title, correct, question_id)
VALUES
  (0, 'ZooKeeper', TRUE, 0),
  (1, 'MongoDB', FALSE, 0),
  (2, 'BaseX', FALSE, 0),
  (3, 'RethinkDB', FALSE, 0),
  (4, 'Software as a Service (SaaS)', FALSE, 1),
  (5, 'Platform as a Service (PaaS)', TRUE, 1),
  (6, 'Infrastructure as a Service (IaaS)', FALSE, 1),
  (7, 'Car as a Service (CaaS)', FALSE, 1),
  (8, 'EC2', TRUE, 2),
  (9, 'Elastic Beanstalk', FALSE, 2),
  (10, 'Amazon Prime', FALSE, 2),
  (11, 'Amazon Web Services', FALSE, 2),
  (12, 'A stuffed yellow elephant', TRUE, 3),
  (13, 'A wooden blue elephant', FALSE, 3),
  (14, 'An inflatable green elephant ', FALSE, 3),
  (15, 'An actual hippo', FALSE, 3),
  (16, 'Giraph', TRUE, 4),
  (17, 'Anzograph', FALSE, 4),
  (18, 'Datastax', FALSE, 4),
  (19, 'Amazon Neptune', FALSE, 4),
  (20, 'Y-Axis Scaling', TRUE, 5),
  (21, 'X-Axis Scaling', FALSE, 5),
  (22, 'Z-Axis Scaling', FALSE, 5),
  (23, 'V-Axis Scaling', FALSE, 5),
  (24, 'CPUs', TRUE, 6),
  (25, 'Disks', FALSE, 6),
  (26, 'Cooling Overhead', FALSE, 6),
  (27, 'DRAM', FALSE, 6),
  (28, 'An Architecture', TRUE, 7),
  (29, 'An Algorithm', FALSE, 7),
  (30, 'A Programming Language', FALSE, 7),
  (31, 'A Database', FALSE, 7),
  (32, 'Data Breaches', TRUE, 8),
  (33, 'Account Hijacking', FALSE, 8),
  (34, 'Malicious Insiders', FALSE, 8),
  (35, 'Insecure Interfaces and APIs', FALSE, 8),
  (36, 'Cloud-Formation', TRUE, 9),
  (37, 'Chef', FALSE, 9),
  (38, 'Ansible', FALSE, 9),
  (39, 'SaltStack', FALSE, 9);

