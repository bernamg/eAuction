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
app = Flask(__name__) 


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




##
##      Demo GET
##
## Obtain department with ndep <ndep>
##
## To use it, access: 
## 
##   http://localhost:8080/departments/10
##

##########################################################
## Create Auction
##########################################################

@app.route("/leilao/<AuthToken>", methods=['POST'])
def create_Auction(AuthToken):
    logger.info("###              DEMO: POST /leilao              ###");   
    payload = request.get_json()

    conn = db_connection()
    cur = conn.cursor()

    logger.info("---- new Auction  ----")
    logger.debug(f'payload: {payload}')

    try:
        cur.execute("SELECT username FROM users where token_login = %s", (AuthToken,) )
        rows = cur.fetchall()
        row = rows[0]
    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(error)
        result = 'Failed, Wrong Token!'
    try:
         # parameterized queries, good for security and performance
        statement = """
                    INSERT INTO auction (artigo_ean, min_price, end_date, description, actual_bid_price ,titulo, stateOfAuction) 
                            VALUES ( %s,   %s ,   %s ,  %s, %s, %s, TRUE)"""

        values = (payload["artigo_ean"], payload["min_price"], payload["end_date"], payload["description"], payload["min_price"],payload["titulo"])

        cur.execute(statement, values)
        #cur.execute("SELECT username FROM users where token_login = %s", (AuthToken,) )
        #rows = cur.fetchall()
        #row = rows[0]

        statement = """ INSERT into users_auction (users_username, auction_artigo_ean)
                            VALUES(%s , %s)"""
        values = (row, payload["artigo_ean"])
        cur.execute(statement, values)
        cur.execute("commit")

        #statement = """ INSERT into edition values( DEFAULT, %s, %s, %s)"""
        #values = (payload["titulo"],payload["description"],payload["artigo_ean"])
        #cur.execute(statement, values)
        #cur.execute("commit")
        #logger.info("Added to editions")

        result = 'leilaoID ' + str(payload["artigo_ean"])
    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(error)
        result = 'Failed to create Auction!'
    finally:
        if conn is not None:
            conn.close()

    return jsonify(result)

##########################################################
## Edit Auction
##########################################################

@app.route("/leilao/<AuthToken>/<artigo_ean>", methods=['PUT'])
def update_auction(AuthToken,artigo_ean):
    logger.info("###              DEMO: PUT /leiao              ###");   
    content = request.get_json()

    conn = db_connection()
    cur = conn.cursor()
    
    #Ver se o Token existe
    try:
        cur.execute("select username from users where token_login = %s", (AuthToken,))
        rows = cur.fetchall()
        row = rows[0]
    except:
        return jsonify('Error Wrong Token')

    #Ver se o leilao pertence ao User
    try:
        cur.execute("select auction_artigo_ean from users_auction where users_username = %s and auction_artigo_ean = %s", (row,artigo_ean,))
        rows = cur.fetchall()
        row = rows[0]
    except:
        return jsonify('Error in artigo_ean')
   
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

            statement = """ INSERT into edition values( DEFAULT, %s, %s, %s)"""
            values = (content["titulo"],content["description"],artigo_ean)
            
            cur.execute(statement, values)
            cur.execute("commit")
            logger.info("Added to editions")

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

            cur.execute("SELECT description FROM auction where artigo_ean = %s", (artigo_ean,) )
            rows = cur.fetchall()
            row = rows[0]
            
            statement = """ INSERT into edition values( DEFAULT, %s, %s, %s)"""
            values = (content["titulo"],row,artigo_ean)
            cur.execute(statement, values)
            cur.execute("commit")
            logger.info("Added to editions")
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

            cur.execute("SELECT titulo FROM auction where artigo_ean = %s", (artigo_ean,) )
            rows = cur.fetchall()
            row = rows[0]
            
            statement = """ INSERT into edition values( DEFAULT, %s, %s, %s)"""
            values = (row,content['description'],artigo_ean)
            cur.execute(statement, values)
            cur.execute("commit")
            logger.info("Added to editions")

        except (Exception, psycopg2.DatabaseError) as error:
            logger.error(error)
            result = 'Failed!'
        finally:
            if conn is not None:
                conn.close()
        return jsonify(result)


