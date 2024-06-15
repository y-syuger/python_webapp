import requests
from apscheduler.schedulers.blocking import BlockingScheduler
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, time, date

# Flaskアプリケーションのインスタンスを作成
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///todo.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# SQLAlchemyのインスタンスを作成
db = SQLAlchemy(app)

# Todoモデルの定義
class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    todo = db.Column(db.String(200), nullable=False)
    deadline = db.Column(db.Date, nullable=False)
    deadline_time = db.Column(db.String(20))

# ここに、利用者のLINEトークンを入れてください。
LINE_NOTIFY_TOKEN = "Your_Line_Notify_Token"

def send_todo_notifications():
    with app.app_context():
        try:
            today = date.today()

            # データベースからToDoリストを取得
            todos = Todo.query.filter_by(deadline=today).all()
            if not todos:
                print("No todos found.")
                return
            
            # 通知メッセージを作成
            message = "Today's ToDo List:\n"
            for todo in todos:
                message += f"{todo.todo} - {todo.deadline} {todo.deadline_time}\n"
            
            # LINE通知を送信
            headers = {'Authorization': f'Bearer {LINE_NOTIFY_TOKEN}'}
            payload = {'message': message}
            response = requests.post('https://notify-api.line.me/api/notify', headers=headers, data=payload)

            if response.status_code == 200:
                print('Notification sent successfully')
            else:
                print('Failed to send notification')
        except Exception as e:
            print(f"An error occurred: {e}")

# スケジューラの設定
scheduler = BlockingScheduler()
# 毎日6時にsend_todo_notifications関数を実行
#scheduler.add_job(send_todo_notifications, 'cron', hour=6, minute=0)

# 10秒ごとに通知を送る
scheduler.add_job(send_todo_notifications, 'interval', seconds=10)

try:
    scheduler.start()
except (KeyboardInterrupt, SystemExit):
    pass
