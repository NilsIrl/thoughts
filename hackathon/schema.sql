DROP TABLE IF EXISTS post;
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

CREATE TABLE post (
    PostId INTEGER PRIMARY KEY,
    PostContent TEXT NOT NULL,
    PosterEmail TEXT NOT NULL REFERENCES user(email),
    PostTime INTEGER NOT NULL DEFAULT (unixepoch())
);