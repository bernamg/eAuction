##
## =============================================
## ============== Bases de Dados ===============
## ============== LEI  2020/2021 ===============
## =============================================
## =================== Demo ====================
## =============================================
## =============================================
## === Department of Informatics Engineering ===
## =========== University of Coimbra ===========
## =============================================
##
## Authors: 
##   Nuno Antunes <nmsa@dei.uc.pt>
##   BD 2021 Team - https://dei.uc.pt/lei/
##   University of Coimbra

from flask import Flask, jsonify, request
import logging, psycopg2, time
import random 
import string
import datetime
import os
app = Flask(__name__) 
from passlib.context import CryptContext

pwd_context = CryptContext(
        schemes=["pbkdf2_sha256"],
        default="pbkdf2_sha256",
        pbkdf2_sha256__default_rounds=30000
)

def encrypt_password(password):
    return pwd_context.encrypt(password)


def check_encrypted_password(password, hashed):
    return pwd_context.verify(password, hashed)

@app.route('/') 
def hello(): 
    return """

    Hello World!  <br/>
    <br/>
    Check the sources for instructions on how to use the endpoints!<br/>
    <br/>
    BD 2021 Team<br/>
    <br/>
    """


##########################################################
## Read Messages                                     CHECK
##########################################################

@app.route("/dbproj/leiloes/mensagens/<AuthToken>/<artigo_ean>", methods=['GET'], strict_slashes=True)
def get_messages(AuthToken,artigo_ean):
    logger.info("###              DEMO: GET /leiloes/mensagens/<AuthToken>/<artigo_ean>              ###");   

    conn = db_connection()
    cur = conn.cursor()
    
    #Token Validation
    try:
        cur.execute("CALL TokenDateValidation();")
        cur.execute("commit")
        cur.execute("select username from users where token_login = %s", (AuthToken,))
        rows = cur.fetchall()
        row = rows[0]
    except:
        return 'Token inexistente ou Sessao Expirada'

    try:
        #Ver se o leilao existe
        cur.execute("select IsAuctionCorrect(%s)",(artigo_ean,))
        rows = cur.fetchall()
        row = rows[0]
        if(row[0]==None):
            return jsonify('Leilao nao encontrado')

        cur.execute("SELECT id, text, users_username FROM message where auction_artigo_ean =%s order by id desc",(artigo_ean,))
        rows = cur.fetchall()
    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(error)
        result = 'Failed!'

    payload = []
    logger.debug("Messages print")
    for row in rows:
        logger.debug(row)
        content = {'ID': int(row[0]), 'Mensagem': row[1], 'User':row[2]}
        payload.append(content) # appending to the payload to be returned

    conn.close()
    return jsonify(payload)

##########################################################
## Create Auction                                    CHECK
##########################################################

@app.route("/dbproj/leilao/<AuthToken>", methods=['POST'])
def create_Auction(AuthToken):
    logger.info("###              DEMO: POST /leilao              ###");   
    payload = request.get_json()

    conn = db_connection()
    cur = conn.cursor()

    logger.info("---- new Auction  ----")
    logger.debug(f'payload: {payload}')

    #   Token Validation
    try:
        cur.execute("CALL TokenDateValidation();")
        cur.execute("commit")
        cur.execute("select username from users where token_login = %s", (AuthToken,))
        rows = cur.fetchall()
        row = rows[0]
    except:
        return 'Token inexistente ou Sessao Expirada'
    
    try:
        #Inserir na tabela auction
        statement = """
                    INSERT INTO auction (artigo_ean, min_price, end_date, description, actual_bid_price ,titulo, stateOfAuction) 
                            VALUES ( %s,   %s ,   %s ,  %s, %s, %s, TRUE)"""

        values = (payload["artigo_ean"], payload["min_price"], payload["end_date"], payload["description"], payload["min_price"],payload["titulo"])

        cur.execute(statement, values)
        #Associar auction a user
        statement = """ INSERT into users_auction (users_username, auction_artigo_ean)
                            VALUES(%s , %s)"""
        values = (row, payload["artigo_ean"])
        cur.execute(statement, values)
        cur.execute("commit")

        result = 'leilaoID ' + str(payload["artigo_ean"])
    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(error)
        result = 'Failed to create Auction!'
    finally:
        if conn is not None:
            conn.close()

    return jsonify(result)

##########################################################
## Edit Auction                                      CHECK
##########################################################

