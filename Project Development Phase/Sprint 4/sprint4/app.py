from flask import *
from database import *
from models import *
from random import *
from flask_mail import Mail, Message
from datetime import *
from time import *
database = Database()

app = Flask(__name__)
app.secret_key = "FlaskNotFoundError"
app.config['MAIL_SERVER'] = 'smtp.sendgrid.net'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'apikey'
app.config['MAIL_PASSWORD'] = credentials.SENDGRID_API_KEY
app.config['MAIL_DEFAULT_SENDER'] = credentials.MAIL_DEFAULT_SENDER
mail = Mail(app)

#Index
@app.route('/')
def index():
    return render_template('index.html')

#Signup
@app.route('/signup', methods = ['GET','POST'])
def signup():
    msg=None
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        account = database.fetchUser(email)
        if account:
            flash("You are already a member, please login using your details")
            return redirect('signin')
        else:
            if database.insertSignUpUserData(email,password,name):
                msg = Message('eXpenso Registration', recipients=[email])
                msg.body = 'Thank you for registering with eXpenso! Happy Managing!!'
                msg.html = """<h1>Sucessfully Registered with eXpenso</h1>
                                <h3>Thank you for registering with eXpenso! Happy Managing!!</h3>
                            """
                mail.send(msg)
                flash("Registration successfull...")
                return redirect('signin')
            else:
                msg="Unable to Register!! Try again"
    return render_template('signup.html',msg=msg)
#Signin
@app.route('/signin',methods = ["GET","POST"])
def signin():
    invalidLogin = None
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        if database.fetchUser(email):
            fetchedPassword = database.fetchPassword(email)
            if fetchedPassword==password:
                session['email']=email
                return redirect('home')
            else:
                invalidLogin="Your Password is wrong!!"                
        else:
            invalidLogin="You have not Registered yet!!"
    return render_template('signin.html',invalidLogin=invalidLogin)

@app.route('/signout')  
def signOut():  
    if 'email' in session:  
        session.pop('email',None)
        return redirect('/')
    return redirect('/')  
    
#Home
@app.route('/home')
def presentHome():
    if 'email' not in session:
        return redirect('/')
    email=session['email']
    user = database.fetchUser(email)
    totalExpenses = database.getTotalExpenseAmount(email)
    totalSavings = database.getDebitSavingsAmount(email)
    expenseFilter = "year"
    expenses = database.fetchExpensesPreview(email,5)
    monthExpenses=database.getExpensesThisYear(email)
    monthLabels=['January', 'February', 'March', 'April', 'May', 'June', 'July','August','September','October','November','December']
    monthExpenseList = [0]*12
    for expense in monthExpenses:
        monthExpenseList[int(expense["MONTH"])-1]=expense["AMOUNT"]
    totalLoanPaid = database.getTotalLoanPaid(email)
    totalLoanLeft = database.getTotalLoanLeft(email)
    reminders = database.readRemindersWithLimit(email)
    reminderList = []
    for reminder in reminders:
        days = (date(int(reminder["YEAR"]),int(reminder["MONTH"]),int(reminder["DATE"])) - date.today()).days
        label = "left"
        if days<0:
            continue
        elif days == 0:
            label = "today"
        name = reminder["REMINDERNAME"]
        reminderdate = reminder["DATE"]+"/"+reminder["MONTH"]
        description = reminder["DESCRIPTION"]
        reminderList.append([days,name,description,label,reminderdate])
    return render_template('home.html',user = user,expenseFilter = expenseFilter,totalExpenses = totalExpenses, totalSavings = totalSavings, expenses = expenses, monthLabels = monthLabels, monthExpenseList = monthExpenseList, totalLoanPaid = totalLoanPaid , totalLoanLeft = totalLoanLeft,reminders = reminderList)

