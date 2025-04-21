from flask import Flask, session, render_template, request, url_for, redirect
from functools import wraps
import sqlite3

app = Flask(__name__)
app.secret_key = 'sirli_kalit'  # session uchun

# Databasega ulanish
def ulanish():
    return sqlite3.connect('users.db')

# Login talab qilinadigan sahifalar uchun decorator
def login_kerak(f):
    @wraps(f)
    def dekarator(*args, **kwargs):
        if "foydalanuvchi" not in session:
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return dekarator

# Foydalanuvchi ro'yxatdan o'tish
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        ism = request.form['ism']
        parol = request.form['parol']
        con = ulanish()
        kursor = con.cursor()

        # Avval foydalanuvchi bor-yo‘qligini tekshiramiz
        kursor.execute("SELECT * FROM users WHERE ism = ?", (ism,))
        mavjud = kursor.fetchone()
        if mavjud:
            con.close()
            return render_template("register.html", xabar="Bu foydalanuvchi allaqachon mavjud!")

        # Yangi foydalanuvchini qo‘shamiz
        kursor.execute("INSERT INTO users (ism, parol) VALUES (?, ?)", (ism, parol))
        con.commit()
        con.close()
        return redirect(url_for("login"))

    return render_template("register.html")

# Login sahifasi
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        ism = request.form['ism']
        parol = request.form['parol']
        con = ulanish()
        kursor = con.cursor()
        kursor.execute("SELECT * FROM users WHERE ism = ? AND parol = ?", (ism, parol))
        user = kursor.fetchone()
        con.close()
        if user:
            session['foydalanuvchi'] = ism
            return redirect(url_for("bosh_sahifa"))
        return render_template('login.html', xabar="Bu foydalanuvchi mavjud emas!")
    return render_template("login.html")

# Logout
@app.route('/logout')
def logout():
    session.pop("foydalanuvchi", None)
    return redirect(url_for('login'))

# Bosh sahifa
@app.route('/')
@login_kerak
def bosh_sahifa():
    return render_template("index.html")

# Qo'shimcha sahifa
@app.route('/create_messages_table')
def create_table():
    con = ulanish()
    kursor = con.cursor()
    kursor.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL,
            parol TEXT NOT NULL,
            xabar TEXT NOT NULL
        )
    ''')
    con.commit()
    con.close()
    return "Xabarlar jadvali yaratildi!"


# Contact sahifasi
@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        email = request.form['email']
        parol = request.form['parol']
        xabar = request.form['xabar']

        con = ulanish()
        kursor = con.cursor()
        kursor.execute("INSERT INTO messages (email, parol, xabar) VALUES (?, ?, ?)", (email, parol, xabar))
        con.commit()
        con.close()

        return "Xabaringiz muvaffaqiyatli yuborildi! ✅"

    return render_template('contact.html')

# Ma'lumotlar bazasini yaratish uchun
@app.route('/init')
def init_db():
    con = ulanish()
    kursor = con.cursor()

    # foydalanuvchilar uchun jadval
    kursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ism TEXT NOT NULL,
            parol TEXT NOT NULL
        )
    """)

    
    kursor.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL,
            parol TEXT NOT NULL,
            xabar TEXT NOT NULL
        )
    """)

    
    kursor.execute("INSERT OR IGNORE INTO users (ism, parol) VALUES ('Saidbek', '2011')")

    con.commit()
    con.close()
    return "Bazalar yaratildi ✅"


if __name__ == "__main__":
    app.run(debug=True)