@app.route("/dbproj/leilao/<AuthToken>/<artigo_ean>", methods=['PUT'])
def update_auction(AuthToken,artigo_ean):
    logger.info("###              DEMO: PUT /leiao              ###");   
    content = request.get_json()

    conn = db_connection()
    cur = conn.cursor()
    
    #PROTECOES
    try:
        cur.execute("CALL TokenDateValidation();")
        cur.execute("commit")
    except:
        return 'Token inexistente ou Sessao Expirada'

    try:
        #Ver se o user existe e esta logado
        cur.execute("select IsUserLogged(%s)",(AuthToken,))
        rows_username = cur.fetchall()
        row_username = rows_username[0]
        if(row_username[0]==None):
            return jsonify('User Incorreto ou Sessao Expirada')
    
        #Ver se o leilao pertence ao User
        cur.execute("select IsAuctionFromUser(%s,"+artigo_ean+");",(row_username[0],))
        rows = cur.fetchall()
        row = rows[0]
        if(row[0] == None):
            return jsonify('Erro ao alterar o leilao') 
    except:
        return jsonify('Failed on first try!')
   
    if "titulo" not in content and "description" not in content:
        return jsonify("Erro, zero campos para alterar")

    if "description" in content and "titulo" in content:
        if content["description"] is None or content["titulo"] is None :
            logger.info("---- Update Auction [Campo Vazio]  ----")
            return jsonify("Os campos não devem estar vazios")

        logger.info("---- Update Auction [Titulo, Description]  ----")
        logger.info(f'content: {content}')

        statement ="""
                UPDATE auction 
                  SET Titulo = %s, description = %s
                WHERE artigo_ean = %s"""

        values = (content["titulo"], content["description"], artigo_ean)
        
        try:
            res = cur.execute(statement, values)
            result = f'Updated: {cur.rowcount}'
            cur.execute("commit")
        except (Exception, psycopg2.DatabaseError) as error:
            logger.error(error)
            result = 'Failed!'
        finally:
            if conn is not None:
                conn.close()
        return jsonify(result)

    if "description" not in content:
        if content["titulo"] is None:
            logger.info("---- Update Auction [Campo Vazio]  ----")
            return jsonify("Os campos não devem estar vazios")

        logger.info("---- Update Auction [Titulo]  ----")
        logger.info(f'content: {content}')

        statement ="""
                UPDATE auction 
                  SET Titulo = %s
                WHERE artigo_ean = %s"""

        values = (content["titulo"], artigo_ean)
        try:
            res = cur.execute(statement, values)
            result = f'Updated: {cur.rowcount}'
            cur.execute("commit")
        except (Exception, psycopg2.DatabaseError) as error:
            logger.error(error)
            result = 'Failed!'
        finally:
            if conn is not None:
                conn.close()
        return jsonify(result)

    if "titulo" not in content:
        if content["description"] is None:
            logger.info("---- Update Auction [Campo Vazio]  ----")
            return jsonify("Os campos não devem estar vazios")

        logger.info("---- Update Auction [Description]  ----")
        logger.info(f'content: {content}')

        statement ="""
                UPDATE auction 
                  SET description = %s
                WHERE artigo_ean = %s"""

        values = (content["description"], artigo_ean)
        try:
            res = cur.execute(statement, values)
            result = f'Updated: {cur.rowcount}'
            cur.execute("commit")
        except (Exception, psycopg2.DatabaseError) as error:
            logger.error(error)
            result = 'Failed!'
        finally:
            if conn is not None:
                conn.close()
        return jsonify(result)

##########################################################
## Write Message                                     CHECK
########################################################## 

@app.route("/leilao10/<AuthToken>/<artigo_ean>", methods=['PUT'])
def write_message(AuthToken,artigo_ean):
    logger.info("###              DEMO: PUT /message              ###");   
    content = request.get_json()

    conn = db_connection()
    cur = conn.cursor()


    #if content["ndep"] is None or content["nome"] is None :
    #    return 'ndep and nome are required to update'

    if "text" not in content:
        return 'message are required to update'
    
    if content["text"] is None:
        return 'Empty Message'

    logger.info("---- write message  ----")
    logger.info(f'content: {content}')

    try:
        cur.execute("CALL TokenDateValidation();")
        cur.execute("commit")
        cur.execute("select username from users where token_login = %s", (AuthToken,))
        rows = cur.fetchall()
        row = rows[0]
    except:
        return 'Token inexistente ou Sessao Expirada'

    # parameterized queries, good for security and performance
    statement ="""
                insert into message values(%s,DEFAULT,%s,%s) """


    values = (content["text"],row[0],artigo_ean)
    

    try:
        res = cur.execute(statement, values)
        result = f'Updated: {cur.rowcount}'
        cur.execute("commit")
    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(error)
        result = 'Failed!'
    finally:
        if conn is not None:
            conn.close()
    return jsonify(result)

