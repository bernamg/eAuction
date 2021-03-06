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
	validade	 TIMESTAMP,
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
/*Verifica validade*/
create or replace procedure TokenDateValidation() 
language plpgsql
as $$
declare
	c1 cursor for
		select token_login, validade from users;	
begin
	 for r in c1
    loop
		if r.validade < CURRENT_TIMESTAMP + '1 hour' then
			update users set token_login=NULL, validade=NULL where r.token_login=token_login;
		end if;
    end loop;
end;
$$;

/* Verificar se user esta logado e qual o seu username*/
create or replace function IsUserLogged(AuthToken VARCHAR) returns VARCHAR
language plpgsql
as $$
declare
	x VARCHAR;
begin
	select username into x from users where token_login = (AuthToken);
	return(x);
exception
	when others then
		raise exception 'error';
end;
$$;

/* Verifica se o artigo_ean existe*/
create or replace function IsAuctionCorrect(rec_artigo_ean BIGINT) returns BIGINT
language plpgsql
as $$
declare
	x BIGINT;
begin
		select artigo_ean into x from auction where artigo_ean = (rec_artigo_ean);
	return(x);
exception
	when others then
		raise exception 'error';
end;
$$;

/* Verifica se um leilao pertence a um user */
create or replace function IsAuctionFromUser(username VARCHAR, rec_artigo_ean BIGINT) returns BIGINT
language plpgsql
as $$
declare
	x BIGINT;
begin
		select auction_artigo_ean into x from users_auction where users_username = (username) and auction_artigo_ean = (rec_artigo_ean);
	return(x);
exception
	when others then
		raise exception 'error';
end;
$$;

/*Finish auction*/
create or replace procedure finishAuction()
language plpgsql
as $$
begin 
    update auction set stateOfAuction = FALSE where end_date < CURRENT_TIMESTAMP + '1 hour';
end;
$$;

create or replace function AuctionEndVerification(rec_artigo_ean BIGINT) returns BOOLEAN
language plpgsql
as $$
declare
	x BOOLEAN;
begin
	select stateOfAuction into x from auction where artigo_ean = (rec_artigo_ean);
	return(x);
exception
	when others then
		raise exception 'error';
end;
$$;

create or replace procedure bidNotification(artigo_ean BIGINT, username VARCHAR)
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
		if r.users_username <> (username) then
			insert into notification values(CONCAT('A sua bid de ',r.max,' no LeilaoID: ',artigo_ean,' foi ultrapassada'),CURRENT_TIMESTAMP,FALSE,r.users_username,artigo_ean);
		end if;
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

/*------------------------------------------------------*/

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
/***********************************************************************
**************************************************************************/

create or replace function func_trig_update_on_auction() returns trigger
language plpgsql
as $$
begin
	update auction set actual_bid_price=new.bid_price where artigo_ean=new.auction_artigo_ean;
	return new;
end;
$$;


create trigger Bid_Auction
	after insert on bid
	for each row
		execute procedure func_trig_update_on_auction();
/*****************************************************************************
******************************************************************************/
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

/******************************************************
*******************************************************/
create or replace function func_trig_Send_Message() returns trigger
language plpgsql
as $$
declare
    c1 cursor for 
        select users_username from users_auction 
		where auction_artigo_ean=new.auction_artigo_ean
		union 
		select users_username 
		from message 
		where auction_artigo_ean=new.auction_artigo_ean;
	
begin
	for r in c1
	loop
		if(new.users_username<>r.users_username) then
			insert into notification values(CONCAT('Nova Mensagem no Leilao ',new.auction_artigo_ean,' de ',new.users_username),CURRENT_TIMESTAMP,FALSE,r.users_username,new.auction_artigo_ean);
		end if;
	end loop;
	return new;
end;
$$;

create trigger Message_Notification
	after insert on message
	for each row
			execute procedure func_trig_Send_Message();

/******************************************************
*******************************************************/
create or replace procedure details(artigo_ean BIGINT)
language plpgsql
as $$
declare
    c1 cursor for 
        select bid_price, users_username
        from bid
        where auction_artigo_ean = (artigo_ean);
    c2 cursor for 
        select text, users_username
        from message
        where auction_artigo_ean = (artigo_ean);
begin 
    create table temp1(bid_price FLOAT, users_username VARCHAR(512));
    create table temp2(message_notif VARCHAR(512), users_username VARCHAR(512));
    for r in c1
    loop
        insert into temp1 values(r.bid_price,r.users_username);
    end loop;

    for r in c2
    loop
        insert into temp2 values(r.text,r.users_username);
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

