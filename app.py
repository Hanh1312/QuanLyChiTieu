import shutil
import os
from datetime import datetime
from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    session,
    flash
)

from database import *

app = Flask(__name__)
app.secret_key = "quanlychitieu_secret_key"


# =====================================
# LOGIN REQUIRED
# =====================================

def login_required():
    return "user" in session


# =====================================
# LOGIN
# =====================================

@app.route("/", methods=["GET", "POST"])
@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        user = check_login(username, password)
        print(user)
        if user:
            session["user"] = user["Username"]
            session["user_id"] = user["UserID"]
            return redirect(url_for("dashboard"))
        else:
            flash("Sai tài khoản hoặc mật khẩu")

    return render_template("login.html")


# =====================================
# LOGOUT
# =====================================

@app.route("/logout")
def logout():

    session.clear()

    return redirect(url_for("login"))


# =====================================
# DASHBOARD
# =====================================

@app.route("/dashboard")
def dashboard():

    if not login_required():
        return redirect(url_for("login"))

    income = get_total_income(session["user_id"])
    expense = get_total_expense(session["user_id"])
    debt_pay = get_total_debt_pay(session["user_id"])
    debt_receive = get_total_debt_receive(session["user_id"])
    saving_total = get_total_saving(session["user_id"])

    balance = income - expense
    warnings = get_due_debts(session["user_id"])
    return render_template(
        "index.html",
        income=income,
        expense=expense,
        balance=balance,
        debt_pay=debt_pay,
        debt_receive=debt_receive,
        saving_total=saving_total,
        warnings=warnings
    )


# =====================================
# TRANSACTIONS
# =====================================

@app.route("/transactions")
def transactions():

    if not login_required():
        return redirect(url_for("login"))

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT *
    FROM Transactions
    WHERE UserID=?
    ORDER BY TransactionDate DESC
    """,
    (
        session["user_id"],
    ))

    rows = cursor.fetchall()

    conn.close()

    return render_template(
        "transactions.html",
        transactions=rows
    )


# =====================================
# ADD TRANSACTION
# =====================================

@app.route("/add_transaction", methods=["POST"])
def add_transaction():

    if not login_required():
        return redirect(url_for("login"))

    date = request.form["date"]
    trans_type = request.form["type"]
    category = request.form["category"]
    amount = request.form["amount"]
    note = request.form["note"]

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO Transactions
        (
            UserID,
            TransactionDate,
            Type,
            Category,
            Amount,
            Note
        )
        VALUES
        (
            ?, ?, ?, ?, ?, ?
        )
    """,
    (
        session["user_id"],
        date,
        trans_type,
        category,
        amount,
        note
    ))

    conn.commit()
    conn.close()

    flash("Đã thêm giao dịch")

    return redirect(url_for("transactions"))


# =====================================
# DELETE TRANSACTION
# =====================================

@app.route("/delete_transaction/<int:id>")
def delete_transaction(id):

    if not login_required():
        return redirect(url_for("login"))

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    DELETE FROM Transactions
    WHERE TransactionID = ?
    AND UserID=?
    """, (id,))

    conn.commit()
    conn.close()

    flash("Đã xóa giao dịch")

    return redirect(url_for("transactions"))

@app.route(
    "/edit_transaction/<int:id>",
    methods=["GET","POST"]
)
def edit_transaction(id):

    conn = get_connection()
    cursor = conn.cursor()

    if request.method == "POST":

        cursor.execute("""

        UPDATE Transactions

        SET
            
            Type=?,
            Category=?,
            Amount=?,
            Note=?

        WHERE TransactionID=?

        """,
        (
            request.form["type"],
            request.form["category"],
            request.form["amount"],
            request.form["note"],
            id
        ))

        conn.commit()
        conn.close()
        return redirect(
            url_for(
                "transactions"
            )
        )

    cursor.execute("""
    SELECT *
    FROM Transactions
    WHERE TransactionID=?
    AND UserID=?
    """,
    (
        id,
        session["user_id"]
    ))

    transaction = cursor.fetchone()
    conn.close()
    return render_template(
        "edit_transaction.html",
        transaction=transaction
    )
# =====================================
# DEBT PAY
# =====================================

@app.route("/debt-pay")
def debt_pay():

    if not login_required():
        return redirect(url_for("login"))

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM DebtPay
        WHERE UserID=?
        ORDER BY DueDate
    """,
    (
    session["user_id"],
    ))

    rows = cursor.fetchall()

    conn.close()

    total_debt = sum(
        debt["Amount"]
        for debt in rows
        if debt["Status"] == "Unpaid"
    )

    return render_template(
        "debt_pay.html",
        debts=rows,
        total_debt=total_debt
    )