##########################################################
## Register User                                     CHECK
########################################################## 

@app.route("/dbproj/users/", methods=['POST'])
def register_person():
    logger.info("###              DEMO: POST /users              ###");   
    payload = request.get_json()

    conn = db_connection()
    cur = conn.cursor()

    logger.info("---- new user  ----")
    logger.debug(f'payload: {payload}')
   
    # parameterized queries, good for security and performance
    statement = """
                  INSERT INTO users (username, email, password) 
                          VALUES ( %s,   %s ,   %s )"""

    values = (payload["username"], payload["email"],encrypt_password( payload["password"]))
    
    try:
        cur.execute(statement, values)
        cur.execute("commit")
        result = 'Registered!'
    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(error)
        result = 'Failed!'
    finally:
        if conn is not None:
            conn.close()

    return jsonify(result)

##########################################################
## Login User                                        CHECK
########################################################## 

@app.route("/dbproj/users", methods=['PUT'])
def login_action():
    logger.info("###              DEMO: PUT /departments              ###");   
    content = request.get_json()

    conn = db_connection()
    cur = conn.cursor()


    if "username" not in content or "password" not in content:
        return 'username and password are required to update'

    if content["username"] is None or content["password"] is None :
        return 'username and password are required to update'

    
    logger.info(f'content: {content}')

    # parameterized queries, good for security and performance
    try:
        res = cur.execute("select username, password from users where username = %s;",(content["username"],))
        if(cur.rowcount == 0):
            result = f'Erro: couldn´t login'
            return jsonify(result)
        rows = cur.fetchall()
        row=rows[0]
        logger.info("row: "+str(row[1]))
        
        if check_encrypted_password(content["password"], row[1])==False:
            return jsonify("Password Errada")
        else:
            letters = string.ascii_lowercase
            result_str = ''.join(random.choice(letters) for i in range(5))
            result = f'authToken: ' + result_str
            statement = """ update users set token_login = %s, validade = (CURRENT_TIMESTAMP + '2 hour') where username = %s """
            values = (result_str,content["username"])
            cur.execute(statement,values)
            cur.execute("commit")
    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(error)
        result = 'Failed!'
    finally:
        if conn is not None:
            conn.close()
    return jsonify(result)

##########################################################
## Ver todos os leiloes e sua descricao              CHECK
########################################################## 

@app.route("/dbproj/leiloes", methods=['GET'], strict_slashes=True)
def get_all_auctions():
    logger.info("###              DEMO: GET /auctions              ###");   
    conn = db_connection()
    cur = conn.cursor()
    cur.execute("CALL finishAuction();")
    cur.execute("commit")
    cur.execute("SELECT artigo_ean, description FROM auction where stateofauction=TRUE")
    rows = cur.fetchall()

    payload = []
    logger.debug("---- auctions  ----")
    for row in rows:
        logger.debug(row)
        content = {'artigo_ean': int(row[0]), 'description': row[1]}
        payload.append(content) # appending to the payload to be returned

    conn.close()
    return jsonify(payload)

################################################################
## Procura por um leilao com uma descricao ou artigo_ean CHECK
################################################################

@app.route("/dbproj/leiloes/<description>", methods=['GET'])
def get_oneAuction(description):
    logger.info("###              DEMO: GET /users/<description>              ###");   

    logger.debug(f'description: {description}')

    conn = db_connection()
    cur = conn.cursor()
    cur.execute("CALL finishAuction();")
    cur.execute("commit")
    str = "SELECT artigo_ean, description FROM auction where description LIKE '%" + description + "%' and stateofauction=TRUE"

    try:
        cur.execute(str)
        if(cur.rowcount == 0):
            cur.execute("SELECT artigo_ean, description FROM auction where artigo_ean = %s and stateofauction=TRUE", (description,) )
        rows = cur.fetchall()
    except(Exception, psycopg2.DatabaseError) as error:
        logger.error(error)
        rows = "0 results"

    conn.close ()
    return jsonify(rows)

##########################################################
## Ver detalhes de um determinado leilao             CHECK
########################################################## 

