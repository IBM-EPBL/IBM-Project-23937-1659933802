import sqlite3
conn = sqlite3.connect('User_Database.db')
print("Opened database successfully")
conn.execute('create table users(name text, email text, phone text, password text)')
print("Table created successfully")
conn.close()