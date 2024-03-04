from flask import Flask, render_template, request, url_for, redirect, flash
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect
from datetime import datetime, timedelta

app = Flask(__name__)
app.config['SECRET_KEY'] = 'reminderapp'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///reminderapp.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
# csrf = CSRFProtect(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    task_name = db.Column(db.String)
    task_duration = db.Column(db.Float, nullable=False)
    time_unit = db.Column(db.String)
    creation_time = db.Column(db.DateTime)
    end_time = db.Column(db.DateTime)
    time_left = db.Column(db.DateTime)

with app.app_context():
    db.create_all()

@app.route("/")
def index():
    tasks = User.query.all()
    update_time_left(tasks)
    return render_template('plans.html', tasks=tasks)


def update_time_left(tasks):
    """
    Refresh the count down
    """
    for task in tasks:
        cur_time = datetime.now()
        delta = task.end_time - cur_time
        task.time_left = delta.total_seconds() if task.end_time > cur_time else 0


@app.route("/add-tasks", methods=['GET', 'POST'])
def add_tasks():
    if request.method == 'POST':
        task_name = request.form['title']
        task_duration = float(request.form['content'])
        time_unit = request.form['time_unit']

        if not task_name:
            flash('Task name is required.', 'error')
            return redirect(url_for('add_tasks'))
        if not task_duration:
            flash('Task duration is required.', 'error')
            return redirect(url_for('add_tasks'))
        creation_time = datetime.now()
        end_time = get_end_time(time_unit, task_duration, creation_time)
        new_task = User(task_name=task_name, task_duration=task_duration, time_unit=time_unit, creation_time=creation_time, end_time=end_time)
        db.session.add(new_task)
        db.session.commit()
        flash('Task added successfully!', 'success')
        return redirect(url_for('index'))

    return render_template('task.html')

def get_end_time(unit, period, starttime):
    if unit == "Days":
        new_day = timedelta(days=period)
        ret_time = starttime + new_day
    elif unit == "Hours":
        new_hour = timedelta(hours=period)
        ret_time = starttime + new_hour
    return ret_time

@app.route("/del-task/<int:id>", methods=['POST'])
def del_task(id):
    task = User.query.get(id)
    if task:
        db.session.delete(task)
        db.session.commit()
        flash('Task removed!')
    else:
        flash('Task was not found.', 'error')

    return redirect(url_for('index'))

# if __name__ == "__main__":
#     app.run(debug=True, port=8000)