import requests
import atexit
from flask import Flask, render_template,request, redirect,url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, time, date
from apscheduler.schedulers.background import BackgroundScheduler

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///todo.db'
db = SQLAlchemy(app)

class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    todo = db.Column(db.String(200), nullable=False)
    deadline = db.Column(db.Date, nullable=False)
    deadline_time = db.Column(db.String(20))
    is_completed = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return f'<Todo {self.id}: {self.todo} -Deadline: {self.deadline}>'

#日付・時間が空欄だった時のデフォルト値
DEFAULT_DATE = str(date.today())
DEFAULT_TIME = time(hour=12, minute=0)

@app.route('/')
def index():
    todo_list = Todo.query.all()
    return render_template('index.html', todo_list=todo_list)

@app.route('/add', methods=['POST'])
def add_todo():
    todo = request.form.get('todo', '').split()
    todo = ' '.join(todo)

    deadline_str = request.form.get('deadline', '')
    if not deadline_str:
        deadline_str = DEFAULT_DATE
    
    #deadline = datetime.strptime(request.form.get('deadline', ''), '%Y-%m-%d')
    deadline = datetime.strptime(deadline_str, '%Y-%m-%d')
    if not todo:
        return redirect(url_for('index', error="Todoと期限は必須項目です。"))
    
    deadline_time = request.form.get('deadline_time')
    if not deadline_time:
        deadline_time = DEFAULT_TIME.strftime('%H:%M')
    print("Deadline Time:",deadline_time)
    # データベースにToDo項目を追加
    new_todo = Todo(todo=todo, deadline=deadline, deadline_time=deadline_time)
    db.session.add(new_todo)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/edit/<int:index>', methods=['GET', 'POST'])
def edit_todo(index):
    todo_to_edit = Todo.query.get_or_404(index)
    if request.method == 'POST':
        todo_to_edit.todo = request.form['todo']
        todo_to_edit.deadline = datetime.strptime(request.form['deadline'], '%Y-%m-%d')
        deadline_time = request.form.get('deadline_time')
        if not deadline_time:
            deadline_time = DEFAULT_TIME.strftime('%H:%M')
        todo_to_edit.deadline_time = deadline_time
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('edit.html', todo=todo_to_edit)

@app.route('/complete/<int:todo_id>', methods=['POST'])
def complete_todo(todo_id):
    todo = Todo.query.get_or_404(todo_id)
    todo.is_completed = not todo.is_completed
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/delete/<int:index>')
def delete_todo(index):
    todo_to_delete = Todo.query.get_or_404(index)
    db.session.delete(todo_to_delete)
    db.session.commit()
    return redirect(url_for('index'))

if __name__=='__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)