@app.route("/dbproj/leilao/<artigo_ean>", methods=['GET'])
def get_DetailsAuction(artigo_ean):
    logger.info("###              DEMO: GET /users/<description>              ###");   

    logger.debug(f'artigo_ean: {artigo_ean}')

    conn = db_connection()
    cur = conn.cursor()
    paypload = []

    try:
        cur.execute("SELECT artigo_ean, min_price, end_date, description, actual_bid_price, titulo FROM auction where artigo_ean = %s", (artigo_ean,) )
        rows = cur.fetchall()
        row = rows[0]
        content = {'artigo_ean': int(row[0]), 'min_price': row[1], 'end_date': row[2], 'description': row[3], 'actual_bid_price': row[4], 'titulo': row[5]}
        paypload.append(content)

        cur.execute("CALL details("+artigo_ean+");")
        cur.execute("select bid_price, users_username from temp1;")
        rows = cur.fetchall()
        for row in rows:
            content = {'bid:price': int(row[0]), 'users_username': row[1]}
            paypload.append(content)

        cur.execute("select message_notif, users_username from temp2;")
        rows = cur.fetchall()
        for row in rows:
            content = {'message_notif': row[0], 'users_username': row[1]}
            paypload.append(content)
        
        cur.execute("drop table temp1, temp2;")
        cur.execute("commit")
    except(Exception, psycopg2.DatabaseError) as error:
        logger.error(error)
        rows = "0 results"

    conn.close ()
    return jsonify(paypload)

##########################################################
## Ver notificacoes e elimina depois                 CHECK
########################################################## 

@app.route("/users2/<AuthToken>", methods=['GET'])
def get_Notifications(AuthToken):
    logger.info("###              DEMO: GET /users2/AuthToken              ###");   
    conn = db_connection()
    cur = conn.cursor()
    payload = []

    #Ver se token esta valido
    try:
        cur.execute("CALL TokenDateValidation();")
        cur.execute("commit")
        cur.execute("select username from users where token_login = %s", (AuthToken,))
        rows = cur.fetchall()
        row = rows[0]
    except:
        return 'Token inexistente ou Sessao Expirada'

    try:
        cur.execute("select message_notif,hour from notification where users_username=%s order by hour desc",(row[0],))
        rowsN = cur.fetchall()
        for rown in rowsN:
            logger.debug(rown)
            content = {'Message': rown[0], 'Data': rown[1]}
            payload.append(content) # appending to the payload to be returned
        
        #Eliminar notificacoes removeNotif
        cur.execute("CALL removeNotif(%s);",(row[0],))
        cur.execute("commit")
    except(Exception, psycopg2.DatabaseError) as error:
        logger.error(error)
        rows = "0 results notifications"

    conn.close ()
    return jsonify(payload)

##########################################################
## Bid Auction                                       CHECK
##########################################################

@app.route("/dbproj/bid/<AuthToken>/<auction_artigo_ean>/<bid_price>", methods=['GET'])
def bid_action(AuthToken,auction_artigo_ean,bid_price):
    logger.info("###              DEMO: PUT /bid action              ###");   
    content = request.get_json()

    conn = db_connection()
    cur = conn.cursor()


    logger.info("---- update bid  ----")
    logger.info(f'auction_artigo_ean: {auction_artigo_ean}' + f'bid_price: {bid_price} '+ f'AuthToken: {AuthToken}')

    #Ver se token e valido
    try:
        cur.execute("CALL TokenDateValidation();")
        cur.execute("commit")
        cur.execute("select username from users where token_login = %s", (AuthToken,))
        rowsNew = cur.fetchall()
    except:
        return 'Token inexistente ou Sessao Expirada'

    #Verificacao
    try:
        cur.execute("CALL finishAuction();")
        cur.execute("select AuctionEndVerification(%s)",(auction_artigo_ean,))
        rows = cur.fetchall()
        row=rows[0]  
        if(row[0]==False):
            return jsonify("Leilao ja terminado")
        cur.execute("select username from users_auction, users where auction_artigo_ean=%s and users.token_login= %s and username=users_auction.users_username;",(auction_artigo_ean,AuthToken,))
        if(cur.rowcount > 0):
            return jsonify("Nao pode fazer licitacoes no seu leilao")
        cur.execute("select bid.bid_price from bid where bid.bid_price >= %s and auction_artigo_ean = %s;",(bid_price,auction_artigo_ean,))
        if(cur.rowcount >= 1):
            return jsonify("Bid mais baixa que o necessario")
        cur.execute("select min_price from auction where artigo_ean = %s and min_price<=%s;",(auction_artigo_ean,bid_price,))
        logger.info
        if(cur.rowcount == 0):
            return jsonify("Bid abaixo do minimo")
    except (Exception, psycopg2.DatabaseError) as error:
            logger.error(error)

    try:
      #  cur.execute("select username from users where token_login = %s", (AuthToken,))
       # rows = cur.fetchall()
        row = rowsNew[0]
        logger.info("---- username  ----" +row[0] )
        statement = """ insert into bid values(%s,%s,%s) """
        values = (bid_price,auction_artigo_ean,row[0])
        cur.execute(statement,values)
        cur.execute("commit")
        #statement = """update auction set actual_bid_price = %s where artigo_ean = %s"""
        #values = (bid_price,auction_artigo_ean)
        #cur.execute(statement,values)
        #result = f'successfully bid'
        #cur.execute("commit")

        logger.info("BEFORE BIDNOTIFICATION")
        cur.execute("CALL bidNotification(%s,%s)",(auction_artigo_ean,row[0],))
        logger.info("Notification Sended")
        result = f'successfully bid'
    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(error)
        result = 'Failed!'
        conn.rollback()
    finally:
        if conn is not None:
            conn.close()
    return jsonify(result)

