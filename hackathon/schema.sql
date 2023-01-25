CREATE TABLE user (
    email UNIQUE TEXT NOT NULL,
    token TEXT NOT NULL
);

CREATE TABLE exhibit (
    exhibit_id INTEGER PRIMARY KEY,
    prompt UNIQUE TEXT NOT NULL
);