#Profile
@app.route('/profile',methods=['GET','POST'])
def presentProfile():
    pageType = "profile-overview"
    email=session["email"]
    profileEditSuccessful=None
    profileEditFailed=None
    wrongPassword=None
    noMatch=None
    passwordChangeSuccessful=None
    if request.method=="POST":
        if request.form["submit"]=="editProfile":
            name=request.form["name"]
            country=request.form["country"]
            phone=request.form["phone"]
            if database.updateUserData(email,name,country,phone):
                profileEditSuccessful="Saved Changes!!"
            else:
                profileEditFailed="Couldn't save changes!!"
            pageType="profile-edit"
        elif request.form["submit"]=="changePassword":
            password = request.form["password"]
            newpassword = request.form["newpassword"]
            renewpassword = request.form["renewpassword"]
            fetchedPassword = database.fetchPassword(session['email'])
            user = database.fetchUser(session['email'])
            if fetchedPassword != password:
                wrongPassword = "Wrong Password !!"
                pageType="profile-change-password"
            elif newpassword != renewpassword:
                noMatch = "Your new Password and Re-type Password don't match!! Enter Password Again..."
                pageType="profile-change-password"
            elif database.updatePassword(session['email'],newpassword):
                passwordChangeSuccessful = "Password Changed Successfully !!"
                pageType="profile-change-password"
                msg = Message('eXpenso Password Changed', recipients=[email])
                msg.body = 'Your Password has been Changed! Happy Managing!!'
                msg.html = """<h1>Your Password has been Changed! Happy Managing!!</h1>
                                <h3>Reply to us if its not you!!</h3>
                            """
                mail.send(msg)
            else:
                wrongPassword = "Couldn't Change Password !!"
                pageType="profile-change-password"
    user = database.fetchUser(email)
    savings = database.getDebitSavingsAmount(email)
    return render_template('profile.html', user = user,pageType=pageType,profileEditSuccessful = profileEditSuccessful,profileEditFailed = profileEditFailed,wrongPassword=wrongPassword,noMatch=noMatch,passwordChangeSuccessful=passwordChangeSuccessful,savings = savings)

#Expenses
@app.route('/expenses')
def presentExpenses():
    email=session['email']
    user = database.fetchUser(email)
    expenses = database.fetchExpensesPreview(email)
    savings = database.fetchSavingsSelectionList(email)
    creditExpenses = database.getCreditExpenseAmount(email)
    debitExpenses = database.getDebitExpenseAmount(email)
    expenses1=database.getExpensesThisYear(email)
    highestExpenses = database.getHighestExpenses(email)
    recentExpenses = database.getRecentExpenses(email)
    monthLabels=['January', 'February', 'March', 'April', 'May', 'June', 'July','August','September','October','November','December']
    monthExpenseList = [0]*12
    for expense in expenses1:
        monthExpenseList[int(expense["MONTH"])-1]=expense["AMOUNT"]

    return render_template('expenses.html',user = user, expenses = expenses, savings=savings, creditExpenses=creditExpenses, debitExpenses=debitExpenses,monthLabels=monthLabels,monthExpenseList=monthExpenseList,highestExpenses = highestExpenses,recentExpenses = recentExpenses)


@app.route('/addExpense',methods = ['GET','POST'])
def addExpense():
    email = session['email']
    date = request.form["expensedate"].split("-")
    expenseid=email+"".join(date)+str(randint(0,10000))+str(randint(0,10000))
    if database.createExpenseData(email,expenseid,date[0],date[1],date[2],request.form) and database.updateSavingsWithExpense(request.form):
        return redirect('/expenses')
    return redirect('/expenses')

@app.route('/expenseRecords',methods = ['GET','POST'])
def presentExpenseRecords():
    email = session['email']
    successMessage = None
    failureMessage = None
    if request.method=='POST':
        if request.form['submit']=='deleteExpense':
            if database.deleteExpenseData(request.form['expenseid']):
                successMessage = "Deleted SuccessFully"
            else:
                failureMessage = "Unable to delete the Expense!!"
        elif request.form['submit']=='getExpenseValues':
            expense = database.readExpenseData(request.form['expenseid'])
            return json.dumps(expense)
        elif request.form['submit']=='editExpense':
            date = request.form["expensedate"].split("-")
            if database.updateExpenseData(request.form,year=date[0],month=date[1],date=date[2]):
                successMessage="Edited Expense Successfully!!"
            else:
                failureMessage="Failed to Edit Expense!!"
        elif request.form['submit']=='addExpense':
            email = session['email']
            date = request.form["expensedate"].split("-")
            expenseid=email+"".join(date)+str(randint(0,10000))+str(randint(0,10000))
            if database.createExpenseData(email,expenseid,date[0],date[1],date[2],request.form):
                successMessage = "Added Expense Successfully"
            else:
                failureMessage = "Could Not Add Expense!!"
    user = database.fetchUser(email)
    expenses = database.fetchExpenses(email)
    savings = database.fetchSavingsSelectionList(email)   
    return render_template('expenseRecords.html',user = user, expenses = expenses,savings=savings,successMessage = successMessage, failureMessage=failureMessage)

