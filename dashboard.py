from flask import Flask, render_template
import sqlite3

app = Flask(__name__)

@app.route('/')
def dashboard():
    conn = sqlite3.connect('agriscan.db')
    c = conn.cursor()
    c.execute("SELECT * FROM reports ORDER BY timestamp DESC")
    data = c.fetchall()
    conn.close()
    return render_template('dashboard.html', data=data)

if __name__ == '__main__':
    app.run(debug=True)
