from flask import Flask, render_template, request, redirect, url_for,flash
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, FloatField
from wtforms.validators import InputRequired, Email, Length
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import pandas as pd
import numpy as np
import pickle
from sklearn.preprocessing import MinMaxScaler
from flask_mail import Mail, Message
import time

app = Flask(__name__)
app.config['SECRET_KEY'] = 'Thisissupposetobesecret!'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@localhost/db_login'

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = "diabeteseprediction@gmail.com" #your email address
app.config['MAIL_PASSWORD'] = "tejas1234" #your password
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)
Bootstrap(app)
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
model = pickle.load(open('model.pkl', 'rb'))
dataset = pd.read_csv('diabetes1.csv')
dataset_x = dataset.iloc[:, [0,1,2,3]].values
sc = MinMaxScaler(feature_range= (0,1))
dataset_scaled = sc.fit_transform(dataset_x)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(15), unique = True)
    email = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(80))
    # diabetes = db.relationship("Diabetes", backref = "ref", lazy = True)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class LoginForm(FlaskForm):
    email = StringField('email', validators=[InputRequired(), Length(min = 4, max=50)])
    password = PasswordField('password', validators=[InputRequired(), Length(min = 8, max=80)])
    remember = BooleanField('remember me')

class RegisterForm(FlaskForm):
    email = StringField('email', validators=[InputRequired(), Email(message='Invalid Email'), Length(max=50)])
    username = StringField('username', validators=[InputRequired(), Length(min = 4,max=50)])
    password = PasswordField('password', validators=[InputRequired(), Length(min = 8,max=80)])

# class Diabetes(db.Model):
#     srno = db.Column(db.Integer, primary_key=True)
#     glucose_level = db.Column(db.Float)
#     insulin = db.Column(db.Float)
#     bmi = db.Column(db.Float)
#     age = db.Column(db.Float)
#     prediction = db.Column(db.Integer)
#     user_id = db.Column(db.Integer, db.ForeignKey("user.id"))

class GetDetails(FlaskForm):

    glucose_level = FloatField('glucose_level')
    insulin = FloatField('insulin')
    bmi = FloatField('bmi')
    age = FloatField('age')

@app.route("/")
def index():
    return render_template('home.html')    

@app.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    if form.validate_on_submit():
        user = User.query.filter_by(email = form.email.data).first()
        if user:
            if check_password_hash(user.password, form.password.data):
                login_user(user)
                return redirect(url_for('dashboard'))
        return '<h1> Invalid username or password</h1>'
    #     return '<h1>' + form.username.data + '' + form.password.data + '</h1>'

    return render_template("login.html", form = form)

@app.route("/signup", methods=['GET', 'POST'])
def signup():
    form = RegisterForm()

    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data, method='sha256')
        new_user = User(username = form.username.data, email = form.email.data, password = hashed_password)
        db.session.add(new_user)
        db.session.commit()

        flash('New user has been created!')
        # time.sleep(2.4)
        return redirect(url_for('login'))
    #     return '<h1>' + form.username.data + ' ' + form.email.data + ' ' + form.password.data + '</h1>'

    return render_template("signup.html", form = form)

@app.route("/dashboard",  methods=['GET', 'POST'])
@login_required
def dashboard():
    
    # print("Hello World")

    if request.method == 'POST':
        float_features = [float(x) for x in request.form.values()]
        final_features = [np.array(float_features)]
        prediction = model.predict( sc.transform(final_features) )
        if prediction == [1]:
            pred = "You have Diabetes, please consult a Doctor."
            msg = current_user.username
            msg1 = "'s details"
            glucose = request.form['glucose_level']
            insul = request.form['insulin']
            bmi = request.form['bmi']
            age = request.form['age']
            predict = pred

            message = Message(msg, sender = 'tspathak0105@gmail.com', recipients=['pathaktejsu18ce@student.mes.ac.in', 'dundaleshwsa18ce@student.mes.ac.in', 'dhakeharsu18ce@student.mes.ac.in', 'nehadoke17@student.mes.ac.in'])
            message.body = msg + msg1 + "\n" + "Glucose Level = " + glucose +"\n" +  "Insulin = " +  insul +"\n" + "BMI = " +  bmi +"\n" + "Age = " +  age +"\n" + predict
            mail.send(message)
        elif prediction == [0]:
            pred = "You don't have Diabetes."
        output = pred
        # msg = current_user.username

        # print(msg)
        # sucess = "Sucessfully mailed"
        # print("Hello World")
        # return "<h1>Details are successfully added</h2>"
        return render_template("index.html", name=current_user.username,prediction_text = '{}'.format(output))
        
    return render_template("index.html", name=current_user.username)



# @app.route("/history", methods = ['GET', 'POST'])
# @login_required
# def history():
#     user = Diabetes.query.filter_by(user_id = current_user.id).all()
#     return render_template("history.html", user = user, name = current_user.username) 


@app.route('/logout')
def logout():
    logout_user()
    flash('Succesfully Logged Out')
    return redirect(url_for('index'))




if __name__ == '__main__':
    app.run(debug = True)