##########################################################
## Atualizar leiloes acabados                        CHECK
########################################################## 

@app.route("/dbproj/auction/update", methods=['GET'])
def finish_auction():
    logger.info("###              DEMO: get /bid auction              ###");   
    content = request.get_json()

    conn = db_connection()
    cur = conn.cursor()
    try:
        cur.execute("CALL finishAuction();")
        cur.execute("commit")
        result = f'state of auctions updated successfully '
        logger.info("---- finish auctions  ----")
    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(error)
        result = 'Failed!'
    finally:
        if conn is not None:
            conn.close()
    return jsonify(result)

##########################################################
## Ver todos os leiloes em que tem atividade         CHECK         
########################################################## 

@app.route("/dbproj/auction/activity/<AuthToken>", methods=['GET'])
def activityOfUsers(AuthToken):
    logger.info("###              DEMO: get /bid auction              ###");   
    content = request.get_json()
    conn = db_connection()
    cur = conn.cursor()
    payload = []

    statement =  """ select users_auction.auction_artigo_ean from users_auction where users_username = %s union select bid.auction_artigo_ean from bid where users_username = %s ; """

    try:
        cur.execute("CALL TokenDateValidation();")
        cur.execute("commit")
        cur.execute("select username from users where token_login = %s", (AuthToken,))
        rows = cur.fetchall()
        row = rows[0]
    except:
        return 'Token inexistente ou Sessao Expirada'

    try:
        values = (row[0],row[0])
        cur.execute(statement,values)
        rows = cur.fetchall()
        for row in rows:
            cur.execute("select titulo, description from auction where artigo_ean = %s; ",(row[0],))
            rows1 = cur.fetchall()
            row1 = rows1[0]
            content = {"Titulo ":row1[0],"Descrição ":row1[1] ,"Artigo_ean ": row[0]}
            payload.append(content)
        cur.execute("commit")
    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(error)
    finally:
        if conn is not None:
            conn.close()
    return jsonify(payload)

##########################################################
## DATABASE ACCESS
##########################################################

def db_connection():
    username = os.getenv('dbusername')
    password = os.getenv('dbpassword')
    databaseE = os.getenv('dbdatabase')
    logger.info("username: "+str(username))
    logger.info("password: "+str(password))
    db = psycopg2.connect(user = username,
                            password = password,
                            host = "db",
                            port = "5432",
                            database = databaseE)
    return db


##########################################################
## MAIN
##########################################################
if __name__ == "__main__":

    # Set up the logging
    logging.basicConfig(filename="logs/log_file.log")
    logger = logging.getLogger('logger')
    logger.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)

    # create formatter
    formatter = logging.Formatter('%(asctime)s [%(levelname)s]:  %(message)s',
                              '%H:%M:%S')
                              # "%Y-%m-%d %H:%M:%S") # not using DATE to simplify
    ch.setFormatter(formatter)
    logger.addHandler(ch)


    time.sleep(1) # just to let the DB start before this print :-)


    logger.info("\n---------------------------------------------------------------\n" + 
                  "API v1.0 online: http://localhost:8080/departments/\n\n")


    

    app.run(host="0.0.0.0", debug=True, threaded=True)