##########################################################
## Write Message
########################################################## 


@app.route("/leilao/<AuthToken>/<artigo_ean>", methods=['PUT'])
def write_message(AuthToken,artigo_ean):
    logger.info("###              DEMO: PUT /message              ###");   
    content = request.get_json()

    conn = db_connection()
    cur = conn.cursor()


    #if content["ndep"] is None or content["nome"] is None :
    #    return 'ndep and nome are required to update'

    if "text" not in content:
        return 'message are required to update'


    logger.info("---- write message  ----")
    logger.info(f'content: {content}')

    try:
        cur.execute("select username from users where token_login = %s", (AuthToken,))
        rows = cur.fetchall()
        row = rows[0]
    except:
        return 'Error'

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



##
##      Demo POST
##
## Add a new department in a JSON payload
##
## To use it, you need to use postman or curl: 
##
##   curl -X POST http://localhost:8080/departments/ -H "Content-Type: application/json" -d '{"localidade": "Polo II", "ndep": 69, "nome": "Seguranca"}'
##


@app.route("/users/", methods=['POST'])
def add_departments():
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

    values = (payload["username"], payload["email"], payload["password"])

    try:
        cur.execute(statement, values)
        cur.execute("commit")
        result = 'Inserted!'
    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(error)
        result = 'Failed!'
    finally:
        if conn is not None:
            conn.close()

    return jsonify(result)




##
##      Demo PUT
##
## Update a department based on the a JSON payload
##
## To use it, you need to use postman or curl: 
##
##   curl -X PUT http://localhost:8080/departments/ -H "Content-Type: application/json" -d '{"ndep": 69, "localidade": "Porto"}'
##
@app.route("/departments/", methods=['PUT'])
def login_action():
    logger.info("###              DEMO: PUT /departments              ###");   
    content = request.get_json()

    conn = db_connection()
    cur = conn.cursor()


    if "username" not in content or "password" not in content:
        return 'username and password are required to update'

    if content["username"] is None or content["password"] is None :
        return 'username and password are required to update'

    

    logger.info("---- update department  ----")
    logger.info(f'content: {content}')

    # parameterized queries, good for security and performance
    statement ="""
                select username, password from users
                where password= %s and username = %s;"""


    values = (content["password"], content["username"])

    try:
        res = cur.execute(statement, values)
        #result = f'Updated: {cur.rowcount}'
        if(cur.rowcount == 0):
            result = f'Erro: couldn´t login'
        else:
            letters = string.ascii_lowercase
            result_str = ''.join(random.choice(letters) for i in range(5))
            result = f'authToken: ' + result_str
            statement = """ update users set token_login = %s  where username = %s """
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


@app.route("/users/auctions", methods=['GET'], strict_slashes=True)
def get_all_auctions():
    logger.info("###              DEMO: GET /auctions              ###");   

    conn = db_connection()
    cur = conn.cursor()

    cur.execute("SELECT artigo_ean, description FROM auction")
    rows = cur.fetchall()

    payload = []
    logger.debug("---- auctions  ----")
    for row in rows:
        logger.debug(row)
        content = {'artigo_ean': int(row[0]), 'description': row[1]}
        payload.append(content) # appending to the payload to be returned

    conn.close()
    return jsonify(payload)

@app.route("/users/<description>", methods=['GET'])
def get_oneAuction(description):
    logger.info("###              DEMO: GET /users/<description>              ###");   

    logger.debug(f'description: {description}')

    conn = db_connection()
    cur = conn.cursor()

    str = "SELECT artigo_ean, description FROM auction where description LIKE '%" + description + "%'"

    try:
        cur.execute(str)
        if(cur.rowcount == 0):
            cur.execute("SELECT artigo_ean, description FROM auction where artigo_ean = %s", (description,) )
        rows = cur.fetchall()
    except(Exception, psycopg2.DatabaseError) as error:
        logger.error(error)
        rows = "0 results"

    conn.close ()
    return jsonify(rows)

@app.route("/users1/<artigo_ean>", methods=['GET'])
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
        cur.execute("select users_username, text from message where auction_artigo_ean = %s order by id", (artigo_ean,))
        rows = cur.fetchall()
        row = row[0]
        for row in rows:
            content = {'users_username':row[0],'text':row[1] }
            paypload.append(content)
    except(Exception, psycopg2.DatabaseError) as error:
        logger.error(error)
        rows = "0 results"

    conn.close ()
    return jsonify(paypload)


