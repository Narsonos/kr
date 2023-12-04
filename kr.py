from flask import Flask, request, redirect, url_for, render_template, flash, session, jsonify
import psycopg2
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.dialects.postgresql import JSONB, INET,TIMESTAMP
from datetime import datetime, timedelta
import random

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://kr:krpass@localhost/kr"
app.config['SECRET_KEY'] = 'e300af42eea1053bf347ebd34dc35e79'
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = '/login'
db = SQLAlchemy()
db.init_app(app)

class User(db.Model, UserMixin):
    __tablename__ = "Users"
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(50), unique = True, nullable=False)
    password_hash = db.Column(db.String(),nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @staticmethod
    def get_by_username(username):
        return User.query.filter_by(username=username).first()

    @staticmethod
    def get_by_id(id):
        return User.query.get(int(id))

    def __repr__(self):
        return f"User {self.username}"

class SomeData(db.Model):
    time = db.Column(TIMESTAMP(), primary_key = True)
    value1 = db.Column(db.Integer())
    value2 = db.Column(db.Integer())
    condition = db.Column(db.String())



@login_manager.user_loader
def load_user(userid):
    return User.get_by_id(userid)


@app.route('/login', methods = ['GET', 'POST'])
def login():
    return render_template('login_admin.html')

@app.route('/logout', methods = ['GET', 'POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/login_validate', methods = ['GET', 'POST'])
def login_validate():
    if request.method == "POST":
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.get_by_username(username)
        actual_login = request.form.get('actual_login')
        #giving the form the validity status
        if not user:
            return jsonify({'success':True, 'login_is_valid':False,'password_is_valid':False}), 200
        else:
            password_valid = user.check_password(password)
            if not password_valid:
                return jsonify({'success':True, 'login_is_valid':True,'password_is_valid':False}), 200
        #the code below is executed when logon attempt is successful
        if actual_login == "no":
            print("fake_login")
            return jsonify({'success':True, 'login_is_valid':True,'password_is_valid':True}), 200
        else:
            print("actual_login")
            login_user(user)
            return redirect(url_for('dashboard'))

@app.route('/dashboard', methods = ['GET', 'POST'])
def dashboard():
    query = db.select(SomeData.time, SomeData.value1).where(SomeData.condition=="good").limit(40)
    rs = db.session.execute(query).all()
    labels,values = [],[]
    for x in rs:
        labels.append(x[0].strftime('%H:%M:%S'))
        values.append(x[1])
    return render_template('dashboard.html', labels=labels, values=values)


def gen_data(quantity):
    initial_time = datetime.now()
    possible_value1 = lambda: random.randint(0,100)
    possible_value2 = lambda: random.randint(15,60)
    possible_conditions = lambda: random.choice(["good","bad","normal"])
    delta = timedelta(minutes=1)

    for i in range(quantity):
        initial_time+=delta
        db.session.execute(db.insert(SomeData).values(
            time=initial_time,
            value1=possible_value1(),
            value2=possible_value2(),
            condition=possible_conditions()
            )
        )    
    db.session.commit()

def gen_users(quantity):
    for i in range(quantity):
        usr = User(username=f"user{i}")
        usr.set_password(f'password{i}')
        print(usr)
        db.session.add(usr)
        db.session.commit()

if __name__ == "__main__":
    app.run(host='0.0.0.0')