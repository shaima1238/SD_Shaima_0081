from flask import Flask, render_template, request, redirect, session
import sqlite3

app = Flask(__name__)
app.secret_key = "payroll123"

# ---------------- DATABASE ---------------- #

def init_db():

    conn = sqlite3.connect("payroll.db")
    cur = conn.cursor()

    cur.execute("""
CREATE TABLE IF NOT EXISTS employee(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    department TEXT,
    email TEXT,
    phone TEXT,
    joining_date TEXT,
    basic REAL,
    hra REAL,
    da REAL,
    deduction REAL,
    absent_days INTEGER,
    net_salary REAL
)
""")

    conn.commit()
    conn.close()

init_db()

# ---------------- LOGIN ---------------- #

@app.route("/", methods=["GET","POST"])
def login():

    if request.method=="POST":

        username=request.form["username"]
        password=request.form["password"]

        if username=="admin" and password=="admin123":

            session["user"]=username

            return redirect("/dashboard")

        else:
            return render_template("login.html",
                                   error="Wrong Username or Password")

    return render_template("login.html")

# ---------------- DASHBOARD ---------------- #

@app.route("/dashboard")
def dashboard():

    if "user" not in session:
        return redirect("/")

    conn=sqlite3.connect("payroll.db")
    cur=conn.cursor()

    cur.execute("SELECT * FROM employee")

    employees=cur.fetchall()

    conn.close()

    return render_template("dashboard.html",
                           employees=employees)

# ---------------- ADD EMPLOYEE ---------------- #

# ---------------- ADD EMPLOYEE ---------------- #

@app.route("/add", methods=["GET", "POST"])
def add():

    if "user" not in session:
        return redirect("/")

    if request.method == "POST":

        # Get form data
        name = request.form["name"]
        email = request.form["email"]
        phone = request.form["phone"]
        department = request.form["department"]
        joining = request.form["joining"]

        basic = float(request.form["basic"])
        absent_days = int(request.form["absent_days"])

        # Salary Calculation
        hra = basic * 0.20
        da = basic * 0.10

        # Other deduction (5%)
        other_deduction = basic * 0.05

        # Salary deduction for absent days
        per_day_salary = basic / 30
        absent_deduction = absent_days * per_day_salary

        # Total deduction
        deduction = other_deduction + absent_deduction

        # Net salary
        net_salary = basic + hra + da - deduction

        conn = sqlite3.connect("payroll.db")
        cur = conn.cursor()

        cur.execute("""
        INSERT INTO employee
        (
            name,
            department,
            email,
            phone,
            joining_date,
            basic,
            hra,
            da,
            deduction,
            absent_days,
            net_salary
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            name,
            department,
            email,
            phone,
            joining,
            basic,
            hra,
            da,
            deduction,
            absent_days,
            net_salary
        ))

        conn.commit()
        conn.close()

        return redirect("/dashboard")

    return render_template("add.html")

# ---------------- DELETE ---------------- #

@app.route("/delete/<int:id>")
def delete(id):

    conn=sqlite3.connect("payroll.db")

    cur=conn.cursor()

    cur.execute("DELETE FROM employee WHERE id=?",(id,))

    conn.commit()

    conn.close()

    return redirect("/dashboard")

# ---------------- LOGOUT ---------------- #

@app.route("/logout")
def logout():

    session.clear()

    return redirect("/")

# ---------------- MAIN ---------------- #

if __name__=="__main__":

    app.run(debug=True)