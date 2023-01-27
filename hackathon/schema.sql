DROP TABLE IF EXISTS follow;
DROP TABLE IF EXISTS post;
DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS image;
DROP TABLE IF EXISTS exhibit;

CREATE TABLE user (
    email TEXT UNIQUE NOT NULL,
    token TEXT NOT NULL
);

CREATE TABLE exhibit (
    exhibit_id INTEGER PRIMARY KEY,
    prompt TEXT UNIQUE NOT NULL
);

CREATE TABLE image (
    imageUrl TEXT UNIQUE NOT NULL,
    ExhibitId INTEGER NOT NULL REFERENCES exhibit(exhibit_id)
);

CREATE TABLE post (
    PostId INTEGER PRIMARY KEY,
    PostContent TEXT NOT NULL,
    PosterEmail TEXT NOT NULL REFERENCES user(email),
    PostTime INTEGER NOT NULL DEFAULT (unixepoch())
);

CREATE TABLE follow (
    follower TEXT NOT NULL REFERENCES user(email),
    followee TEXT NOT NULL REFERENCES user(email),
    -- Hopefully this isn't too bad of an idea to just ignore problems
    UNIQUE(follower, followee) ON CONFLICT IGNORE
);