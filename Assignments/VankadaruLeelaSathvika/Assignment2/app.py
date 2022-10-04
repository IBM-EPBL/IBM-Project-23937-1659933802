import imp
from flask import Flask, render_template,request,redirect
import sqlite3 as sql
import ibm_db

conn = ibm_db.connect("DATABASE=bludb;HOSTNAME=824dfd4d-99de-440d-9991-629c01b3832d.bs2io90l08kqb1od8lcg.databases.appdomain.cloud;PORT=30119;SECURITY=SSL;SSLServerCertificate=DigiCertGlobalRootCA.crt;UID=dpq83331;PWD=wc6BJHXIkfHrCmUg",'','')
#conn = ibm_db.connect("DATABASE=<databasename>;HOSTNAME=<your-hostname>;PORT=<portnumber>;SECURITY=SSL;SSLServerCertificate=DigiCertGlobalRootCA.crt;UID=<username>;PWD=<password>",'','')


app = Flask(__name__)

@app.route('/')
def index():
    return render_template('/index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/signup')
def signup():
    return render_template('signup.html')

@app.route('/signin')
def signin():
    return render_template('signin.html')

@app.route('/postSignUpData',methods =['POST','GET'])
def postSignUpData():
    if request.method == 'POST':
        #sqlite
        # try:
        #     name = request.form['name']
        #     email = request.form['email']
        #     phone = request.form['phone']
        #     password = request.form['password']
        #     with sql.connect("User_Database.db") as conn:
        #         cur = conn.cursor()
        #         cur.execute("Insert into users (name,email,phone,password) values (?,?,?,?)",(name,email,phone,password))
        #         conn.commit()
        #         msg = "Record Successfully Added!" 
        # except:
        #     conn.rollback()
        #     msg = "error in insert Operation"
        # finally:
        #     return render_template("users.html",msg=msg)
        #     conn.close()

        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        password = request.form['password']

        sql = "SELECT * FROM users WHERE name =?"
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(stmt,1,name)
        ibm_db.execute(stmt)
        account = ibm_db.fetch_assoc(stmt)
        if account:
            return render_template('users.html', msg="You are already a member, please login using your details")
        else:
            insert_sql = "INSERT INTO users VALUES (?,?,?,?)"
            prep_stmt = ibm_db.prepare(conn, insert_sql)
            ibm_db.bind_param(prep_stmt, 1, name)
            ibm_db.bind_param(prep_stmt, 2, email)
            ibm_db.bind_param(prep_stmt, 3, phone)
            ibm_db.bind_param(prep_stmt, 4, password)
            ibm_db.execute(prep_stmt)
        return render_template('index.html', msg="user Data saved successfuly..")

@app.route('/users')
def users():
    #sqlite
    # con = sql.connect("User_Database.db")
    # con.row_factory = sql.Row
   
    # cur = con.cursor()
    # cur.execute("select * from users")
   
    # users = cur.fetchall()
    # return render_template("users.html", users = users)
    users = []
    sql = "SELECT * FROM users"
    stmt = ibm_db.exec_immediate(conn, sql)
    dictionary = ibm_db.fetch_both(stmt)
    while dictionary != False:
        print ("The Name is : ",  dictionary)
        users.append(dictionary)
        dictionary = ibm_db.fetch_both(stmt)

    if users:
        return render_template("users.html", users = users)