@app.route('/expenseAnalysis')
def presentExpenseAnalysis():
    email=session['email']
    user=database.fetchUser(email)
    expenses= database.getExpensesThisMonth(email)
    dayLabels=[str(i) for i in range(1,32)]
    dayExpenseList=[0]*31
    for expense in expenses:
        dayExpenseList[int(expense["DATE"])-1]=expense["AMOUNT"]
    expenses=database.getExpensesThisYear(email)
    monthLabels=['January', 'February', 'March', 'April', 'May', 'June', 'July','August','September','October','November','December']
    monthExpenseList = [0]*12
    for expense in expenses:
        monthExpenseList[int(expense["MONTH"])-1]=expense["AMOUNT"]
    
    expenses=database.getExpensesAllYears(email)
    yearLabels=[]
    yearExpenseList = []
    for expense in expenses:
        yearLabels.append(expense["YEAR"])
        yearExpenseList.append(expense["AMOUNT"])
    yearLabels=yearLabels
    return render_template('expenseAnalysis.html',filter=filter,user=user,dayLabels=dayLabels,dayExpenseList=dayExpenseList,monthLabels=monthLabels,monthExpenseList=monthExpenseList,yearLabels=yearLabels,yearExpenseList=yearExpenseList)

#Savings
@app.route('/Savings')
def presentSavings():
    email=session['email']
    user=database.fetchUser(email)
    creditsavings = database.getCreditSavingsAmount(email)
    debitsavings = database.getDebitSavingsAmount(email)
    recentsavings = database.getRecentSavings(email)
    highestsavings = database.getHighestSavings(email)
    debitSavingsList =[]
    debitLabels = []
    debitList = database.fetchSavingsWithType(email,'debit')
    for debit in debitList:
        debitLabels.append(debit["SAVINGSNAME"])
        debitSavingsList.append(debit["AMOUNT"])
    return render_template('savings.html',user=user,creditsavings = creditsavings, debitsavings = debitsavings, recentsavings = recentsavings, highestsavings = highestsavings, debitLabels = debitLabels ,debitSavingsList = debitSavingsList,)

@app.route('/addSavings', methods = ['POST','GET'])
def addSavings():
    email = session['email']
    if request.method == "POST":
        savingsid=email+str(randint(0,10000))+str(randint(0,10000))
        if database.createSavingsData(email,savingsid,request.form,):
            return redirect('/Savings')
    return redirect('/Savings')

@app.route('/SavingsRecords',methods = ['GET','POST'])
def presentSavingsRecords():
    email = session['email']
    successMessage = None
    failureMessage = None
    if request.method=='POST':
        if request.form['submit']=='deleteSaving':
            if database.deleteSavingsData(request.form['savingsid']):
                successMessage = "Deleted SuccessFully"
            else:
                failureMessage = "Unable to delete the Saving!!"
        elif request.form['submit']=='getSavingsValues':
            saving = database.readSavingsData(request.form['savingsid'])
            return json.dumps(saving)
        elif request.form['submit']=='editsavings':
            if database.updateSavingsData(request.form):
                successMessage="Edited Saving Successfully!!"
            else:
                failureMessage="Failed to Saving Expense!!"
        elif request.form['submit']=='addSaving':
            savingsid=email+str(randint(0,10000))+str(randint(0,10000))
            if database.createSavingsData(email,savingsid,request.form,):
                successMessage = "Added Saving Successfully"
            else:
                failureMessage = "Could Not Add Saving!!"
    user = database.fetchUser(email)
    creditSavings = database.fetchSavingsWithType(email,'credit')
    debitSavings = database.fetchSavingsWithType(email,'debit')
    return render_template('savingsRecords.html',user = user,creditSavings = creditSavings, debitSavings = debitSavings,successMessage = successMessage, failureMessage=failureMessage)