@app.route("/users2/<AuthToken>", methods=['GET'])
def get_Notifications(AuthToken):
    logger.info("###              DEMO: GET /users2/AuthToken              ###");   
    conn = db_connection()
    cur = conn.cursor()
    payload = []

    try:
        cur.execute("select username from users where token_login = %s;",(AuthToken,))
        rows = cur.fetchall()
        row = rows[0]

        cur.execute("select message_notif,hour from notification where users_username=%s order by hour desc",(row[0],))
        rowsN = cur.fetchall()
        for rown in rowsN:
            logger.debug(rown)
            content = {'Message': rown[0], 'Data': rown[1]}
            payload.append(content) # appending to the payload to be returned
        
        #Eliminar notificacoes removeNotif
    
        logger.info("Before removeNotif")   
        logger.info("Row[0] antes de remover "+ row[0])
        cur.execute("CALL removeNotif(%s);",(row[0],))
        cur.execute("commit")
        logger.info("removeNotif Done")
    except(Exception, psycopg2.DatabaseError) as error:
        logger.error(error)
        rows = "0 results notifications"

    conn.close ()
    return jsonify(payload)

@app.route("/dbproj/bid/<AuthToken>/<auction_artigo_ean>/<bid_price>", methods=['GET'])
def bid_action(AuthToken,auction_artigo_ean,bid_price):
    logger.info("###              DEMO: PUT /bid action              ###");   
    content = request.get_json()

    conn = db_connection()
    cur = conn.cursor()
    

    logger.info("---- update bid  ----")
    logger.info(f'auction_artigo_ean: {auction_artigo_ean}' + f'bid_price: {bid_price} '+ f'AuthToken: {AuthToken}')

    # parameterized queries, good for security and performance
    try:
        #Notificar antigo maior bider 
        #VER TITULO
           # cur.execute(" select users_username, bid_price from bid where bid_price = (select max(bid_price) from bid) and auction_artigo_ean= %s", (auction_artigo_ean,))
            #rows = cur.fetchall()
            #row = rows[0]

            #datetime_object = datetime.datetime.now()
            #statement = """INSERT INTO notification VALUES('A sua bid de %s foi ultrapassada',%s,%s,%s);"""
            #values = (row[1],datetime_object,row[0],auction_artigo_ean)
            #cur.execute(statement,values)
            logger.info("BEFORE BIDNOTIFICATION")
            cur.execute("CALL bidNotification("+auction_artigo_ean+");")
            logger.info("Notification Sended")

    except (Exception, psycopg2.DatabaseError) as error:
            logger.error(error)

    try:
        cur.execute("select username from users where token_login = %s", (AuthToken,))
        rows = cur.fetchall()
        #result = f'Updated: {cur.rowcount}'
        if(cur.rowcount == 0):
            result = f'there is no token'
        else:
            row = rows[0]
            logger.info("---- username  ----" +row[0] )
            statement = """ insert into bid values(%s,%s,%s) """
            values = (bid_price,auction_artigo_ean,row[0])
            cur.execute(statement,values)

            #verificar valores das  bids uqbas
            statement = """update auction set actual_bid_price = %s where artigo_ean = %s"""
            values = (bid_price,auction_artigo_ean)
            cur.execute(statement,values)
            result = f'successfully bid'
            cur.execute("commit")
    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(error)
        result = 'Failed!'
        conn.rollback()
    finally:
        if conn is not None:
            conn.close()
    return jsonify(result)


@app.route("/dbproj/auction/update", methods=['GET'])
def finish_auction():
    logger.info("###              DEMO: get /bid auction              ###");   
    content = request.get_json()

    conn = db_connection()
    cur = conn.cursor()
    statement = """ update auction set stateOfAuction = FALSE where end_date < CURRENT_TIMESTAMP  """
    
    try:
        cur.execute(statement)
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
## DATABASE ACCESS
##########################################################

def db_connection():
    db = psycopg2.connect(user = "aulaspl",
                            password = "aulaspl",
                            host = "db",
                            port = "5432",
                            database = "dbfichas")
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
