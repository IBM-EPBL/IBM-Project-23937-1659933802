from flask import Flask,flash, render_template,request,redirect
import credentials
import ibm_db
import ibm_boto3
from ibm_botocore.client import Config, ClientError

conn = ibm_db.connect("DATABASE="+credentials.DB2_DATABASE_NAME+";HOSTNAME="+credentials.DB2_HOST_NAME+";PORT="+credentials.DB2_PORT+";SECURITY=SSL;SSLServerCertificate=DigiCertGlobalRootCA.crt;UID="+credentials.DB2_UID+";PWD="+credentials.DB2_PWD+"",'','')

cos = ibm_boto3.resource("s3",
    ibm_api_key_id=credentials.COS_API_KEY_ID,
    ibm_service_instance_id=credentials.COS_INSTANCE_CRN,
    config=Config(signature_version="oauth"),
    endpoint_url=credentials.COS_ENDPOINT
)

class User:
    def __init__(self) -> None:
        pass

app = Flask(__name__)
app.secret_key = "FlaskNotFoundError"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/signup')
def signup():
    return render_template('signup.html')

@app.route('/signin')
def signin():
    return render_template('signin.html')


@app.route('/home')
def presentHome():
    return render_template('home.html')

@app.route('/profile')
def presentProfile():
    return render_template('profile.html')

@app.route('/expenses')
def presentExpenses():
    return render_template('expenses.html')

@app.route('/sample')
def presentSample():
    return render_template('sample.html')


@app.route('/postSignUpData',methods =['POST','GET'])
def postSignUpData():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        
        sql = "SELECT * FROM user WHERE email=?"
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(stmt,1,email)
        ibm_db.execute(stmt)
        account = ibm_db.fetch_assoc(stmt)
        if account:
            return render_template('signup.html', msg="You are already a member, please login using your details")
        else:
            insert_sql = "INSERT INTO user(email,password,name) VALUES (?,?,?)"
            prep_stmt = ibm_db.prepare(conn, insert_sql)
            ibm_db.bind_param(prep_stmt, 1, email)
            ibm_db.bind_param(prep_stmt, 2, password)
            ibm_db.bind_param(prep_stmt, 3, name)
            ibm_db.execute(prep_stmt)
        return render_template('signin.html', msg="Registration successfull..")

@app.route('/postSignInData',methods =['POST','GET'])
def postSignInData():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
    
        sql = "SELECT PASSWORD FROM user WHERE email=?"
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(stmt,1,email)
        ibm_db.execute(stmt)
        account = ibm_db.fetch_assoc(stmt)
        print(account)
        if account and account["PASSWORD"]==password:
            return render_template('home.html',email=email)
        else:
            return render_template('signin.html', invalidLogin="Your email or password is wrong!!")