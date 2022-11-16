from flask import *
from database import *
from models import *
from random import *

user = User("sample","sample","sample","sample")
database = Database()

app = Flask(__name__)
app.secret_key = "FlaskNotFoundError"

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
    totalExpenses = database.getExpensesTotal(email)
    totalSavings = database.getSavingsTotal(email)
    expenseFilter = "year"
    savingsFilter = "year"
    expenses = database.fetchExpensesPreview(email,5)
    monthExpenses=database.getExpensesThisYear(email)
    monthLabels=['January', 'February', 'March', 'April', 'May', 'June', 'July','August','September','October','November','December']
    monthExpenseList = [0]*12
    for expense in monthExpenses:
        monthExpenseList[int(expense["MONTH"])-1]=expense["AMOUNT"]
    return render_template('home.html',user = user,expenseFilter = expenseFilter,totalExpenses = totalExpenses, savingsFilter = savingsFilter, totalSavings = totalSavings, expenses = expenses, monthLabels = monthLabels, monthExpenseList = monthExpenseList)

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
            else:
                wrongPassword = "Couldn't Change Password !!"
                pageType="profile-change-password"
    user = database.fetchUser(email)
    return render_template('profile.html', user = user,pageType=pageType,profileEditSuccessful = profileEditSuccessful,profileEditFailed = profileEditFailed,wrongPassword=wrongPassword,noMatch=noMatch,passwordChangeSuccessful=passwordChangeSuccessful)

#Expenses
@app.route('/expenses')
def presentExpenses():
    email=session['email']
    user = database.fetchUser(email)
    expenses = database.fetchExpensesPreview(email)
    savings = database.fetchSavings(email)
    creditExpenses = database.getCreditExpenses(email)
    debitExpenses = database.getDebitExpenses(email)
    expenses1=database.getExpensesThisYear(email)
    monthLabels=['January', 'February', 'March', 'April', 'May', 'June', 'July','August','September','October','November','December']
    monthExpenseList = [0]*12
    for expense in expenses1:
        monthExpenseList[int(expense["MONTH"])-1]=expense["AMOUNT"]
    return render_template('expenses.html',user = user, expenses = expenses, savings=savings, creditExpenses=creditExpenses, debitExpenses=debitExpenses,monthLabels=monthLabels,monthExpenseList=monthExpenseList)


@app.route('/addExpense',methods = ['GET','POST'])
def addExpense():
    email = session['email']
    date = request.form["expensedate"].split("-")
    expenseid=email+"".join(date)+str(database.getTotalExpenseCountToday(email,date[0],date[1],date[2]))+str(randint(0,10000))
    if database.insertExpenseData(email,expenseid,date[0],date[1],date[2],request.form) and database.updateSavingsWithExpense(request.form):
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
            expense = database.getExpenseData(request.form['expenseid'])
            return json.dumps(expense)
        elif request.form['submit']=='editExpense':
            date = request.form["expensedate"].split("-")
            if database.editExpenseData(request.form,year=date[0],month=date[1],date=date[2]):
                successMessage="Edited Expense Successfully!!"
            else:
                failureMessage="Failed to Edit Expense!!"
        elif request.form['submit']=='addExpense':
            email = session['email']
            date = request.form["expensedate"].split("-")
            expenseid=email+"".join(date)+str(database.getTotalExpenseCountToday(email,date[0],date[1],date[2]))+str(randint(0,10000))
            if database.insertExpenseData(email,expenseid,date[0],date[1],date[2],request.form):
                successMessage = "Added Expense Successfully"
            else:
                failureMessage = "Could Not Add Expense!!"
    user = database.fetchUser(email)
    expenses = database.fetchExpenses(email)
    savings = database.fetchSavings(email)   
    return render_template('expenseRecords.html',user = user, expenses = expenses,savings=savings,successMessage = successMessage, failureMessage=failureMessage)

@app.route('/expenseAnalysis')
def presentExpenseAnalysis():
    email=session['email']
    user=database.fetchUser(email)
    expenses= database.getExpensesThisMonth(email)
    dayLabels=[str(i) for i in range(1,32)]
    print(dayLabels)
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
    return render_template('savings.html',user=user,creditsavings = creditsavings, debitsavings = debitsavings, recentsavings = recentsavings, highestsavings = highestsavings)

@app.route('/addSavings', methods = ['POST','GET'])
def addSavings():
    email = session['email']
    if request.method == "POST":
        savingsid=email+str(database.getTotalSavingsCount(email)+randint(0,10000)+randint(0,10000))
        if database.insertSavingsData(email,savingsid,request.form,):
            return redirect('/Savings')
    return redirect('/Savings')

@app.route('/SavingsRecords',methods = ['GET','POST'])
def presentSavingsRecords():
    email = session['email']
    successMessage = None
    failureMessage = None
    if request.method=='POST':
        if request.form['submit']=='deleteSaving':
            if database.deleteSavingData(request.form['savingsid']):
                successMessage = "Deleted SuccessFully"
            else:
                failureMessage = "Unable to delete the Saving!!"
        elif request.form['submit']=='getSavingsValues':
            saving = database.getSavings(request.form['savingsid'])
            return json.dumps(saving)
        elif request.form['submit']=='editsavings':
            if database.editSavingsData(request.form):
                successMessage="Edited Saving Successfully!!"
            else:
                failureMessage="Failed to Saving Expense!!"
        elif request.form['submit']=='addSaving':
            savingsid=email+str(database.getTotalSavingsCount(email))+str(randint(0,1000))+str(randint(0,10000))
            if database.insertSavingsData(email,savingsid,request.form,):
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
    return render_template('savingsAnalysis.html',user=user)


#reminders
@app.route('/Reminders')
def presentReminders():
    email=session['email']
    user=database.fetchUser(email)
    return render_template('reminders.html',user=user)

@app.route('/RecurringReminders')
def presentRecurringReminders():
    email=session['email']
    user=database.fetchUser(email)
    return render_template('recurringReminders.html',user=user)

@app.route('/LoanTracker')
def presentLoanTracker():
    email=session['email']
    user=database.fetchUser(email)
    return render_template('LoanTracker.html',user=user)

@app.route('/addLoan')
def addLoan():
    email = session['email']
    if request.method == "POST":
        date = request.form["expensedate"].split("-")
        expenseid=email+"".join(date)+str(database.getTotalExpenseCountToday(email,date[0],date[1],date[2])+1)
        if database.insertExpenseData(email,expenseid,date[0],date[1],date[2],request.form) and database.updateSavingsWithExpense(request.form):
            return redirect('/expenses')
        return redirect('/expenses')

#Sample
@app.route('/sample')
def presentSample():
    user = database.fetchUser(session['email'])
    return render_template('sample.html',user=user)