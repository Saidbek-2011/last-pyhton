from flask import Flask, session, render_template, request, url_for, redirect
from functools import wraps
import sqlite3

app = Flask(__name__)
app.secret_key = 'sirli_kalit' #session uchun

#data basega ulanish
def ulanish():
    return sqlite3.connect('users.db')

# decorator
def login_kerak(f):
    @wraps(f)
    def dekarator(*args, **kwargs):
        if "foydalanuvchi" not in session:
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return dekarator

@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        ism = request.form['ism']
        parol = request.form['parol']
        con = ulanish()
        kursor = con.cursor()
        kursor.execute("SELECT * FROM users WHERE ism = ? AND parol = ?", (ism, parol))
        user = kursor.fetchone()
        con.close()
        print(user)
        if user:
            session['foydalanuvchi'] = ism
            return redirect(url_for("bosh_sahifa"))
        return render_template('login.html', xabar="Manimcha san hammani aldading🫵")
    return render_template("login.html")

@app.route('/logout')
def logout():
    session.pop("foydalanuvchi", None)
    return redirect(url_for('login'))


#baseni tayorlash
@app.route('/init')
def init_db():
    con = ulanish()
    kursor = con.cursor()
    kursor.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, ism TEXT NOT NULL, parol TEXT NOT NULL)")
    kursor.execute("CREATE TABLE IF NOT EXISTS talabalar (id INTEGER PRIMARY KEY AUTOINCREMENT, ism TEXT NOT NULL, sinf TEXT, ball REAL)")
    kursor.execute("INSERT OR IGNORE INTO users (ism, parol) VALUES ('admin', 'admin77')")
    con.commit()
    con.close()
    return "Tizim Va Baza Tayyor"

@app.route('/')
@login_kerak
def bosh_sahifa():
    return render_template("index.html")

@app.route('/contact')
@login_kerak
def contact():
    return render_template("contact.html")





if __name__ == "__main":
    app.run(debug=True)

