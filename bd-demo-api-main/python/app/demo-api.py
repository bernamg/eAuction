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
## Obtain all departments, in JSON format
##
## To use it, access: 
## 
##   http://localhost:8080/departments/
##

@app.route("/users/", methods=['GET'], strict_slashes=True)
def get_all_departments():
    logger.info("###              DEMO: GET /users              ###");   

    conn = db_connection()
    cur = conn.cursor()

    cur.execute("SELECT username, email FROM users")
    rows = cur.fetchall()

    payload = []
    logger.debug("---- users  ----")
    for row in rows:
        logger.debug(row)
        content = {'username': (row[0]), 'email': row[1]}
        payload.append(content) # appending to the payload to be returned

    conn.close()
    return jsonify(payload)



##
##      Demo GET
##
## Obtain department with ndep <ndep>
##
## To use it, access: 
## 
##   http://localhost:8080/departments/10
##

@app.route("/departments/<ndep>", methods=['GET'])
def get_department(ndep):
    logger.info("###              DEMO: GET /departments/<ndep>              ###");   

    logger.debug(f'ndep: {ndep}')

    conn = db_connection()
    cur = conn.cursor()

    cur.execute("SELECT ndep, nome, local FROM dep where ndep = %s", (ndep,) )
    rows = cur.fetchall()

    row = rows[0]

    logger.debug("---- selected department  ----")
    logger.debug(row)
    content = {'ndep': int(row[0]), 'nome': row[1], 'localidade': row[2]}

    conn.close ()
    return jsonify(content)

## CREATE AUCTION

@app.route("/leilao/", methods=['POST'])
def create_Auction():
    logger.info("###              DEMO: POST /leilao              ###");   
    payload = request.get_json()

    conn = db_connection()
    cur = conn.cursor()

    logger.info("---- new Auction  ----")
    logger.debug(f'payload: {payload}')

    # parameterized queries, good for security and performance
    statement = """
                  INSERT INTO auction (artigo_ean, min_price, end_date, description, titulo) 
                          VALUES ( %s,   %s ,   %s ,  %s, %s)"""

    values = (payload["artigo_ean"], payload["min_price"], payload["end_date"], payload["AuthToken"],payload["titulo"],payload["AuthToken"])

    try:
        cur.execute(statement, values)
     
        cur.execute("SELECT username FROM users where token_login = %s", (AuthToken,) )
        rows = cur.fetchall()
        row = rows[0]
        
        statement = """ INSERT into users_auction (users_username, auction_artigo_ean)
                            VALUES(%s , %s)"""
        values = (row, payload["artigo_ean"])

        cur.execute("commit")
        result = 'leilaoID ' + artigo_ean
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


    if content["username"] is None or content["password"] is None :
        return 'username and password are required to update'

    if "username" not in content or "password" not in content:
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
    logger.info("###              DEMO: GET /users/<artigo_ean>              ###");   

    logger.debug(f'artigo_ean: {description}')

    conn = db_connection()
    cur = conn.cursor()

    cur.execute("SELECT artigo_ean, description FROM auction where description like %s", (description,) )
    if(cur.rowcount == 0):
        cur.execute("SELECT artigo_ean, description FROM auction where artigo_ean = %s", (description,) )
    #logger.debug(f'o que retorna {cur.rowcount}')  
    rows = cur.fetchall()

    row = rows[0]

    logger.debug("---- selected auction  ----")
    logger.debug(row)
    content = {'artigo_ean': int(row[0]), 'description': row[1]}

    conn.close ()
    return jsonify(content)

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



