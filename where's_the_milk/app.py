'''

This file contains the core implementation of the Flask application (i.e. the
URL routing, methods, database/model methods, and more)

'''

from flask import Flask, render_template
from flask_bootstrap import Bootstrap

# declaring our Flask application and connecting it to Bootstrap
app = Flask(__name__)
Bootstrap(app)

########################################################################
#### URL Routing
########################################################################

# Login page
@app.route("/login")
def login():
  # HTML/CSS Citation: https://bestjquery.com/tutorial/form/demo42/
  return render_template('login.html')

# Signup page
@app.route("/signup")
def signup():
  # HTML/CSS Citation: https://www.tutorialrepublic.com/codelab.php?topic=bootstrap&file=elegant-sign-up-form-with-icons
  return render_template('signup.html')



if __name__ == "__main__":
  app.run(debug=True)