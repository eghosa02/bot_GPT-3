DROP TABLE IF EXISTS accounts;
DROP TABLE IF EXISTS channels;
DROP TABLE IF EXISTS accounts_2;

CREATE TABLE accounts(
    usernameId INTEGER,
    actualDelay INTEGER,
    actualTime INTEGER,
    serverId INTEGER,
    identify INTEGER
);

CREATE TABLE channels(
    channelId INTEGER
);

CREATE TABLE accounts_2(
    usernameId INTEGER,
    actualDelay INTEGER,
    actualTime INTEGER,
    serverId INTEGER,
    identify INTEGER
);

INSERT INTO channels(channelId) VALUES (833703219712098358);
INSERT INTO channels(channelId) VALUES (1060292940125196288);
INSERT INTO channels(channelId) VALUES (1060295203942039714);