@app.route('/SavingsAnalysis')
def presentSavingsAnalysis():
    email=session['email']
    user=database.fetchUser(email)
    debitList = database.fetchSavingsWithType(email,'debit')
    creditList = database.fetchSavingsWithType(email,'credit')
    debitSavingsList =[]
    creditSavingsList =[]
    debitLabels = []
    creditLabels = []
    for debit in debitList:
        debitLabels.append(debit["SAVINGSNAME"])
        debitSavingsList.append(debit["AMOUNT"])
    for credit in creditList:
        creditLabels.append(credit["SAVINGSNAME"])
        creditSavingsList.append(credit["AMOUNT"])
    return render_template('savingsAnalysis.html',user=user, debitLabels = debitLabels ,debitSavingsList = debitSavingsList, creditLabels = creditLabels, creditSavingsList = creditSavingsList)


#reminders
@app.route('/Reminders', methods = ['POST','GET'])
def presentReminders():
    email=session['email']
    if request.method == "POST":
        if request.form['submit']=='addReminder':
            reminderid = email+"reminder"+str(randint(0,1000000))
            year,month,date=request.form["reminderdate"].split("-")
            database.createReminder(email,reminderid,date,month,year,request.form)
            date_time = datetime(int(year), int(month), int(date), 6, 0, 0)
            print("Given Date:",date_time)
            timestamp = mktime(date_time.timetuple())
            msg = Message('eXpenso Reminder', recipients=[email])
            msg.send_at = timestamp
            msg.date = timestamp
            print(msg.send_at, msg.date)
            msg.body = 'Reminder!!'
            msg.html = """<h1>%s</h1>
                            <h3>%s</h3>
                        """%(request.form["remindername"],request.form["reminderdescription"])
            mail.send(msg)
        elif request.form['submit']=='editReminder':
            year,month,date=request.form["reminderdate"].split("-")
            database.updateReminder(date,month,year,request.form)
        elif request.form['submit']=='getReminderValues':
            reminder = database.getReminder(request.form['reminderid'])
            return json.dumps(reminder)
        elif request.form['submit']=='deleteReminder':
            database.deleteReminder(request.form["reminderid"])

    user=database.fetchUser(email)
    reminders = database.readReminders(email)
    return render_template('reminders.html',user=user,reminders = reminders)

@app.route('/LoanTracker', methods = ['GET','POST'])
def presentLoanTracker():
    email=session['email']
    if request.method == 'POST':
        if request.form["submit"]=="addLoan":
            loanid = email+"loan"+str(randint(0,10000))+str(randint(0,10000))
            totalAmount = round(float(request.form["amountborrowed"])+((float(request.form["amountborrowed"])*float(request.form["duration"])*float(request.form["interest"]))/100.0))
            amountLeft = totalAmount - float(request.form["amountpaid"])
            database.createLoanData(email,loanid,totalAmount,amountLeft,request.form)
        elif request.form["submit"]=="editLoan":
            totalAmount = round(float(request.form["amountborrowed"])+((float(request.form["amountborrowed"])*float(request.form["duration"])*float(request.form["interest"]))/100.0))
            amountLeft = totalAmount - float(request.form["amountpaid"])
            database.updateLoanData(totalAmount,amountLeft,request.form)
        elif request.form["submit"]=="deleteLoan":
            database.deleteLoanData(request.form["loanid"])
        elif request.form["submit"]=="getLoanValues":
            loan = database.getLoanData(request.form['loanid'])
            return json.dumps(loan)
    user=database.fetchUser(email)
    loans = database.readLoanData(email)
    totalLoanPaid = database.getTotalLoanPaid(email)
    totalLoanLeft = database.getTotalLoanLeft(email)
    return render_template('LoanTracker.html',user=user,loans=loans, totalLoanPaid = totalLoanPaid , totalLoanLeft = totalLoanLeft)

#Sample
@app.route('/sample')
def presentSample():
    user = database.fetchUser(session['email'])
    return render_template('sample.html',user=user)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)