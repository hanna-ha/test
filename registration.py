from flask import Flask, render_template, redirect, url_for, session, make_response, request, flash
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, BooleanField, validators
from wtforms.validators import Length, Email, DataRequired
from flask_login import LoginManager, login_user, logout_user, login_required
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash
from common.models import db, User  # implementing a new shared model for the registration and app
import os
import pandas as pd

# Initialise running app
app = Flask(__name__, static_folder='./templates/static') # this is for the css of the html templates)

# Set secret key for the app! (This will need to be moved to environment varible using dotenv once in production)
app.config['SECRET_KEY'] = 'not_so_secret'

# Give address to db, in this case local folder, will become sql server
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///sqlite.db"

#################################################################################

# Getting the reads directory
# Directories csv path
# directories_csv = 'directories.csv'

# # Loading directories in a dataframe
# directories = pd.read_csv(directories_csv, index_col='directory', skipinitialspace=True)

# # Creating directory variable from the data on the csv file
# umaps_directory = directories.loc['umaps_directory_base', 'path'].strip("'")

umaps_directory = '/data/reads/hanna_umap_path_test'

########################

########################

#### Configure DB on app
db.init_app(app)
migrate = Migrate(app, db)

########################

########################

# Setting up login manager
login = LoginManager()
login.init_app(app)

# User_loader function is in charge of retrieving users from db!
@login.user_loader
def user_loader(user_id):
    # Return user info based on id
    return User.query.filter_by(id=user_id).first()

########################

########################
# CLASSES

# Class for logging in - Enabling this here to ensure that the admins are the only ones able to edit and add new users
class LoginForm(FlaskForm):
    email = StringField('email', validators=[Email()])
    password = PasswordField('password', validators=[Length(min=5)])

# Class for registering a user 
class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()], render_kw={"pattern": "[A-Za-z0-9_]+", "title": "Only letters, numbers, and underscores are allowed"})
    email = StringField('email', validators=[Email()])
    password = PasswordField('password', validators=[Length(min=5)])
    repeat_password = PasswordField('repeat_password', validators=[Length(min=5)])
    organization = StringField('Organization', validators=[DataRequired()], render_kw={"pattern": "[A-Za-z0-9_]+", "title": "Only letters, numbers, and underscores are allowed"})
    user_path = StringField('user_path') #, validators=[DataRequired()])
    auth_level = SelectField('Auth Level', choices=[
        ('none', 'Select the access level:'),
        ('admin', 'Admin'),
        ('guest', 'Guest')
    ], validators=[DataRequired()])

    # Checkbox fields for page selections
    aligner = BooleanField('Aligner')
    diffexp = BooleanField('Differential Expression')
    qc_pages = BooleanField('Quality Control')
    ssg = BooleanField('Sample Sheet Generator')
    select_all = BooleanField('Select All')

# Form to update the user information and access 
class UserForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('email', validators=[Email()])
    password = PasswordField('Password', [validators.Optional(), validators.Length(min=5)])
    repeat_password = PasswordField('Repeat Password', [validators.Optional(), validators.EqualTo('password', message='Passwords must match')])
    organization = StringField('Organization', validators=[DataRequired()])
    user_path = StringField('user_path') #, validators=[DataRequired()])
    auth_level = SelectField('Auth Level', choices=[
        ('none', 'Select the access level:'),
        ('admin', 'Admin'),
        ('guest', 'Guest')
    ], validators=[DataRequired()])

    # Checkbox fields for page selections
    aligner = BooleanField('Aligner')
    diffexp = BooleanField('Differential Expression')
    qc_pages = BooleanField('Quality Control')
    ssg = BooleanField('Sample Sheet Generator')
    select_all = BooleanField('Select All')

    

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

        # Check pass
        if user and check_password_hash(user.password, form.password.data):            

            # Login the user (cookie)
            login_user(user)
            # Storing the user credentials in the session for later use
            session['auth_level'] = user.auth_level

            # Only users with admin access are allowed
            if session['auth_level'] == 'admin':
                # Redirect it to the registration page
                return redirect('/register') 
            else:
                form.password.errors.append("You don't have admin access. Please try again with an account having admin access.")
        # If the password is wrong, give error message
        else:
            form.password.errors.append('Wrong password, try again!')

        print(form.errors)
    # Standard return with template
    return render_template('login.html', form=form, errors=form.errors)


