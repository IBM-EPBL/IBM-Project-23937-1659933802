import credentials
import ibm_db
import ibm_boto3
from ibm_botocore.client import Config, ClientError
from datetime import *
from models import *

conn = ibm_db.connect("DATABASE="+credentials.DB2_DATABASE_NAME+";HOSTNAME="+credentials.DB2_HOST_NAME+";PORT="+credentials.DB2_PORT+";SECURITY=SSL;SSLServerCertificate=DigiCertGlobalRootCA.crt;UID="+credentials.DB2_UID+";PWD="+credentials.DB2_PWD+"",'','')

cos = ibm_boto3.resource("s3",
    ibm_api_key_id=credentials.COS_API_KEY_ID,
    ibm_service_instance_id=credentials.COS_INSTANCE_CRN,
    config=Config(signature_version="oauth"),
    endpoint_url=credentials.COS_ENDPOINT
)

class Database:
    def __init__(self) -> None:
        pass


    def fetchUser(self,email):
        sql = "SELECT email,name,phone,country FROM user WHERE email=?"
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(stmt,1,email)
        ibm_db.execute(stmt)
        account = ibm_db.fetch_assoc(stmt)
        if account:
            user = User(account["EMAIL"],account["NAME"],account["PHONE"],account["COUNTRY"])
            return user
        return None
    
    def fetchPassword(self,email):
        try:
            sql = "SELECT password FROM user WHERE email = ?"
            stmt = ibm_db.prepare(conn, sql)
            ibm_db.bind_param(stmt,1,email)
            ibm_db.execute(stmt)
            account = ibm_db.fetch_assoc(stmt)
            if account:
                return account["PASSWORD"]
            else:
                return False
        except:
            return False

    def insertSignUpUserData(self,email,password,name):
        try:
            insert_sql = "INSERT INTO user(email,password,name) VALUES (?,?,?)"
            prep_stmt = ibm_db.prepare(conn, insert_sql)
            ibm_db.bind_param(prep_stmt, 1, email)
            ibm_db.bind_param(prep_stmt, 2, password)
            ibm_db.bind_param(prep_stmt, 3, name)
            ibm_db.execute(prep_stmt)
        except:
            print("error")
            return False
        return True 

    def updateUserData(self,email,name,country,phone):
        try:
            sql = "update user set name = ? , country = ?, phone = ? where email = ?;"
            stmt = ibm_db.prepare(conn, sql)
            ibm_db.bind_param(stmt,1,name)
            ibm_db.bind_param(stmt,2,country)
            ibm_db.bind_param(stmt,3,phone)
            ibm_db.bind_param(stmt,4,email)
            ibm_db.execute(stmt)
        except:
            return False 
        return True

    def updatePassword(self,email,password):
        try:
            sql = "update user set password = ? where email = ?;"
            stmt = ibm_db.prepare(conn, sql)
            ibm_db.bind_param(stmt,1,password)
            ibm_db.bind_param(stmt,2,email)
            ibm_db.execute(stmt)
        except:
            return False 
        return True

    def fetchExpensesPreview(self,email,limit=10):
        sql ="SELECT expensename,date,month,year,expenses.description,savingsname,savingstype,expenses.amount FROM expenses join savings on expenses.savingsid=savings.savingsid WHERE expenses.email=? order by expenseid desc limit ?;"
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(stmt,1,email)
        ibm_db.bind_param(stmt,2,limit)
        ibm_db.execute(stmt)
        expense = ibm_db.fetch_both(stmt)
        expenseList = []
        while expense != False:
            expenseList.append(expense)
            expense = ibm_db.fetch_both(stmt)
        return expenseList
    
    def fetchExpenses(self,email):
        sql ="SELECT expenseid, expensename,date,month,year,expenses.description,expenses.amount,expenses.savingsid,savings.savingsname,savings.savingstype FROM expenses join savings on expenses.savingsid=savings.savingsid WHERE expenses.email=? order by expenseid desc;"
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(stmt,1,email)
        ibm_db.execute(stmt)
        expense = ibm_db.fetch_both(stmt)
        expenseList = []
        while expense != False:
            expenseList.append(expense)
            expense = ibm_db.fetch_both(stmt)
        return expenseList
    
    def fetchSavingsSelectionList(self,email):
        sql ="SELECT savingsid,savingsname,savingsType from savings where email = ?"
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(stmt,1,email)
        ibm_db.execute(stmt)
        saving = ibm_db.fetch_both(stmt)
        savingsList = []
        while saving != False:
            savingsList.append(saving)
            saving = ibm_db.fetch_both(stmt)
        return savingsList

    def getTotalExpenseAmount(self,email):
        today = date.today()
        sql = "SELECT SUM(amount) as TOTAL from expenses where email = ? and year = ?"
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(stmt,1,email)
        ibm_db.bind_param(stmt,2,today.year)
        ibm_db.execute(stmt)
        value = ibm_db.fetch_assoc(stmt)
        return value["TOTAL"]

    # def getTotalSavingsAmount(self,email):
    #     sql = "SELECT SUM(amount) as TOTAL from savings where email = ? and savingstype = 'credit'"
    #     stmt = ibm_db.prepare(conn, sql)
    #     ibm_db.bind_param(stmt,1,email)
    #     ibm_db.execute(stmt)
    #     value = ibm_db.fetch_assoc(stmt)
    #     return value["TOTAL"]

    def createExpenseData(self,email,expenseid,year,month,date,expense):
        try:
            insert_sql = "INSERT INTO EXPENSES VALUES(?,?,?,?,?,?,?,?,?);"
            prep_stmt = ibm_db.prepare(conn, insert_sql)
            ibm_db.bind_param(prep_stmt, 1, expenseid)
            ibm_db.bind_param(prep_stmt, 2, date)
            ibm_db.bind_param(prep_stmt, 3, month)
            ibm_db.bind_param(prep_stmt, 4, year)
            ibm_db.bind_param(prep_stmt, 5, expense["expensename"])
            ibm_db.bind_param(prep_stmt, 6, expense["expensedescription"])
            ibm_db.bind_param(prep_stmt, 7, expense["savings"])
            ibm_db.bind_param(prep_stmt, 8, email)
            ibm_db.bind_param(prep_stmt, 9, expense["expenseamount"])
            ibm_db.execute(prep_stmt)
        except:
            print("error")
            return False
        return True
        
    def readExpenseData(self,expenseid):
        sql = "SELECT * from expenses where expenseid = ?"
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(stmt,1,expenseid)
        ibm_db.execute(stmt)
        expense = ibm_db.fetch_assoc(stmt)
        return expense

    def updateExpenseData(self,expense,year,month,date):
        try:
            sql = "update expenses set date =?,month=?,year=?,expensename=?,description=?,savingsid=?,amount=? where expenseid = ?;"
            prep_stmt = ibm_db.prepare(conn, sql)
            ibm_db.bind_param(prep_stmt, 1, date)
            ibm_db.bind_param(prep_stmt, 2, month)
            ibm_db.bind_param(prep_stmt, 3, year)
            ibm_db.bind_param(prep_stmt, 4, expense["expensename"])
            ibm_db.bind_param(prep_stmt, 5, expense["expensedescription"])
            ibm_db.bind_param(prep_stmt, 6, expense["savings"])
            ibm_db.bind_param(prep_stmt, 7, expense["expenseamount"])
            ibm_db.bind_param(prep_stmt, 8, expense["expenseid"])
            ibm_db.execute(prep_stmt)
        except:
            return False 
        return True

    def deleteExpenseData(self,expenseid):
        try:
            sql = "delete from expenses where expenseid = ?;"
            stmt = ibm_db.prepare(conn, sql)
            ibm_db.bind_param(stmt,1,expenseid)
            ibm_db.execute(stmt)
        except:
            return False 
        return True
    
    def getExpensesThisMonth(self,email):
        year = date.today().year
        month = date.today().month
        sql ="SELECT date,SUM(amount) as amount from expenses where email=? and year=? and month=? group by date;"
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(stmt,1,email)
        ibm_db.bind_param(stmt,2,year)
        ibm_db.bind_param(stmt,3,month)
        ibm_db.execute(stmt)
        expense = ibm_db.fetch_both(stmt)
        expensesList = []
        while expense != False:
            expensesList.append(expense)
            expense = ibm_db.fetch_both(stmt)
        return expensesList
    def getRecentExpenses(self, email, limit = 5):
        sql ="SELECT expensename,date,month,year,expenses.description,expenses.amount,savingsname,savingstype from expenses join savings on expenses.savingsid=savings.savingsid where expenses.email = ? order by year desc,month desc,date desc limit ?;"
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(stmt,1,email)
        ibm_db.bind_param(stmt,2,limit)
        ibm_db.execute(stmt)
        expense = ibm_db.fetch_both(stmt)
        expensesList = []
        while expense != False:
            expensesList.append(expense)
            expense = ibm_db.fetch_both(stmt)
        return expensesList

    def getHighestExpenses(self, email, limit = 5):
        sql ="SELECT expensename,date,month,year,expenses.description,expenses.amount,savingsname,savingstype from expenses join savings on expenses.savingsid=savings.savingsid where expenses.email = ? order by expenses.amount desc limit ?;"
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(stmt,1,email)
        ibm_db.bind_param(stmt,2,limit)
        ibm_db.execute(stmt)
        expense = ibm_db.fetch_both(stmt)
        expensesList = []
        while expense != False:
            expensesList.append(expense)
            expense = ibm_db.fetch_both(stmt)
        return expensesList
    
    
    def getExpensesThisYear(self,email):
        year = date.today().year
        sql ="SELECT month,SUM(amount) as amount from expenses where email=? and year=? group by month;"
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(stmt,1,email)
        ibm_db.bind_param(stmt,2,year)
        ibm_db.execute(stmt)
        expense = ibm_db.fetch_both(stmt)
        expensesList = []
        while expense != False:
            expensesList.append(expense)
            expense = ibm_db.fetch_both(stmt)
        return expensesList

    def getExpensesAllYears(self,email):
        sql ="SELECT year,SUM(amount) as amount from expenses where email=? group by year order by year asc;"
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(stmt,1,email)
        ibm_db.execute(stmt)
        expense = ibm_db.fetch_both(stmt)
        expensesList = []
        while expense != False:
            expensesList.append(expense)
            expense = ibm_db.fetch_both(stmt)
        return expensesList

    def getCreditExpenseAmount(self,email):
        sql ="SELECT SUM(expenses.amount) as creditamount from expenses join savings on expenses.savingsid=savings.savingsid where expenses.email=? and savingstype='credit';"
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(stmt,1,email)
        ibm_db.execute(stmt)
        value = ibm_db.fetch_assoc(stmt)
        return value["CREDITAMOUNT"]
    
    
    def getDebitExpenseAmount(self,email):
        sql ="SELECT SUM(expenses.amount) as debitamount from expenses join savings on expenses.savingsid=savings.savingsid where expenses.email=? and savingstype='debit';"
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(stmt,1,email)
        ibm_db.execute(stmt)
        value = ibm_db.fetch_assoc(stmt)
        return value["DEBITAMOUNT"]

    def readSavingsData(self, savingsid):
        sql ="SELECT * from savings where savingsid = ?;"
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(stmt,1,savingsid)
        ibm_db.execute(stmt)
        savings = ibm_db.fetch_assoc(stmt)
        return savings

    def getRecentSavings(self, email, limit = 5):
        sql ="SELECT * from savings where email = ? and savingsid in (select savingsid from expenses where email=? order by year desc, month desc, date desc) limit ?;"
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(stmt,1,email)
        ibm_db.bind_param(stmt,2,email)
        ibm_db.bind_param(stmt,3,limit)
        ibm_db.execute(stmt)
        saving = ibm_db.fetch_both(stmt)
        savingsList = []
        while saving != False:
            savingsList.append(saving)
            saving = ibm_db.fetch_both(stmt)
        return savingsList

    def getHighestSavings(self, email, limit = 5):
        sql ="SELECT * from savings where email = ? order by amount desc limit ?;"
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(stmt,1,email)
        ibm_db.bind_param(stmt,2,limit)
        ibm_db.execute(stmt)
        saving = ibm_db.fetch_both(stmt)
        savingsList = []
        while saving != False:
            savingsList.append(saving)
            saving = ibm_db.fetch_both(stmt)
        return savingsList

    def getCreditSavingsAmount(self,email):
        sql ="SELECT SUM(amount) as creditamount from savings where email=? and savingstype='credit';"
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(stmt,1,email)
        ibm_db.execute(stmt)
        value = ibm_db.fetch_assoc(stmt)
        return value["CREDITAMOUNT"]
    
    def getDebitSavingsAmount(self,email):
        sql ="SELECT SUM(amount) as debitamount from savings where email=? and savingstype='debit';"
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(stmt,1,email)
        ibm_db.execute(stmt)
        value = ibm_db.fetch_assoc(stmt)
        return value["DEBITAMOUNT"]
    
    def getDebitExpenseAmount(self,email):
        sql ="SELECT SUM(expenses.amount) as debitamount from expenses join savings on expenses.savingsid=savings.savingsid where expenses.email=? and savingstype='debit';"
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(stmt,1,email)
        ibm_db.execute(stmt)
        value = ibm_db.fetch_assoc(stmt)
        return value["DEBITAMOUNT"]

    def updateSavingsWithExpense(self,form):
        try:
            savingsid = form["savings"]
            expenseamount = float(form["expenseamount"])
            sql ="SELECT savingstype,amount from savings where savingsid= ? "
            stmt = ibm_db.prepare(conn, sql)
            ibm_db.bind_param(stmt,1,savingsid)
            ibm_db.execute(stmt)
            data = ibm_db.fetch_assoc(stmt)
            savingsAmount = float(data["AMOUNT"])
            savingsType = data["SAVINGSTYPE"]
            if savingsType == "credit":
                savingsAmount+=expenseamount
            else:
                savingsAmount-=expenseamount
            sql = "update savings set amount = ? where savingsid = ?;"
            prep_stmt = ibm_db.prepare(conn, sql)
            ibm_db.bind_param(prep_stmt, 1, savingsAmount)
            ibm_db.bind_param(prep_stmt, 2, savingsid)
            ibm_db.execute(prep_stmt)
        except:
            print("error")
            return False 
        return True
        
    def updateSavingsWithIncome(self,form):
        try:
            savingsid = form["savings"]
            income = float(form["income"])
            sql ="SELECT savingstype,amount from savings where savingsid= ? "
            stmt = ibm_db.prepare(conn, sql)
            ibm_db.bind_param(stmt,1,savingsid)
            ibm_db.execute(stmt)
            data = ibm_db.fetch_assoc(stmt)
            savingsAmount = float(data["AMOUNT"])
            savingsType = data["SAVINGSTYPE"]
            if savingsType == "debit":
                savingsAmount+=income
            else:
                savingsAmount-=income
            sql = "update savings set amount = ? where savingsid = ?;"
            prep_stmt = ibm_db.prepare(conn, sql)
            ibm_db.bind_param(prep_stmt, 1, savingsAmount)
            ibm_db.bind_param(prep_stmt, 2, savingsid)
            ibm_db.execute(prep_stmt)
        except:
            print("error")
            return False 
        return True
    
    def getSavingsCount(self,email):
        sql = "SELECT COUNT(*) as COUNT from expenses where email = ? "
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(stmt,1,email)
        ibm_db.execute(stmt)
        value = ibm_db.fetch_assoc(stmt)
        return value["COUNT"]

    def fetchSavingsWithType(self,email, type):
        sql ="SELECT * from savings where email = ? and savingstype = ?"
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(stmt,1,email)
        ibm_db.bind_param(stmt,2,type)
        ibm_db.execute(stmt)
        saving = ibm_db.fetch_both(stmt)
        savingsList = []
        while saving != False:
            savingsList.append(saving)
            saving = ibm_db.fetch_both(stmt)
        return savingsList
        
    def createSavingsData(self,email,savingsid,saving):
        try:
            insert_sql = "INSERT INTO SAVINGS VALUES(?,?,?,?,?,?);"
            prep_stmt = ibm_db.prepare(conn, insert_sql)
            ibm_db.bind_param(prep_stmt, 1, savingsid)
            ibm_db.bind_param(prep_stmt, 2, saving["savingsname"])
            ibm_db.bind_param(prep_stmt, 3, saving["savingstype"])
            ibm_db.bind_param(prep_stmt, 4, saving["savingsdescription"])
            ibm_db.bind_param(prep_stmt, 5, saving["savingsamount"])
            ibm_db.bind_param(prep_stmt, 6, email)
            ibm_db.execute(prep_stmt)
        except:
            print("error")
            return False
        return True
    
    def deleteSavingsData(self,savingsid):
        try:
            sql1 = "delete from expenses where savingsid = ?;"
            stmt1 = ibm_db.prepare(conn, sql1)
            ibm_db.bind_param(stmt1,1,savingsid)
            ibm_db.execute(stmt1)

            sql = "delete from savings where savingsid = ?;"
            stmt = ibm_db.prepare(conn, sql)
            ibm_db.bind_param(stmt,1,savingsid)
            ibm_db.execute(stmt)
        except:
            return False 
        return True
    
    def updateSavingsData(self,saving):
        try:
            sql = "update savings set savingsname=?,description=?,savingstype=?,amount=? where savingsid = ?;"
            prep_stmt = ibm_db.prepare(conn, sql)
            ibm_db.bind_param(prep_stmt, 1, saving["savingsname"])
            ibm_db.bind_param(prep_stmt, 2, saving["savingsdescription"])
            ibm_db.bind_param(prep_stmt, 3, saving["savingstype"])
            ibm_db.bind_param(prep_stmt, 4, float(saving["savingsamount"]))
            ibm_db.bind_param(prep_stmt, 5, saving["savingsid"])
            ibm_db.execute(prep_stmt)
        except:
            return False 
        return True

    def updateSavingsAmount(self,savingsid,savingsType,amount):
        try:
            sql1 = "SELECT amount as amount from savings where savingsid = ? "
            stmt = ibm_db.prepare(conn, sql1)
            ibm_db.bind_param(stmt,1,savingsid)
            ibm_db.execute(stmt)
            value = ibm_db.fetch_assoc(stmt)
            savingsamount = float(value["AMOUNT"])
        except:
            print("No Savings")
        if savingsType=="credit":
            savingsamount += amount
        else:
            savingsamount -= amount
        try:
            sql = "update savings set amount=? where savingsid = ?;"
            prep_stmt = ibm_db.prepare(conn, sql)
            ibm_db.bind_param(prep_stmt, 1, savingsamount)
            ibm_db.bind_param(prep_stmt, 2, savingsid)
            ibm_db.execute(prep_stmt)
        except:
            return False 
        return True

    def createLoanData(self,email,loanid,totalamount,amountLeft,loan):
        try:
            insert_sql = "INSERT INTO LOANS VALUES(?,?,?,?,?,?,?,?,?,?,?);"
            prep_stmt = ibm_db.prepare(conn, insert_sql)
            ibm_db.bind_param(prep_stmt, 1, loanid)
            ibm_db.bind_param(prep_stmt, 2, loan["loanname"])
            ibm_db.bind_param(prep_stmt, 3, loan["loanpayee"])
            ibm_db.bind_param(prep_stmt, 4, loan["loandate"])
            ibm_db.bind_param(prep_stmt, 5, loan["amountborrowed"])
            ibm_db.bind_param(prep_stmt, 6, loan["duration"])
            ibm_db.bind_param(prep_stmt, 7, loan["interest"])
            ibm_db.bind_param(prep_stmt, 8, totalamount)
            ibm_db.bind_param(prep_stmt, 9, loan["amountpaid"])
            ibm_db.bind_param(prep_stmt, 10, amountLeft)
            ibm_db.bind_param(prep_stmt, 11, email)
            ibm_db.execute(prep_stmt)
        except:
            print("error")
            return False
        return True

    def readLoanData(self,email):
        sql = "SELECT * from loans where email = ?"
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(stmt,1,email)
        ibm_db.execute(stmt)
        loan = ibm_db.fetch_both(stmt)
        loans = []
        while loan != False:
            loans.append(loan)
            loan = ibm_db.fetch_both(stmt)
        return loans
    
    def getLoanData(self,loanid):
        print(loanid)
        sql = "SELECT * from loans where loanid = ?"
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(stmt,1,loanid)
        ibm_db.execute(stmt)
        loan = ibm_db.fetch_assoc(stmt)
        return loan
    
    def updateLoanData(self,totalamount,amountLeft,loan):
        try:
            sql = "update loans set loanname=?,payee=?,date=?,duration=?,interest=?,amountborrowed=?,totalamount=?,amountpaid=?,amountleft=? where loanid = ?;"
            prep_stmt = ibm_db.prepare(conn, sql)
            ibm_db.bind_param(prep_stmt, 1, loan["loanname"])
            ibm_db.bind_param(prep_stmt, 2, loan["loanpayee"])
            ibm_db.bind_param(prep_stmt, 3, loan["loandate"])
            ibm_db.bind_param(prep_stmt, 4, loan["duration"])
            ibm_db.bind_param(prep_stmt, 5, loan["interest"])
            ibm_db.bind_param(prep_stmt, 6, loan["amountborrowed"])
            ibm_db.bind_param(prep_stmt, 7, totalamount)
            ibm_db.bind_param(prep_stmt, 8, loan["amountpaid"])
            ibm_db.bind_param(prep_stmt, 9, amountLeft)
            ibm_db.bind_param(prep_stmt, 10, loan["loanid"])

            ibm_db.execute(prep_stmt)
        except:
            print("error")
            return False 
        return True

    def deleteLoanData(self,loanid):
        try:
            sql = "delete from loans where loanid = ?;"
            stmt = ibm_db.prepare(conn, sql)
            ibm_db.bind_param(stmt,1,loanid)
            ibm_db.execute(stmt)
        except:
            return False 
        return True
    
    def getTotalLoanPaid(self,email):
        sql = "SELECT SUM(amountpaid) as TOTAL from loans where email = ?"
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(stmt,1,email)
        ibm_db.execute(stmt)
        value = ibm_db.fetch_assoc(stmt)
        return value["TOTAL"]
    
    def getTotalLoanLeft(self,email):
        sql = "SELECT SUM(amountleft) as TOTAL from loans where email = ?"
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(stmt,1,email)
        ibm_db.execute(stmt)
        value = ibm_db.fetch_assoc(stmt)
        return value["TOTAL"]
    
    def createReminder(self,email,reminderid,date,month,year,reminder):
        try:
            insert_sql = "INSERT INTO reminders VALUES(?,?,?,?,?,?,?,?);"
            prep_stmt = ibm_db.prepare(conn, insert_sql)
            ibm_db.bind_param(prep_stmt, 1, reminderid)
            ibm_db.bind_param(prep_stmt, 2, date)
            ibm_db.bind_param(prep_stmt, 3, month)
            ibm_db.bind_param(prep_stmt, 4, year)
            ibm_db.bind_param(prep_stmt, 5, reminder["remindername"])
            ibm_db.bind_param(prep_stmt, 6, reminder["reminderdescription"])
            ibm_db.bind_param(prep_stmt, 7, email)
            ibm_db.bind_param(prep_stmt, 8, reminder["frequency"])
            ibm_db.execute(prep_stmt)
        except:
            print("error")
            return False
        return True

    def readReminders(self,email):
        sql = "SELECT * from reminders where email = ?"
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(stmt,1,email)
        ibm_db.execute(stmt)
        reminder = ibm_db.fetch_both(stmt)
        reminders = []
        while reminder != False:
            reminders.append(reminder)
            reminder = ibm_db.fetch_both(stmt)
        return reminders
    
    def readRemindersWithLimit(self,email,limit=10):
        sql = "SELECT * from reminders where email = ? order by year asc, month asc, date asc limit ?"
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(stmt,1,email)
        ibm_db.bind_param(stmt,2,limit)
        ibm_db.execute(stmt)
        reminder = ibm_db.fetch_both(stmt)
        reminders = []
        while reminder != False:
            reminders.append(reminder)
            reminder = ibm_db.fetch_both(stmt)
        return reminders

    def getReminder(self,reminderid):
        sql = "SELECT * from reminders where reminderid = ?"
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(stmt,1,reminderid)
        ibm_db.execute(stmt)
        loan = ibm_db.fetch_assoc(stmt)
        return loan

    def updateReminder(self,date,month,year,reminder):
        try:
            sql = "update reminders set date=?,month=?,year=?,remindername=?,description=?,frequency=? where reminderid = ?;"
            prep_stmt = ibm_db.prepare(conn, sql)
            ibm_db.bind_param(prep_stmt, 1, date)
            ibm_db.bind_param(prep_stmt, 2, month)
            ibm_db.bind_param(prep_stmt, 3, year)
            ibm_db.bind_param(prep_stmt, 4, reminder["remindername"])
            ibm_db.bind_param(prep_stmt, 5, reminder["reminderdescription"])
            ibm_db.bind_param(prep_stmt, 6, reminder["frequency"])
            ibm_db.bind_param(prep_stmt, 10, reminder["reminderid"])
            ibm_db.execute(prep_stmt)
        except:
            print("error")
            return False 
        return True

    def deleteReminder(self, reminderid):
        try:
            sql = "delete from reminders where reminderid = ?;"
            stmt = ibm_db.prepare(conn, sql)
            ibm_db.bind_param(stmt,1,reminderid)
            ibm_db.execute(stmt)
        except:
            return False 
        return True