# =====================================
# ADD DEBT PAY
# =====================================

@app.route("/add_debt_pay", methods=["POST"])
def add_debt_pay():

    if not login_required():
        return redirect(url_for("login"))

    person = request.form["person"]
    amount = request.form["amount"]
    due_date = request.form["due_date"]
    note = request.form["note"]

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO DebtPay
        (
            UserID,
            PersonName,
            Amount,
            DueDate,
            Note
        )
        VALUES
        (
            ?, ?, ?, ?, ?
        )
    """,
    (
        session["user_id"],
        person,
        amount,
        due_date,
        note
    ))

    conn.commit()
    conn.close()

    flash("Đã thêm khoản nợ phải trả")

    return redirect(url_for("debt_pay"))

@app.route("/delete_debt_pay/<int:id>")
def delete_debt_pay(id):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM DebtPay WHERE DebtID=?",
        (id,)
    )

    conn.commit()
    conn.close()

    return redirect(url_for("debt_pay"))
# =====================================
# PAID DEBT
# =====================================

@app.route("/paid_debt/<int:id>")
def paid_debt(id):

    if not login_required():
        return redirect(url_for("login"))

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE DebtPay
        SET Status='Paid'
        WHERE DebtID=?
    """,(id,))

    conn.commit()
    conn.close()

    flash("Đã cập nhật trạng thái")

    return redirect(url_for("debt_pay"))

@app.route(
    "/edit_debt_pay/<int:id>",
    methods=["GET","POST"]
)
def edit_debt_pay(id):

    conn = get_connection()
    cursor = conn.cursor()

    if request.method == "POST":

        cursor.execute("""
            UPDATE DebtPay
            SET
                PersonName=?,
                Amount=?,
                DueDate=?,
                Note=?
            WHERE DebtID=?
            AND UserID=session["user_id"]
        """,
        (
            request.form["person"],
            request.form["amount"],
            request.form["due_date"],
            request.form["note"],
            id
        ))

        conn.commit()

        return redirect(
            url_for("debt_pay")
        )

    cursor.execute("""
        SELECT *
        FROM DebtPay
        WHERE DebtID=?
    """,(id,))

    debt = cursor.fetchone()

    return render_template(
        "edit_debt_pay.html",
        debt=debt
    )

# =====================================
# DEBT RECEIVE
# =====================================

@app.route("/debt-receive")
def debt_receive():

    if not login_required():
        return redirect(url_for("login"))

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM DebtReceive
        WHERE UserID=?
        ORDER BY DueDate
    """,
    (
        session["user_id"],
    ))

    rows = cursor.fetchall()

    conn.close()

    total_receive = sum(
        debt["Amount"]
        for debt in rows
        if debt["Status"] == "Uncollected"
    )

    return render_template(
        "debt_receive.html",
        debts=rows,
        total_receive=total_receive
    )


# =====================================
# ADD DEBT RECEIVE
# =====================================

@app.route("/add_debt_receive", methods=["POST"])
def add_debt_receive():

    if not login_required():
        return redirect(url_for("login"))

    person = request.form["person"]
    amount = request.form["amount"]
    due_date = request.form["due_date"]
    note = request.form["note"]

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO DebtReceive
        (
            UserID,
            PersonName,
            Amount,
            DueDate,
            Note
        )
        VALUES
        (
            ?, ?, ?, ?, ?
        )
    """,
    (
        session["user_id"],
        person,
        amount,
        due_date,
        note
    ))

    conn.commit()
    conn.close()

    flash("Đã thêm khoản cho vay")

    return redirect(url_for("debt_receive"))