# Register page
@app.route('/register', methods=['GET', 'POST'])
@login_required # Added a checkpoint to ensure that the user is logged in to access the page
def register():
    # Redirect to login if the user is not admin
    if session.get('auth_level') != 'admin':
        return redirect(url_for('login'))
    
    form = RegisterForm()
    
    if form.validate_on_submit() and form.password.data == form.repeat_password.data:
        repeat_email = User.query.filter_by(email=form.email.data).first() # Check if email already registered
        repeat_user = User.query.filter_by(username=form.username.data).first() # Check if username already registered (Need to confirm if this check is needed)

        user_path_exist = False 
        user_path=form.user_path.data # If the user_path part is filled during registration

        if os.path.isdir(user_path): # If the entered user_path exists - Should exist as we are not creating
            user_path_exist = True

        elif user_path == '': # If no entry from user
            try:
                if os.path.exists(umaps_directory): # All clear
                    user_directory = os.path.join(umaps_directory, form.username.data)
                    user_path_exist = True
                else:
                    # Trying to determine the reason why umaps_directory doesn't exist
                    if not os.path.exists(umaps_directory):
                        form.user_path.errors.append(f'Reads directory ({umaps_directory}) does not exist.')
                    elif not os.access(umaps_directory, os.R_OK):
                        form.user_path.errors.append(f'Reads directory ({umaps_directory}) is not accessible due to permissions.')
                    else:
                        form.user_path.errors.append(f'Unknown issue accessing reads directory ({umaps_directory}).')
                        
                    user_path_exist = False
            
            except Exception as e:
                form.user_path.errors.append(f'Failed to access reads directory ({umaps_directory}): {e}')
                user_path_exist = False

        else:
            user_path_exist = False # If either doesnt exist
            form.user_path.errors.append('Reads directory not created. Possible reasons: User path provided could be wrong or umaps_directory mentioned in directories.csv might not exist.')   

        # Adding two checkpoints to identify the actual problem
        if repeat_user is None and repeat_email is None: 

            if user_path_exist is True:
                try:
                    # User object
                    user = User(
                        username=form.username.data,  
                        email=form.email.data,
                        password= generate_password_hash(form.password.data),
                        organization=form.organization.data,
                        user_path=form.user_path.data if form.user_path.data != '' and os.path.isdir(user_path) else user_directory,
                        auth_level=form.auth_level.data,
                        aligner=form.aligner.data,
                        diffexp=form.diffexp.data,
                        qc_pages=form.qc_pages.data,
                        ssg=form.ssg.data,
                    )
                    db.session.add(user)
                    
                    # If no user_path mentioned
                    if user_path == '': 
                        # Create a folder for the user
                        user_name = form.username.data # selecting the user input username
                        user_folder = os.path.join(umaps_directory, user_name)
                        os.makedirs(user_folder, exist_ok=True)
                    # If user_path mentioned, we will use that path as reads alignment. (IDK if we should create a dir inside the path with the username. Keeping this way now)
                    else:
                        user_folder = user_path

                    if os.path.isdir(user_folder): # If folder created or exists
                        # Commit only if everything successful
                        db.session.commit()
                        return redirect(url_for('register_success'))
                    
                    else:
                        # Rollback if any error
                        db.session.rollback()
                        form.email.errors.append(f'Directory for user not created. Please check if the location {user_folder} exists')

                except Exception as e:
                    form.email.errors.append(f'An error occurred during registration: {e}')
            else:
                # Only for path not exist error
                render_template('register.html', form=form, errors=form.errors)
        else:
            form.email.errors.append('There is already an account associated with this username or email!')
    else:
        if form.password.data != form.repeat_password.data:
            form.repeat_password.errors.append('The passwords do not match!')

    response = make_response(render_template('register.html', form=form, errors=form.errors))
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    return response


# Registration successful page
@app.route('/register_success')
@login_required
def register_success():
    form = RegisterForm()
    response = make_response(render_template('register_success.html', form=form, errors=form.errors))
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    return response


# Update data page
@app.route('/update')
@login_required
def update():
    form = RegisterForm()
    our_users = User.query.order_by(User.id) # to display the available users in the database to the frontend

    response = make_response(render_template('update.html', form=form, errors=form.errors, our_users=our_users))
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    return response 


