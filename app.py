from flask import Flask, render_template, request, redirect
import mysql.connector
from datetime import datetime

app = Flask(__name__)

# ✅ Step 1: DB Connection
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="Jeeva@123",
        database="hotel_db"
    )

# ✅ Step 2: Fixed Menu Items
MENU_ITEMS = {
    "Idly": 10,
    "Sambar rice": 20,
    "Dosai": 25,
    "Biryani": 80,
    "Chapati": 15
}

# ✅ Step 3: Home Page - Billing Form
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        name = request.form["customer_name"]
        mobile = request.form["mobile"]
        selected_items = request.form.getlist("item")
        quantities = request.form.getlist("qty")

        db = get_db_connection()
        cursor = db.cursor()

        cursor.execute("INSERT INTO customer_bills (customer_name, mobile) VALUES (%s, %s)", (name, mobile))
        bill_id = cursor.lastrowid

        total = 0
        items = []

        for i in range(len(selected_items)):
            item = selected_items[i]
            qty_str = quantities[i]

            if item in MENU_ITEMS:
                is_number = False
                # ✅ Loop-based isdigit check (no exception)
                for c in qty_str:
                    if c < '0' or c > '9':
                        is_number = False
                        break
                    else:
                        is_number = True

                if is_number:
                    qty = int(qty_str)
                    price = MENU_ITEMS[item]
                    subtotal = qty * price
                    total += subtotal
                    items.append((bill_id, item, price, qty, subtotal))

        cursor.executemany("INSERT INTO bill_items (bill_id, item_name, price, qty, subtotal) VALUES (%s, %s, %s, %s, %s)", items)
        db.commit()
        db.close()

        return render_template("bill.html", name=name, mobile=mobile, items=items, total=total, date=datetime.now())

    return render_template("index.html", menu=MENU_ITEMS)

# ✅ Step 4: View All Bills Page
@app.route("/view")
def view():
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    cursor.execute("""
        SELECT cb.id, cb.customer_name, cb.mobile, cb.bill_date,
               SUM(bi.subtotal) AS total
        FROM customer_bills cb
        LEFT JOIN bill_items bi ON cb.id = bi.bill_id
        GROUP BY cb.id
        ORDER BY cb.bill_date DESC
    """)
    bills = cursor.fetchall()
    db.close()

    return render_template("view.html", bills=bills)

# ✅ Step 5: Run Flask App
if __name__ == "__main__":
    app.run(debug=True)
