from flask import Flask, render_template, request, redirect, url_for, jsonify
import sqlite3
from pathlib import Path

app = Flask(__name__)
DB = Path(__file__).with_name("expenses.db")

def get_db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    conn.execute("""CREATE TABLE IF NOT EXISTS expenses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        amount REAL NOT NULL,
        category TEXT NOT NULL,
        expense_date TEXT NOT NULL,
        note TEXT DEFAULT ''
    )""")
    conn.commit()
    conn.close()

@app.route("/")
def dashboard():
    conn = get_db()
    expenses = conn.execute("SELECT * FROM expenses ORDER BY expense_date DESC, id DESC").fetchall()
    total = conn.execute("SELECT COALESCE(SUM(amount),0) FROM expenses").fetchone()[0]
    categories = conn.execute("SELECT category, SUM(amount) total FROM expenses GROUP BY category ORDER BY total DESC").fetchall()
    conn.close()
    return render_template("index.html", expenses=expenses, total=total, categories=categories)

@app.post("/add")
def add_expense():
    data = request.form
    conn = get_db()
    conn.execute("INSERT INTO expenses(title,amount,category,expense_date,note) VALUES(?,?,?,?,?)",
                 (data["title"], float(data["amount"]), data["category"], data["expense_date"], data.get("note","")))
    conn.commit(); conn.close()
    return redirect(url_for("dashboard"))

@app.post("/delete/<int:expense_id>")
def delete_expense(expense_id):
    conn = get_db()
    conn.execute("DELETE FROM expenses WHERE id=?", (expense_id,))
    conn.commit(); conn.close()
    return redirect(url_for("dashboard"))

@app.get("/api/summary")
def summary():
    conn = get_db()
    rows = conn.execute("SELECT category, SUM(amount) total FROM expenses GROUP BY category").fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])

if __name__ == "__main__":
    init_db()
    app.run(debug=True)
