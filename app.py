from flask import Flask, render_template, url_for, request, redirect, send_from_directory, abort, session, flash, \
    Response, make_response
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os, json, boto3
from werkzeug.utils import secure_filename
from flask_wtf import FlaskForm
from flask_bootstrap import Bootstrap
from wtforms import StringField, PasswordField, BooleanField, SelectField
from wtforms.validators import InputRequired, Email, Length
import email_validator
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from whitenoise import WhiteNoise
from flask_s3 import FlaskS3
from filters import convert_date, file_type, show_own_items, filter_image, filter_pdf, filter_word, filter_misc, \
    get_image, remove_file_id, filter_video, get_avatar, calc_age
import pdfkit
import pydf
import subprocess
import calendar
from config import S3_BUCKET, S3_KEY, S3_SECRET_ACCESS_KEY, SECRET_KEY

# Initiate app
app = Flask(__name__, template_folder='Templates')

# Config for wkhtmltopdf which converts a html page to pdf
# COMMENT THIS WHEN TESTING LOCAL!!
# UNCOMMENT THIS WHEN PUSHING TO PRODUCTION!!
app.config["WKHTMLTOPDF_CMD"] = subprocess.Popen(
    ['which', os.environ.get('WKHTMLTOPDF_BINARY', 'wkhtmltopdf')],
    stdout=subprocess.PIPE).communicate()[0].strip()

# Switch between dev and production database
ENV = 'prod'
if ENV == 'dev':
    app.debug = True
    # dev database
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:seasalt99@localhost:5000/UserInfo'
elif ENV == 'prod':
    # production database
    app.debug = False
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://nxxdepmkljikwb' \
                                            ':0ac9891a1e1d987c4a859cc1ea4851955ba6a9867656bff7af2e1843b557ec0a@ec2-54' \
                                            '-157-234-29.compute-1.amazonaws.com:5432/d8v7k04hg7aqu3'

# import bootstrap
bootstrap = Bootstrap(app)

# Enable WhiteNoise
app.wsgi_app = WhiteNoise(app.wsgi_app, root='Static/')
app.wsgi_app = WhiteNoise(
    app.wsgi_app,
    root='Static/',
    prefix='Static/'
)

# Initialise login manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Allow jinja template to enable filters for tables
app.jinja_env.filters['convert_date'] = convert_date
app.jinja_env.filters['file_type'] = file_type
app.jinja_env.filters['show_own_items'] = show_own_items
app.jinja_env.globals.update(show_own_items=show_own_items)
app.jinja_env.globals.update(filter_image=filter_image)
app.jinja_env.globals.update(filter_video=filter_video)
app.jinja_env.globals.update(filter_word=filter_word)
app.jinja_env.globals.update(filter_pdf=filter_pdf)
app.jinja_env.globals.update(filter_misc=filter_misc)
app.jinja_env.globals.update(get_image=get_image)
app.jinja_env.globals.update(remove_file_id=remove_file_id)
app.jinja_env.globals.update(get_avatar=get_avatar)
app.jinja_env.globals.update(calc_age=calc_age)

# Secret key
app.config["SECRET_KEY"] = SECRET_KEY

# Suppresses warnings
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Flash message secret key (not related to any databases; flask just need a key for flash messages)
app.secret_key = 'lanadelrey'

# Use SQLAlchemy for the db
db = SQLAlchemy(app)


# Form class to log in
class LoginForm(FlaskForm):
    email = StringField('Email', validators=[InputRequired(), Email(message="Invalid email address")])
    password = PasswordField('Password', validators=[InputRequired(), Length(min=8, max=80)])
    remember = BooleanField('Remember me for next time')


# Form class to sign up
class SignupForm(FlaskForm):
    email = StringField('Email', validators=[InputRequired(), Email(message="Invalid email address")])
    password = PasswordField('Password', validators=[InputRequired(), Length(min=8, max=80)])
    name = StringField('Name', validators=[InputRequired(), Length(min=1, max=50)])
    interests = StringField('Interests', validators=[InputRequired(), Length(min=1, max=500)])
    bio = StringField('Bio', validators=[InputRequired(), Length(min=1, max=500)])
    education = StringField('Education', validators=[InputRequired(), Length(min=1, max=500)])
    education = StringField('Education', validators=[InputRequired(), Length(min=1, max=500)])
    occupation = StringField('Occupation', validators=[InputRequired(), Length(min=1, max=500)])
    birth_year = SelectField('Year', choices=[year for year in range(1900, 2021)])
    birth_month = SelectField('Month', choices=[month for month in calendar.month_name][1:])
    birth_date = SelectField('Date', choices=[day for day in range(1, 32)])