@app.route("/edit_debt_receive/<int:id>", methods=["GET", "POST"])
def edit_debt_receive(id):

    conn = get_connection()
    cursor = conn.cursor()

    if request.method == "POST":

        cursor.execute("""
        UPDATE DebtReceive
        SET
            PersonName=?,
            Amount=?,
            DueDate=?,
            Note=?
        WHERE DebtID=?
        AND UserID=session["user_id"]
        """,
        (
            request.form["person"],
            request.form["amount"],
            request.form["due_date"],
            request.form["note"],
            id
        ))

        conn.commit()
        conn.close()

        flash("Đã cập nhật khoản cho vay")

        return redirect(url_for("debt_receive"))

    cursor.execute("""
    SELECT *
    FROM DebtReceive
    WHERE DebtID=?
    """, (id,))

    debt = cursor.fetchone()

    conn.close()

    return render_template(
        "edit_debt_receive.html",
        debt=debt
    )
@app.route("/delete_debt_receive/<int:id>")
def delete_debt_receive(id):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM DebtReceive WHERE DebtID=?",
        (id,)
    )

    conn.commit()
    conn.close()

    return redirect(url_for("debt_receive"))
# =====================================
# COLLECTED
# =====================================

@app.route("/collected/<int:id>")
def collected(id):

    if not login_required():
        return redirect(url_for("login"))

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    UPDATE DebtReceive
    SET Status='Collected'
    WHERE DebtID=?
    AND UserID=session["user_id"]
    """,(id,))

    conn.commit()
    conn.close()

    flash("Đã thu hồi khoản nợ")

    return redirect(url_for("debt_receive"))


# =====================================
# REPORT
# =====================================

@app.route("/report")
def report():

    if not login_required():
        return redirect(url_for("login"))

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            strftime('%m', TransactionDate) AS MonthNum,
            SUM(Amount) AS TotalAmount
        FROM Transactions
        WHERE Type='Expense'
        AND UserID=?
        GROUP BY strftime('%m', TransactionDate)
        ORDER BY MonthNum
    """,
    (
        session["user_id"],
    ))

    rows = cursor.fetchall()

    months = []
    values = []

    for row in rows:
        months.append(f"Tháng {row['MonthNum']}")
        values.append(float(row['TotalAmount']))

    conn.close()

    return render_template(
        "report.html",
        months=months,
        values=values
    )

    
def auto_backup():

    source = os.path.join(
        os.getcwd(),
        "expense.db"
    )

    if os.path.exists(source):

        backup_folder = "backup"

        os.makedirs(
            backup_folder,
            exist_ok=True
        )

        filename = datetime.now().strftime(
            "backup_%Y%m%d_%H%M%S.db"
        )

        shutil.copy(
            source,
            os.path.join(
                backup_folder,
                filename
            )
        )

@app.route("/savings")
def savings():

    if not login_required():
        return redirect(url_for("login"))

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM Savings
        WHERE UserID=?
        ORDER BY SavingDate DESC
    """,
    (
        session["user_id"],
    ))
    rows = cursor.fetchall()

    conn.close()

    return render_template(
        "savings.html",
        savings=rows
    )

@app.route("/add_saving", methods=["POST"])
def add_saving():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO Savings
    (
        UserID,
        SavingDate,
        Type,
        Amount,
        Note
    )
    VALUES
    (
        ?, ?, ?, ?, ?
    )
    """,
    (
        session["user_id"],
        request.form["date"],
        request.form["type"],
        request.form["amount"],
        request.form["note"]
    ))

    conn.commit()
    conn.close()

    return redirect(
        url_for("savings")
    )

@app.route("/register", methods=["GET","POST"])
def register():

    if request.method == "POST":

        conn = get_connection()
        cursor = conn.cursor()

        try:

            cursor.execute("""
                INSERT INTO Users
                (
                    Username,
                    PasswordHash
                )
                VALUES
                (
                    ?, ?
                )
            """,
            (
                request.form["username"],
                request.form["password"]
            ))

            conn.commit()

            flash("Đăng ký thành công")

            return redirect(
                url_for("login")
            )

        except Exception as e:
            flash(str(e))

        finally:
            conn.close()

    return render_template(
        "register.html"
    )


auto_backup()
# =====================================
# RUN
# =====================================

if __name__ == "__main__":
    app.run(
        debug=False,
        host="0.0.0.0",
        port=5000
    )