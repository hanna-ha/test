from flask import Flask, render_template, redirect, session
from datetime import datetime, timedelta
# For authorisation forms
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import Length, Email

# Manage DB connection
from flask_migrate import Migrate

# Login helpers
from flask.helpers import url_for
from flask_login import LoginManager, login_user, logout_user
from werkzeug.security import check_password_hash

from common.models import db, User




######## end imports

# Import Dash App
from dash_app.__main__ import create_dash_application

# To prevent multiple failed login attempts
max_user_failed_attempts = 5
time_of_lockout = timedelta(minutes=60)

# Initialise running app
app = Flask(__name__,
    static_folder='./templates/static' # this is for the css of the html templates
    )
# Set secret key for the app! (This will need to be moved to environment varible using dotenv once in production)
app.config['SECRET_KEY'] = 'not_so_secret'


# Give address to db, in this case local folder, will become sql server
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///sqlite.db"

#### Configure DB on app
db.init_app(app)
migrate = Migrate(app, db)
 
######## Set up login manager
login = LoginManager()
login.init_app(app)

#### Set up dash app
create_dash_application(app)

# user_loader function is in charge of retrieving users from db!
@login.user_loader
def user_loader(user_id):
    # Return user info based on id
    return User.query.filter_by(id=user_id).first()


########################
# CLASSES

# Class for logging in
class LoginForm(FlaskForm):
    id = db.Column(db.Integer, primary_key=True)
    email = StringField('email', validators=[Email()])
    password = PasswordField('password', validators=[Length(min=5)])


########################


#########################
# ROUTES

# Home route redirects to login
@app.route('/')
def index():
    return redirect(url_for('login'))


# Route to login
@app.route('/login', methods=['GET', 'POST'])
def login():
    # Declare login form obj
    form = LoginForm()
    # Check if the form is valid or not
    if form.validate_on_submit():
        # If the form is valid we want to get the user obj by email, and check the hashed pass
        user = User.query.filter_by(email=form.email.data).first()

        # If the user object is none, it means that it's not present in the DB and consequently was never registered
        if not user:
            # This 'artificially' registers an error associated with the email!!
            form.email.errors.append(f'Could not find an account associated with the email {form.email.data}')

            # form.errors.pop('password')
            print(form.errors.keys())
            return render_template('login.html', form=form, errors=form.errors)

        if user:
            # Check if account is locked out
            if user.lockout_until and datetime.utcnow() < user.lockout_until:
                form.email.errors.append('Account is temporarily locked. Try again later.')
                return render_template('login.html', form=form, errors=form.errors)
        
        # Check password
        if user and check_password_hash(user.password, form.password.data):            

            # Login the user (cookie)
            login_user(user)
            # Storing the user credentials in the session for later use
            session['email'] = user.email
            session['username'] = user.username
            session['auth_level'] = user.auth_level
            session['user_path'] = user.user_path
            session['aligner'] = user.aligner
            session['diffexp'] = user.diffexp
            session['qc_pages'] = user.qc_pages
            session['ssg'] = user.ssg

            # Resetting the failed_attempts to 0
            user.failed_attempts = 0
            user.lockout_until = None
            db.session.commit()

            # Redirect it to the dash app!
            return redirect('/app/home') 
        
        # If the password is wrong, add lockdown timer and failed attempts
        else:
            if user.failed_attempts is None:
                user.failed_attempts = 0
            
            user.failed_attempts += 1 # Adds failed attempts

            if user.failed_attempts >= max_user_failed_attempts: # Modify failed attempts if need change
                user.lockout_until = datetime.utcnow() + time_of_lockout
            
            db.session.commit()

            form.password.errors.append(f'Wrong password, try again! [You have {int(max_user_failed_attempts-user.failed_attempts)} tries before getting locked out.]')

        print(form.errors)
    # Standard return with template
    return render_template('login.html', form=form, errors=form.errors)



# Logout endpoint (removes cookies)
@app.route('/logout')
def logout():
    logout_user()
    session.pop('auth_level', None) 
    print("Logout successful, redirecting to login")
    return redirect(url_for('login'))







# @du.callback(
#     output=Output("upload-status", "children"),
#     id="upload-data",
# )
# def callback_on_completion(status: du.UploadStatus):
#     return html.Ul([html.Li(str(x)) for x in status.uploaded_files])
############################


if __name__ == '__main__':
    app.run()


##########################