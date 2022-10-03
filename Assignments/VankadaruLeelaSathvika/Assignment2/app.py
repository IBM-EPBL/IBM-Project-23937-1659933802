import imp
from flask import Flask, render_template,request,redirect
import sqlite3 as sql
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
        try:
            name = request.form['name']
            email = request.form['email']
            phone = request.form['phone']
            password = request.form['password']
            with sql.connect("User_Database.db") as conn:
                cur = conn.cursor()
                cur.execute("Insert into users (name,email,phone,password) values (?,?,?,?)",(name,email,phone,password))
                conn.commit()
                msg = "Record Successfully Added!" 
        except:
            conn.rollback()
            msg = "error in insert Operation"
        finally:
            return render_template("users.html",msg=msg)
            conn.close()

@app.route('/users')
def users():
    con = sql.connect("User_Database.db")
    con.row_factory = sql.Row
   
    cur = con.cursor()
    cur.execute("select * from users")
   
    users = cur.fetchall()
    return render_template("users.html", users = users)