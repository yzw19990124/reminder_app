from flask import Flask, render_template, request, url_for, redirect, flash
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect
from datetime import datetime

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
    creation_time = db.Column(db.DateTime, default=datetime.now())

with app.app_context():
    db.create_all()

@app.route("/")
def index():
    tasks = User.query.all()
    return render_template('plans.html', tasks=tasks)

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
        new_task = User(task_name=task_name, task_duration=task_duration, time_unit=time_unit)
        db.session.add(new_task)
        db.session.commit()
        flash('Task added successfully!', 'success')
        return redirect(url_for('index'))

    return render_template('task.html')


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

if __name__ == "__main__":
    app.run(debug=True, port=8000)