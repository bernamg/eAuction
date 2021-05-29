CREATE TABLE auction (
	artigo_ean	 BIGINT,
	min_price	 FLOAT(8) NOT NULL,
	end_date	 TIMESTAMP NOT NULL,
	description	 VARCHAR(512) NOT NULL,
	actual_bid_price FLOAT(8),
	titulo		 VARCHAR(512) NOT NULL,
	stateOfAuction		 BOOLEAN NOT NULL,
	PRIMARY KEY(artigo_ean)
);

CREATE TABLE bid (
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
	id_version	 SERIAL,
	titulo		 VARCHAR(512) NOT NULL,
	description	 VARCHAR(512) NOT NULL,
	auction_artigo_ean BIGINT,
	PRIMARY KEY(id_version,auction_artigo_ean)
);

CREATE TABLE message (
	text		 TEXT,
	id		 	SERIAL,
	users_username	 VARCHAR(512) NOT NULL,
	auction_artigo_ean BIGINT NOT NULL
);

CREATE TABLE notification (
	message_notif	 TEXT,
	hour		 		TIMESTAMP,
	lida		 BOOLEAN,
	users_username	 VARCHAR(512) NOT NULL,
	auction_artigo_ean BIGINT NOT NULL
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

create or replace procedure bidNotification(artigo_ean BIGINT)
language plpgsql
as $$
declare
    c1 cursor for 
        select users_username, max(bid_price)
        from bid
        where auction_artigo_ean = (artigo_ean) 
		group by users_username;
begin 
    for r in c1
    loop
		insert into notification values(CONCAT('A sua bid de ',r.max,' no LeilaoID: ',artigo_ean,' foi ultrapassada'),CURRENT_TIMESTAMP,FALSE,r.users_username,artigo_ean);
    end loop;
end;
$$;

create or replace procedure removeNotif(username VARCHAR)
language plpgsql
as $$
declare
    c1 cursor for 
        select users_username
        from notification
        where users_username = (username);
begin 
    for r in c1
    loop
		DELETE FROM notification WHERE users_username=r.users_username;	
    end loop;
end;
$$;


create or replace function func_trig_Create_Auction() returns trigger
language plpgsql
as $$
begin
	insert into edition values(DEFAULT, new.titulo, new.description, new.artigo_ean);
	return new;
end;
$$;

create trigger Create_Auction
	after insert on auction
	for each row
		execute procedure func_trig_Create_Auction();


create or replace function func_trig_Update_Auction() returns trigger
language plpgsql
as $$
declare
    c1 cursor for 
        select titulo, description
        from auction
        where artigo_ean = new.artigo_ean;
begin
	if new.titulo=old.titulo and new.description<>old.description then
		insert into edition values(DEFAULT, old.titulo, new.description, new.artigo_ean);
	elseif new.description=old.description and new.titulo<>old.titulo then
		insert into edition values(DEFAULT, new.titulo, old.description, new.artigo_ean);
	else
		insert into edition values(DEFAULT, new.titulo, new.description, new.artigo_ean);
	END IF;
	return new;
end;
$$;

create trigger Update_Auction
	after update on auction
	for each row
		when (new.actual_bid_price=old.actual_bid_price) 
			execute procedure func_trig_Update_Auction();
	

INSERT INTO users VALUES('dvm18','dvm@student.uc','123');
INSERT INTO users VALUES('bernas','bernas@student.uc','123');
INSERT INTO auction VALUES(1234567890123,5.10,'2021-05-05','PlayStation 4 como nova com um comandos e o pes',5.10,'leilao do dvm',TRUE);
INSERT INTO auction VALUES(1234567890124,5.10,'2021-05-05','PlayStation 4 como nova com dois comandos e o fifa21',5.10,'leilao do berna',TRUE);
INSERT INTO users_auction VALUES('dvm18',1234567890123);
INSERT INTO users_auction VALUES('bernas',1234567890124);
insert into message values('olasdsdsdd',DEFAULT,'dvm18',1234567890124);