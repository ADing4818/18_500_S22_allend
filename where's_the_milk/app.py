'''

This file contains the core implementation of the Flask application (i.e. the
URL routing, methods, database/model methods, and more)

'''

from flask import Flask, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField
from wtforms.validators import InputRequired, Email, Length
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import os

########################################################################
#### Assorted Declarations
########################################################################

# declaring our Flask application and connecting it to Bootstrap (Bootstrap
# module may or may not be used).
app = Flask(__name__)
Bootstrap(app)

# Adding a secret key that is randomly generated
app.config['SECRET_KEY'] = os.urandom(64)

# Initializing database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///main.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
db = SQLAlchemy(app)

# Initializing flask_login variables
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

########################################################################
#### Models
########################################################################

class User(UserMixin, db.Model):
  id = db.Column(db.Integer, primary_key=True)
  username = db.Column(db.String(25), unique=True)
  password = db.Column(db.String(80), unique=True)
  email_address = db.Column(db.String(50), unique=True)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

########################################################################
#### Forms
########################################################################

class Login_form(FlaskForm):
  username = StringField('Username', validators=[InputRequired(), Length(min=5, max=25)])
  password = PasswordField('Password', validators=[InputRequired(), Length(min=5, max=80)])
  confirmation = BooleanField('Confirmation', validators=[InputRequired()])

class Signup_form(FlaskForm):
  username = StringField('Username', validators=[InputRequired(), Length(min=5, max=25)])
  email_address = StringField('Email Address', validators=[InputRequired(), Email(message="ERROR: Invalid email address."), Length(max=50)])
  password = PasswordField('Password', validators=[InputRequired(), Length(min=5, max=80)])
  confirm_password = PasswordField('Confirm Password', validators=[InputRequired(), Length(min=5, max=80)])
  confirmation = BooleanField('Confirmation', validators=[InputRequired()])

########################################################################
#### URL Routing
########################################################################

# The default URL that redirects the user to the homepage
@app.route("/", methods=["GET"])
@login_required
def init():
  return redirect(url_for('homepage'))

# Login page
# HTML/CSS Citation: https://bestjquery.com/tutorial/form/demo42/
@app.route("/login", methods=["GET", "POST"])
def login():
  form = Login_form()

  # validating that the form was submitted and that the fields were verified
  if form.validate_on_submit():
    # querying for the existing user in the db by username
    user = User.query.filter_by(username=form.username.data).first()
    # if user exists, check that the passwords match
    if user:
      # user has successfully logged in - send to homepage
      if check_password_hash(user.password, form.password.data):
        login_user(user)
        return redirect(url_for('homepage'))
    
    return redirect(url_for('login'))

  return render_template('login.html', form=form)

# Signup page
# HTML/CSS Citation: https://www.tutorialrepublic.com/codelab.php?topic=bootstrap&file=elegant-sign-up-form-with-icons
@app.route("/signup", methods=["GET", "POST"])
def signup():
  form = Signup_form()

  # validating that the form was submitted and that the fields were verified
  if form.validate_on_submit():
    username = form.username.data
    hashed_password = generate_password_hash(form.password.data, method='sha256')
    hashed_confirm_password = form.confirm_password.data
    email_address = form.email_address.data
    confirmation = form.confirmation.data

    # checking if the two hashed passwords are the same and the confirmation box was clicked
    if check_password_hash(hashed_password, hashed_confirm_password) and confirmation:
      # creating new user to be stored in db
      new_user = User(username=username, password=hashed_password, email_address=email_address)
      
      # adding and saving new user to the db
      db.session.add(new_user)
      db.session.commit()

      # signing new user in
      login_user(new_user)

      return redirect(url_for('homepage'))

  return render_template('signup.html', form=form)

# Homepage (i.e. Dashboard)
@app.route("/homepage", methods=["GET", "POST"])
@login_required
def homepage():
  return render_template('homepage.html')

# Method to logout a user and return them to the login page
@app.route("/logout")
@login_required
def logout():
  logout_user()
  return redirect(url_for('login'))

if __name__ == "__main__":
  app.run(debug=True)