# Edit user page # Need to add some error handling
@app.route('/edit_user/<int:id>', methods=['GET', 'POST']) # clicking on edit from update page takes to /edit_user/id
@login_required
def edit_user(id):
    id_change = User.query.get_or_404(id) # Checks for id and error if id doesn't exist 
    form = UserForm(obj=id_change) # Using only with current user data

    if form.validate_on_submit() and request.method == "POST":

        updates = False # Default is false, no changes

        if 'edit-username' in request.form and request.form['edit-username'] != id_change.username: # default value of edit_username is the current username. if changed, it will update
            id_change.username = request.form['edit-username']
            updates = True

        if 'edit-email' in request.form and request.form['edit-email'] != id_change.email: # Similar as the username. 
            id_change.email = request.form['edit-email']
            updates = True

        if 'edit-organization' in request.form and request.form['edit-organization'] != id_change.organization: 
            id_change.organization = request.form['edit-organization']
            updates = True

        if 'edit-auth_level' in request.form and request.form['edit-auth_level'] != id_change.auth_level:
            id_change.auth_level = request.form['edit-auth_level']
            updates = True

        # The other changes are not much restricting. But these are important and can have an effect on the portal. So, treating them differently.
        if 'edit-user-path' in request.form and request.form['edit-user-path'] != id_change.user_path:
            if os.path.isdir(request.form['edit-user-path']): # Only checking and not creating the new path since we are expecting to have a folder ready in cases where we are updating user path
                id_change.user_path = request.form['edit-user-path']
                updates = True
            else:
                form.user_path.errors.append(f'Directory not found. Please check if the location {request.form["edit-user-path"]} exists')
                return render_template("edit_user.html", form=form, id_change=id_change, errors=form.errors)
        
        # Checks if both password entries are there and they are the same
        if 'edit-password' in request.form and request.form['edit-password']: # Default value of password is not given. Whatever entry is added will be the new password
            if request.form['edit-password'] == request.form['edit-re-password']: # Only if the entered password is same
                if request.form['edit-password'].strip() != '':
                    id_change.password = generate_password_hash(request.form['edit-password'])
                    updates = True
                else:
                    form.password.errors.append(f'Password cannot be empty.')
                    return render_template("edit_user.html", form=form, id_change=id_change, errors=form.errors)
            else:
                form.password.errors.append(f'Passwords does not match.')
                return render_template("edit_user.html", form=form, id_change=id_change, errors=form.errors)

        # Checking if the checkboxes are updated
        aligner = 'aligner' in request.form
        diffexp = 'diffexp' in request.form
        qc_pages = 'qc_pages' in request.form
        ssg = 'ssg' in request.form

        if aligner != id_change.aligner: # Similar to before, updates = True if any changes
            id_change.aligner = aligner
            updates = True

        if diffexp != id_change.diffexp:
            id_change.diffexp = diffexp
            updates = True

        if qc_pages != id_change.qc_pages:
            id_change.qc_pages = qc_pages
            updates = True

        if ssg != id_change.ssg:
            id_change.ssg = ssg
            updates = True

        if updates:
            try:
                db.session.commit() # If updates are there and are proper, commit
                print('Commit worked')
                flash('User updated successfully', 'success')
                return redirect(url_for('update'))
            except Exception as e:
                print(e)
                db.session.rollback() # If there is an issue with the update, rollback
                form.errors.append(f'An error occurred while updating: {e}')
                return render_template("edit_user.html", form= form, id_change = id_change)
            
        else:
            return redirect(url_for('update')) # If clicked without any updates, will return to the update page
    else:
        response = make_response(render_template("edit_user.html", form=form, id_change=id_change, errors=form.errors))
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
        response.headers['Pragma'] = 'no-cache'
        return response

        
# Remove user page
@app.route('/remove_user/<int:id>', methods=['GET', 'POST']) # clicking on remove from update page takes to /remove_user/id
@login_required
def remove_user(id):
    form = UserForm() 
    
    id_to_remove = User.query.get_or_404(id) # Checks for id and error if id doesn't exist 

    if form.validate_on_submit() and request.method == "POST":
        if 'confirm' in request.form: # Deletes user if Yes clicked. I dont know if I should add any other confirmation here
            try:
                db.session.delete(id_to_remove)
                db.session.commit()
                print('User deleted successfully')
                return redirect(url_for('update')) # IF deleted, goes back to update page
            except Exception as e:
                print(e)
                form.errors.append(f'An error occurred while updating: {e}')
                return render_template("remove_user.html", form=form, id_to_remove=id_to_remove, errors=form.errors)
            
        elif 'cancel' in request.form:
            return redirect(url_for('update')) # Returns to update page if cancelled
    else:
        response = make_response(render_template("remove_user.html", form= form, id_to_remove = id_to_remove, errors=form.errors))
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
        response.headers['Pragma'] = 'no-cache'
        return response


# Logout endpoint (removes cookies)
@app.route('/logout')
def logout():
    logout_user()
    session.pop('email', None) 
    session.clear() # Hopefully clear all sessions data
    print("Logout successful, redirecting to login")
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(port=3204, host="192.168.168.60")
