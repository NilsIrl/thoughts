DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS exhibit;

CREATE TABLE user (
    email TEXT UNIQUE NOT NULL,
    token TEXT NOT NULL
);

CREATE TABLE exhibit (
    exhibit_id INTEGER PRIMARY KEY,
    prompt TEXT UNIQUE NOT NULL
);