# Class to store user details
class UserInfo(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(), unique=True)
    password = db.Column(db.String(80))
    interests = db.Column(db.String(500))
    bio = db.Column(db.String(500))
    education = db.Column(db.String(500))
    occupation = db.Column(db.String(500))
    birth_year = db.Column(db.Integer)
    birth_month = db.Column(db.String)
    birth_date = db.Column(db.Integer)

    visit = db.Column(db.Integer)

    # Constructor
    def __init__(self, name, email, password, interests, bio, occupation, education, birth_year, birth_date,
                 birth_month):
        self.name = name
        self.email = email
        self.password = password
        self.interests = interests
        self.bio = bio
        self.occupation = occupation
        self.education = education
        self.birth_date = birth_date
        self.birth_month = birth_month
        self.birth_year = birth_year
        self.visit = 0


@login_manager.user_loader
def load_user(user_id):
    return UserInfo.query.get(int(user_id))


@app.route('/', methods=['POST', 'GET'])
def landing():
    logged_in = current_user.is_authenticated
    return render_template('landing.html', logged_in=logged_in)


@app.route('/signup', methods=['POST', 'GET'])
def signup():
    signup_form = SignupForm()

    # Store the user's pswd as a hash to improve security
    if signup_form.validate_on_submit():
        hash_pswd = generate_password_hash(signup_form.password.data, method="sha256")
        new_user = UserInfo(email=signup_form.email.data, password=hash_pswd,
                            name=signup_form.name.data, interests=signup_form.interests.data, bio=signup_form.bio.data,
                            occupation=signup_form.occupation.data, education=signup_form.education.data,
                            birth_year=signup_form.birth_year.data, birth_month=signup_form.birth_month.data,
                            birth_date=signup_form.birth_date.data)
        db.session.add(new_user)
        db.session.commit()

        user = UserInfo.query.filter_by(email=signup_form.email.data).first()
        login_user(user)

        return redirect(url_for("profile"))

    return render_template('signup.html', signup_form=signup_form)


@app.route('/login', methods=['POST', 'GET'])
def login():
    login_form = LoginForm()

    if login_form.validate_on_submit():

        # Check if the user is in the database seeing if the assigned user var exists and checking if pswd match
        user = UserInfo.query.filter_by(email=login_form.email.data).first()
        if user:
            if check_password_hash(user.password, login_form.password.data):
                login_user(user, remember=login_form.remember.data)

                return redirect(url_for("profile"))

        flash("Invalid email/password combination. Please try again.")
        return render_template('login.html', login_form=login_form)

    return render_template('login.html', login_form=login_form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for("landing"))


@app.route('/profile', methods=['POST', 'GET'])
@login_required
def profile():
    if current_user.visit:
        current_user.visit += 1
    else:
        current_user.visit = 1
    db.session.commit()
    return render_template('profile.html', name=current_user.name, interests=current_user.interests,
                           bio=current_user.bio, id=current_user.id, counter=current_user.visit,
                           occupation=current_user.occupation, education=current_user.education,
                           birth_year=current_user.birth_year, birth_month=current_user.birth_month,
                           birth_date=current_user.birth_date)


# Allows other people to view a portfolio
@app.route('/view_user_portfolio/<int:id>', methods=['POST', 'GET'])
def view_user_portfolio(id):
    user = UserInfo.query.get_or_404(id)
    name = user.name

    if user.visit:
        user.visit += 1
    else:
        user.visit = 1

    s3 = boto3.resource('s3',
                        aws_access_key_id=S3_KEY,
                        aws_secret_access_key=S3_SECRET_ACCESS_KEY)
    bucket = s3.Bucket(S3_BUCKET)
    storage = bucket.objects.all()

    return render_template('view_user_portfolio.html', user_id=id, name=name, storage=storage, bucket=bucket)


