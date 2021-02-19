CREATE TABLE t_schooltasks (
    task_name     TEXT,
    content_name  TEXT,
    datetime_from TEXT,
    identity      INTEGER,
    subject_name  TEXT,
    MSG_SENT      TEXT
);

CREATE TABLE t_chats (
    chatid INTEGER,
    PRIMARY KEY (
        chatid
    )
);

