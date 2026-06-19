from flask import Flask, render_template, request, redirect
import sqlite3

app = Flask(__name__)


def init_db():
    conn = sqlite3.connect('expenses.db')

    conn.execute('''
    CREATE TABLE IF NOT EXISTS expenses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        amount REAL NOT NULL,
        category TEXT NOT NULL,
        expense_date TEXT NOT NULL
    )
    ''')

    conn.commit()
    conn.close()


@app.route('/')
def home():
    conn = sqlite3.connect('expenses.db')
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM expenses")
    expenses = cursor.fetchall()

    cursor.execute("SELECT SUM(amount) FROM expenses")
    total = cursor.fetchone()[0]

    conn.close()

    if total is None:
        total = 0

    return render_template(
        'index.html',
        expenses=expenses,
        total=total
    )


@app.route('/add', methods=['GET', 'POST'])
def add_expense():

    if request.method == 'POST':

        title = request.form['title']
        amount = request.form['amount']
        category = request.form['category']
        expense_date = request.form['expense_date']

        conn = sqlite3.connect('expenses.db')

        conn.execute(
            '''
            INSERT INTO expenses
            (title, amount, category, expense_date)
            VALUES (?, ?, ?, ?)
            ''',
            (title, amount, category, expense_date)
        )

        conn.commit()
        conn.close()

        return redirect('/')

    return render_template('add.html')


@app.route('/delete/<int:id>')
def delete_expense(id):

    conn = sqlite3.connect('expenses.db')

    conn.execute(
        "DELETE FROM expenses WHERE id=?",
        (id,)
    )

    conn.commit()
    conn.close()

    return redirect('/')


if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000)