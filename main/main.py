from flask import Flask, render_template, request, redirect, url_for
import sqlite3
from datetime import datetime

app = Flask(__name__)

DB_NAME = "inventory.db"

def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

@app.route("/", methods=["GET"])
def index():
    search = request.args.get("search", "")
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS inventory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT,
            quantity_in_stock INTEGER,
            supplier TEXT,
            last_updated TEXT
        )
    """)

    if search:
        cursor.execute("""
            SELECT * FROM inventory
            WHERE name LIKE ? OR category LIKE ?
        """, (f"%{search}%", f"%{search}%"))
    else:
        cursor.execute("SELECT * FROM inventory")

    rows = cursor.fetchall()
    conn.close()
    return render_template("main.html", rows=rows)

@app.route("/add", methods=["GET", "POST"])
def add_item():
    if request.method == "POST":
        name = request.form["name"]
        category = request.form["category"]
        quantity = request.form["quantity"]
        supplier = request.form["supplier"]
        last_updated = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        conn = get_db_connection()
        conn.execute("""
            INSERT INTO inventory (name, category, quantity_in_stock, supplier, last_updated)
            VALUES (?, ?, ?, ?, ?)
        """, (name, category, quantity, supplier, last_updated))
        conn.commit()
        conn.close()
        return redirect(url_for("index"))
    return render_template("add.html")

@app.route("/edit/<int:item_id>", methods=["GET", "POST"])
def edit_item(item_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    if request.method == "POST":
        name = request.form["name"]
        category = request.form["category"]
        quantity = request.form["quantity"]
        supplier = request.form["supplier"]
        last_updated = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        cursor.execute("""
            UPDATE inventory
            SET name=?, category=?, quantity_in_stock=?, supplier=?, last_updated=?
            WHERE id=?
        """, (name, category, quantity, supplier, last_updated, item_id))
        conn.commit()
        conn.close()
        return redirect(url_for("index"))

    cursor.execute("SELECT * FROM inventory WHERE id=?", (item_id,))
    item = cursor.fetchone()
    conn.close()
    return render_template("edit.html", item=item)

@app.route("/delete/<int:item_id>")
def delete_item(item_id):
    conn = get_db_connection()
    conn.execute("DELETE FROM inventory WHERE id=?", (item_id,))
    conn.commit()
    conn.close()
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True)
