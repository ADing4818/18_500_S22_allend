'''

This file contains the core implementation of the Flask application (i.e. the
URL routing, methods, database/model methods, and more)

'''

from flask import Flask, render_template, redirect, url_for, request
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, validators
from wtforms.validators import InputRequired, Email, Length
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_migrate import Migrate
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
migrate = Migrate(app, db)

# Initializing admin user for database
admin = Admin(app)

# Initializing flask_login variables
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Global data set that the user can choose from for the detection algorithm
global_items = ["soda", "milk", "chips", "egg", "bread", "cereal", "water",
                "peanut_butter", "oreos", "orange", "apple", "lemon", "tomato",
                "potato", "broccoli"]

# Dictionary of aisles:item(s) in given store with a placeholder of 8 for now
aisles_items = {
  "1": [],
  "2": [],
  "3": [],
  "4": [],
  "5": [],
  "6": [],
  "7": [],
  "8": []
}

########################################################################
#### Models
########################################################################

class User(UserMixin, db.Model):
  id = db.Column(db.Integer, primary_key=True)
  username = db.Column(db.String(25), unique=True)
  password = db.Column(db.String(80), unique=True)
  email_address = db.Column(db.String(50), unique=True)
  aisle_1 = db.Column(db.String(500), unique=True, default=None)
  aisle_1_unused = db.Column(db.String(500), unique=True, default=None)

  '''
    Note: more aisles can be added if necessary. We have one aisle here to show
          proof of concept. The system is set up such that more aisles can be 
          added if necessary.
  '''

# Overriding the superclass method to only allow the admin user to view the admin page
class MyModelView(ModelView):
  def is_accessible(self):
    return current_user.username == "admin"

# Adding models to the admin page
admin.add_view(MyModelView(User, db.session))

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

class Items_form(FlaskForm):
  soda = BooleanField('Soda')
  milk = BooleanField('Milk')
  chips = BooleanField('Chips')
  egg = BooleanField('Egg')
  bread = BooleanField('Bread')
  cereal = BooleanField('Cereal')
  water = BooleanField('Water')
  peanut_butter = BooleanField('Peanut Butter')
  oreos = BooleanField('Oreos')
  orange = BooleanField('Orange')
  apple = BooleanField('Apple')
  lemon = BooleanField('Lemon')
  tomato = BooleanField('Tomato')
  potato = BooleanField('Potato')
  broccoli = BooleanField('Broccoli')

########################################################################
#### Helper Functions
########################################################################


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
    # the password is encrypted as method|salt|hash (hash is created with password + random salt)
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

      # sending user to choose their list of items to be evaluated
      return redirect(url_for('items'))

  return render_template('signup.html', form=form)

# Landing page for new users to choose items to analyze
# HTML/CSS Citation: https://bbbootstrap.com/snippets/bootstrap-folder-list-checkbox-and-transform-effect-16091735
@app.route("/items", methods=["GET", "POST"])
@login_required
def items():
  form = Items_form()
  chosen_items = []
  unchosen_items = []

  # confirming if the form/inputs are validated
  if form.validate_on_submit():
    for item in global_items:
      # check what items were checked off and add to list of items user picked
      # Note: even if the user tampers with the item name, the code will not
      #       register the foreign item because the name needs to be matched
      #       against our global item list.
      if request.form.get(item) == "y":
        # check if each item was checked off, and if so, check for validation and add to list of items users picked
        chosen_items.append(item)
      else:
        # storing the list of unchosen items
        unchosen_items.append(item)
    
    '''
      Note: Below implementation can be extended to multiple aisles as described
            above.
    '''

    # Adds items to aisles_items dictionary and sends the new user to the homepage
    aisles_items["1"].extend(chosen_items)
    
    # Adds items to the user model for future reference. A string is used because
    # no lists are allowed as a field of a model.
    current_user.aisle_1 = " ".join(aisles_items["1"])
    current_user.aisle_1_unused = " ".join(unchosen_items)
    
    # saving the items to the db and resetting the lists for the next user
    db.session.commit()
    chosen_items = []
    unchosen_items = []
    aisles_items["1"] = []

    '''
      Note: Once the items form is submitted, the user is essentially editing
            the list of items that they are choosing.
    '''
    
    return render_template('homepage.html')
    
  return render_template('items.html', form=form)

# Homepage (i.e. Dashboard)
# HTML/CSS Citation: https://getbootstrap.com/docs/4.0/layout/grid/
@app.route("/homepage", methods=["GET", "POST"])
@login_required
def homepage():
  return render_template('homepage.html')

# This is the page where the user can see the presence of items after object detection
@app.route("/items_presence/<aisle_number>", methods=["GET", "POST"])
@login_required
def items_presence(aisle_number):
  analyzed_items = []
  omitted_items = []
  # TO-DO: Add to docs (i.e. Readme)

  '''
    Note: For this project, we will be only using aisle 1 since the other aisles are empty.
          The input of this function is "aisle_number", which would be normally used if the
          other aisles were populated.
  '''

  # Turning aisle items string back to a list to easily iterate through
  if current_user.aisle_1 != None:
    analyzed_items = current_user.aisle_1.split()

  if current_user.aisle_1_unused != None:
    omitted_items = current_user.aisle_1_unused.split()

  return render_template('items_presence.html', analyzed_items=analyzed_items, omitted_items=omitted_items)

# Method to logout a user and return them to the login page
@app.route("/logout")
@login_required
def logout():
  logout_user()
  return redirect(url_for('login'))

if __name__ == "__main__":
  app.run(debug=True)