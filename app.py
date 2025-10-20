from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
import os

BASE_DIR = os.path.dirname(__file__)
DB_PATH = os.path.join(BASE_DIR, "todo.db")

app = Flask(__name__)
app.secret_key = "change_this_secret_in_production"

# ---------- DB helpers ----------
def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            category TEXT,
            completed INTEGER DEFAULT 0
        )
    ''')
    conn.commit()
    conn.close()

def add_task(title, category):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute('INSERT INTO tasks (title, category) VALUES (?, ?)', (title, category))
    conn.commit()
    conn.close()

def update_task(task_id, title, category, completed):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute('UPDATE tasks SET title=?, category=?, completed=? WHERE id=?',
                (title, category, completed, task_id))
    conn.commit()
    conn.close()

def delete_task(task_id):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute('DELETE FROM tasks WHERE id=?', (task_id,))
    conn.commit()
    conn.close()

def list_tasks():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute('SELECT id, title, category, completed FROM tasks ORDER BY id DESC')
    rows = cur.fetchall()
    conn.close()
    return rows

def get_task(task_id):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute('SELECT id, title, category, completed FROM tasks WHERE id=?', (task_id,))
    row = cur.fetchone()
    conn.close()
    return row

# ---------- Routes ----------
@app.route("/")
def index():
    tasks = list_tasks()
    return render_template("index.html", tasks=tasks)

@app.route("/add", methods=["GET", "POST"])
def add():
    if request.method == "POST":
        title = request.form["title"].strip()
        category = request.form.get("category","").strip()
        if not title:
            flash("❌ Aufgabe darf nicht leer sein", "danger")
            return redirect(url_for("add"))
        add_task(title, category)
        flash("✅ Aufgabe hinzugefügt", "success")
        return redirect(url_for("index"))
    return render_template("add.html")

@app.route("/edit/<int:task_id>", methods=["GET","POST"])
def edit(task_id):
    task = get_task(task_id)
    if not task:
        flash("Aufgabe existiert nicht.", "danger")
        return redirect(url_for("index"))
    if request.method == "POST":
        title = request.form["title"].strip()
        category = request.form.get("category","").strip()
        completed = 1 if request.form.get("completed")=="on" else 0
        update_task(task_id, title, category, completed)
        flash("✅ Aufgabe aktualisiert", "success")
        return redirect(url_for("index"))
    return render_template("edit.html", task=task)

@app.route("/delete/<int:task_id>", methods=["POST"])
def delete(task_id):
    delete_task(task_id)
    flash("Aufgabe gelöscht", "info")
    return redirect(url_for("index"))

if __name__ == "__main__":
    init_db()
    app.run(debug=True)
