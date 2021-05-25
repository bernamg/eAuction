CREATE TABLE auction (
	artigo_ean	 BIGINT,
	min_price	 FLOAT(8) NOT NULL,
	end_date	 DATE NOT NULL,
	description	 VARCHAR(512) NOT NULL,
	actual_bid_price FLOAT(8),
	PRIMARY KEY(artigo_ean)
);

CREATE TABLE bid (
	username		 VARCHAR(512) NOT NULL,
	bid_price		 FLOAT(8) NOT NULL,
	auction_artigo_ean BIGINT,
	users_username	 VARCHAR(512) NOT NULL,
	PRIMARY KEY(bid_price,auction_artigo_ean)
);

CREATE TABLE users (
	username	 VARCHAR(512),
	email	 VARCHAR(512) UNIQUE NOT NULL,
	password	 VARCHAR(512) NOT NULL,
	token_login VARCHAR(512),
	PRIMARY KEY(username)
);

CREATE TABLE edition (
	id_version	 VARCHAR(512),
	auction_artigo_ean BIGINT,
	PRIMARY KEY(id_version,auction_artigo_ean)
);

CREATE TABLE message (
	text		 TEXT,
	users_username	 VARCHAR(512),
	auction_artigo_ean BIGINT,
	PRIMARY KEY(users_username,auction_artigo_ean)
);

CREATE TABLE notification (
	message_notif	 TEXT,
	hour		 DATE,
	users_username	 VARCHAR(512),
	auction_artigo_ean BIGINT,
	PRIMARY KEY(users_username,auction_artigo_ean)
);

CREATE TABLE users_auction (
	users_username	 VARCHAR(512),
	auction_artigo_ean BIGINT,
	PRIMARY KEY(users_username,auction_artigo_ean)
);

ALTER TABLE bid ADD CONSTRAINT bid_fk1 FOREIGN KEY (auction_artigo_ean) REFERENCES auction(artigo_ean);
ALTER TABLE bid ADD CONSTRAINT bid_fk2 FOREIGN KEY (users_username) REFERENCES users(username);
ALTER TABLE edition ADD CONSTRAINT edition_fk1 FOREIGN KEY (auction_artigo_ean) REFERENCES auction(artigo_ean);
ALTER TABLE message ADD CONSTRAINT message_fk1 FOREIGN KEY (users_username) REFERENCES users(username);
ALTER TABLE message ADD CONSTRAINT message_fk2 FOREIGN KEY (auction_artigo_ean) REFERENCES auction(artigo_ean);
ALTER TABLE notification ADD CONSTRAINT notification_fk1 FOREIGN KEY (users_username) REFERENCES users(username);
ALTER TABLE notification ADD CONSTRAINT notification_fk2 FOREIGN KEY (auction_artigo_ean) REFERENCES auction(artigo_ean);
ALTER TABLE users_auction ADD CONSTRAINT users_auction_fk1 FOREIGN KEY (users_username) REFERENCES users(username);
ALTER TABLE users_auction ADD CONSTRAINT users_auction_fk2 FOREIGN KEY (auction_artigo_ean) REFERENCES auction(artigo_ean);


INSERT INTO users VALUES('dvm18','dvm@student.uc','123');
INSERT INTO users VALUES('bernas','bernas@student.uc','123');
INSERT INTO auction VALUES(1234567890123,5.10,'2021-05-05','PlayStation 4 como nova com dois comandos e o fifa21',NULL);
INSERT INTO auction VALUES(1234567890124,5.10,'2021-05-05','PlayStation 4 como nova com dois comandos e o fifa21',NULL);
INSERT INTO users_auction VALUES('dvm18',1234567890123);
INSERT INTO users_auction VALUES('bernas',1234567890124);




