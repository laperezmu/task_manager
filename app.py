from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime
import webbrowser
import sqlite3
import signal
import sys

app = Flask(__name__)

def signal_handler(sig, frame):
    print('Cerrando el servidor...')
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

def init_sqlite_db():
    conn = sqlite3.connect('data/outlier.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            createdAt TEXT NOT NULL,
            project TEXT NOT NULL,
            type TEXT NOT NULL,
            taskId TEXT NOT NULL,
            begin TEXT NOT NULL,
            end TEXT NOT NULL,
            notes TEXT,
            elapsedTime REAL NOT NULL,
            earnings REAL NOT NULL,
            timeStatus TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

init_sqlite_db()


project_dictionary = {}
project_dictionary["bee_multiverse"] = {
    "time": 50.0,
    "extra": 10.0,
    "paid_rate": 15,
    "extra_rate": 4.5
}
project_dictionary["bee_lieve"] = {
    "time": 50.0,
    "extra": 10.0,
    "paid_rate": 15,
    "extra_rate": 4.5
}
project_dictionary["bee_creative"] = {
    "time": 50.0,
    "extra": 10.0,
    "paid_rate": 15,
    "extra_rate": 4.5
}
project_dictionary["bee_babadabada"] = {
    "time": 50.0,
    "extra": 10.0,
    "paid_rate": 15,
    "extra_rate": 4.5
}
project_dictionary["bee_there"] = {
    "time": 50.0,
    "extra": 10.0,
    "paid_rate": 15,
    "extra_rate": 4.5
}
project_dictionary["bee_bop"] = {
    "time": 50.0,
    "extra": 10.0,
    "paid_rate": 15,
    "extra_rate": 4.5
}
project_dictionary["bee_square"] = {
    "time": 50.0,
    "extra": 10.0,
    "paid_rate": 15,
    "extra_rate": 4.5
}
project_dictionary["bee_knes_man"] = {
    "time": 50.0,
    "extra": 10.0,
    "paid_rate": 15,
    "extra_rate": 4.5
}
project_dictionary["bee_keepers"] = {
    "time": 50.0,
    "extra": 10.0,
    "paid_rate": 15,
    "extra_rate": 4.5
}
project_dictionary["bee_safety"] = {
    "time": 50.0,
    "extra": 10.0,
    "paid_rate": 15,
    "extra_rate": 4.5
}


@app.route('/')
def index():
    return redirect(url_for('list_projects'))

@app.route('/submit_form', methods=['POST'])
def submit_form():
    # Obteniendo los datos del formulario
    project = request.form['proyecto']
    task_type = request.form['tipo']
    task_id = request.form['id']
    time_begin = request.form['inicio']
    time_end = request.form['fin']
    notes = request.form['notas']

    elapsed_time_in_minutes = calculate_elapsed_time(time_begin, time_end)
    earnings = calculate_earnings(elapsed_time_in_minutes, project)
    time_status = calculate_time_status(elapsed_time_in_minutes, project)
    now = datetime.now()
    createdAt = now.strftime("%x")

    conn = sqlite3.connect('data/outlier.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO tasks (createdAt, project, type, taskId, begin, end, notes, elapsedTime, earnings, timeStatus)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (createdAt, project, task_type, task_id, time_begin, time_end, notes, elapsed_time_in_minutes, earnings, time_status))
    conn.commit()
    conn.close()

    return redirect(url_for('list_projects'))

@app.route('/index', methods=['GET','POST'] )
def list_projects():
    date=request.form.get("date", False)

    if date is False:
        now = datetime.now()
        createdAt = now.strftime("%x")
    else:
        createdAt = date[5:7]+"/"+date[8:]+"/"+date[2:4]


    conn = sqlite3.connect('data/outlier.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM tasks WHERE createdAt = ?', (createdAt, ))
    records = cursor.fetchall()
    conn.close()

    conn = sqlite3.connect('data/outlier.db')
    cursor = conn.cursor()
    cursor.execute('SELECT SUM(earnings) FROM tasks WHERE createdAt = ?', (createdAt, ))
    total_earnings = cursor.fetchall()
    total = 0
    if total_earnings[0][0] is not None:
        total = total_earnings[0][0]
    conn.close()

    return render_template('index.html', records=records, total=total)


def calculate_elapsed_time(begin, end):
    today = datetime.today().date()

    begin_time = datetime.strptime(begin, '%H:%M').time()
    datetime_begin = datetime.combine(today, begin_time)

    end_time = datetime.strptime(end, '%H:%M').time()
    datetime_end = datetime.combine(today, end_time)

    elapsed_time = (datetime_end - datetime_begin).total_seconds() / 60
    return elapsed_time


def calculate_time_status(elapsed_time, project):
    on_time = project_dictionary[project]["time"]
    extra = project_dictionary[project]["extra"]

    if elapsed_time <= on_time:
        return "En tiempo"
    else:
        if elapsed_time - on_time > extra:
            return "Expirado"
        else:
            return "Tiempo extra"
        

def calculate_earnings(elapsed_time_in_minutes, project):
    on_time = project_dictionary[project]["time"]
    extra = project_dictionary[project]["extra"]
    paid_rate = project_dictionary[project]["paid_rate"]
    extra_rate = project_dictionary[project]["extra_rate"]

    if elapsed_time_in_minutes > on_time + extra:
        return 0
    if elapsed_time_in_minutes > on_time:
        return ((on_time/60)* paid_rate) + ((elapsed_time_in_minutes-on_time)/60)*extra_rate
    else:
        return (elapsed_time_in_minutes/60)*paid_rate


if __name__ == '__main__':
    webbrowser.open("http://127.0.0.1:5000", new=0)
    app.run(debug=False)