@app.route('/pdf')
def pdf():
    # This is for heroku
    config = pdfkit.configuration(wkhtmltopdf=app.config['WKHTMLTOPDF_CMD'])

    # This is for localhost
    # config = pdfkit.configuration(wkhtmltopdf="Static///wkhtmltopdf///bin///wkhtmltopdf.exe")
    options = {
        "enable-local-file-access": None
    }
    css = ["Static/css/profile.css"]
    link = get_avatar(current_user.id)
    # change https link to http
    img_src = link[0:4] + link[5:]
    html = render_template('profile_pdf.html', name=current_user.name, interests=current_user.interests,
                           bio=current_user.bio, id=current_user.id, img_src=img_src,
                           occupation=current_user.occupation,
                           education=current_user.education,
                           birth_year=current_user.birth_year, birth_month=current_user.birth_month,
                           birth_date=current_user.birth_date)

    download_pdf = pdfkit.from_string(html, False, configuration=config, options=options, css=css)
    response = make_response(download_pdf)
    response.headers["Content-Type"] = "application/pdf"
    response.headers["Content-Disposition"] = "inline;filename=output.pdf"
    return response


# Upload an user avatar
@app.route('/s3_avatar_upload', methods=['POST'])
def s3_avatar_upload():
    s3 = boto3.resource('s3',
                        aws_access_key_id=S3_KEY,
                        aws_secret_access_key=S3_SECRET_ACCESS_KEY)
    file = request.files["image"]

    # Check if the uploaded file is an image
    if not filter_image(file.filename):
        flash("File type not supported. Accepted image extensions are PNG, JPG and JPEG.")
        return redirect('profile')

    avatar_folder = "Avatar/" + str(current_user.id) + ".png"
    s3.Bucket(S3_BUCKET).put_object(Key=avatar_folder, Body=file)

    return redirect('profile')


# Upload file to S3 into the user's subfolder based on their id
@app.route('/s3_upload', methods=['POST'])
def s3_upload():
    # TODO: SAVE THESE IN ENV FILE
    s3 = boto3.resource('s3',
                        aws_access_key_id=S3_KEY,
                        aws_secret_access_key=S3_SECRET_ACCESS_KEY)

    file = request.files["image"]
    sanitised_filename = secure_filename(file.filename)
    user_folder = str(current_user.id) + "/" + sanitised_filename
    s3.Bucket(S3_BUCKET).put_object(Key=user_folder, Body=request.files['image'])

    flash("File uploaded!")
    return redirect('art_portfolio')


# Delete an item from S3 storage
@app.route('/s3_delete', methods=["POST"])
def s3_delete():
    key = request.form['key']
    s3 = boto3.resource('s3',
                        aws_access_key_id=S3_KEY,
                        aws_secret_access_key=S3_SECRET_ACCESS_KEY)
    s3.Bucket(S3_BUCKET).Object(key).delete()

    flash("File Deleted!")

    return redirect('art_portfolio')


# Download an item from S3 storage
@app.route('/s3_download', methods=["POST"])
def s3_download():
    key = request.form['key']
    s3 = boto3.resource('s3',
                        aws_access_key_id=S3_KEY,
                        aws_secret_access_key=S3_SECRET_ACCESS_KEY)
    bucket = s3.Bucket(S3_BUCKET)
    file = s3.Bucket(S3_BUCKET).Object(key).get()

    # If the requested file is an image, display it on the browser
    if filter_image(key):
        return Response(file['Body'].read(),
                        mimetype='None'
                        )

    # Otherwise, prompt the user to download the file
    return Response(file['Body'].read(),
                    mimetype='None',
                    headers={"Content-Disposition": "attachment;filename={}".format(key)}
                    )


# Route url
@app.route('/art_portfolio', methods=['POST', 'GET'])
@login_required
def art_portfolio():
    # TODO: SAVE THE ACCESS KEYS ELSEWHERE
    s3 = boto3.resource('s3',
                        aws_access_key_id=S3_KEY,
                        aws_secret_access_key=S3_SECRET_ACCESS_KEY)
    bucket = s3.Bucket(S3_BUCKET)
    storage = bucket.objects.all()

    return render_template('art_portfolio.html', owner=current_user.email,
                           bucket=bucket, storage=storage, user_id=current_user.id, name=current_user.name)


@app.route('/edit_profile/<int:id>', methods=['GET', 'POST'])
def edit_profile(id):
    if request.method == 'POST':
        user = UserInfo.query.get_or_404(id)
        user.interests = request.form['interests']
        user.bio = request.form['bio']
        user.occupation = request.form['occupation']
        user.education = request.form['education']

        try:
            db.session.commit()
            return redirect('/profile')
        except:
            return "Error updating :("

    else:
        return render_template('edit_profile.html', id=current_user.id, interests=current_user.interests,
                               bio=current_user.bio, education=current_user.education,
                               occupation=current_user.occupation)


# Run the app on port 9999 as 5000 is taken by Postgres
if __name__ == "__main__":
    app.run(port=9999, debug=True)
