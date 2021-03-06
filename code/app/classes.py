from flask_wtf import FlaskForm
from flask_login import UserMixin
from werkzeug.security import check_password_hash
from werkzeug.security import generate_password_hash

from wtforms import PasswordField, StringField, SubmitField, RadioField
from wtforms import IntegerField, SelectField, FloatField, DateTimeField, BooleanField
from wtforms.validators import DataRequired, Optional

from flask_wtf.file import FileField, FileRequired, FileAllowed
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import requests

from app import db, login_manager

authors = [{'name':'Kexin Wang','position':'CEO','linkedin':'https://www.linkedin.com/in/sheena-kexin-wang-3a51b7170/', 'pic':'https://www.usfca.edu/sites/default/files/styles/rte_150x150/public/pic1_-_kexin_wang.jpg?itok=Sx5fOi-S'},
{'name':'Daniel Carrera', 'position':'CTO','linkedin':'https://www.linkedin.com/in/daniel-carrera/','pic':'https://www.usfca.edu/sites/default/files/styles/rte_150x150/public/catalog/arts_and_sciences/img_3126_-_daniel_carrera.jpg?itok=V2Fpl961'}, 
{'name':'Boliang Liu','position':'Data Scientist','linkedin':'https://www.linkedin.com/in/boliang-liu/','pic':'https://www.usfca.edu/sites/default/files/styles/rte_150x150/public/images/headshots/boliang_liu.jpg?itok=goQGlgND'},
{'name':'Elyse Cheung-Sutton','position':'Data Scientist', 'linkedin':'https://www.linkedin.com/in/elysecs/','pic':'https://www.usfca.edu/sites/default/files/images/headshots/elyse_cheung-sutton.jpg'},
{'name':'Kris Johnson','position':'Data Scientist','linkedin':'https://www.linkedin.com/in/kr-johnson/','pic':'https://www.usfca.edu/sites/default/files/styles/rte_150x150/public/images/headshots/kristofor_johnson.jpg?itok=UOXI4F-1'},
{'name':'Moh Kaddoura', 'position':'Data Scientist','linkedin':'https://www.linkedin.com/in/moh-kaddoura/','pic':'https://www.usfca.edu/sites/default/files/styles/rte_150x150/public/images/headshots/moh_kaddoura.jpg?itok=AtQnH6ya'},
{'name':'Suren Gunturu', 'position':'Data Scientist','linkedin':'https://www.linkedin.com/in/suren-gunturu/','pic':'https://www.usfca.edu/sites/default/files/images/headshots/suren_gunturu.jpg'}, 
{'name':'Wenyao Zhang', 'position':'Data Scientist', 'linkedin':'https://www.linkedin.com/in/wenyao-zhang/','pic':'https://www.usfca.edu/sites/default/files/styles/rte_150x150/public/images/headshots/wenyao-zhang.jpg?itok=Y09MBXza'}]

WORKOUT_CHOICES = [('1','Bicep Curl'),('2', 'Front Raise'), ('3', 'Shoulder Press')] # choose the exercise
SIDE_CHOICES = [('1', 'Left'),('2', 'Right')] # choose what side you are facing relative to the camera

class UploadFileForm(FlaskForm):
    """
    Class for uploading file when submitted
    """
    # file_selector = FileField('File', validators=[FileRequired()])
    file_selector = FileField('File', validators=[
        FileRequired(),
        FileAllowed(['mp4'], 'mp4 video only'),
    ])
    exercise_selection = SelectField('Workout Name', choices=WORKOUT_CHOICES)
    side_selection = SelectField('Side Faced Relative to the Camera', choices=SIDE_CHOICES)
    submit = SubmitField('Submit')

class User(db.Model, UserMixin):
    """
    Create User class and connect to Postgres so Users can be stored
    """
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)

    def __init__(self, username, email, password):
        """
        Parameters: 
            username(str): user inputted username when logging or registering
            email(str): user inputted email when logging or registering
            password(str): user inputted password when logging or registering
        """
        self.username = username
        self.email = email
        self.set_password(password)

    def set_password(self, password):
        """
        Create password hash
        Arguments: 
            password(str): user inputted password when logging or registering
        """
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """
        Check if password is valid
        Arguments: 
            password(str): user inputted password when logging or registering
        """
        return check_password_hash(self.password_hash, password)

class RegistrationForm(FlaskForm):
    """
    Content of Registration form, with information to add: 
    - username
    - email
    - password
    And a submit button
    """
    username = StringField('Username:', validators=[DataRequired()])
    email = StringField('Email:', validators=[DataRequired()])
    password = PasswordField('Password:', validators=[DataRequired()])
    submit = SubmitField('Submit')

class LogInForm(FlaskForm):
    """
    Content of Log In form with Users able to add: 
    - username
    - password
    And a submit button
    """
    username = StringField('Username:', validators=[DataRequired()])
    password = PasswordField('Password:', validators=[DataRequired()])
    submit = SubmitField('Login')

db.create_all()
db.session.commit()

# user_loader :
# This callback is used to reload the user object
# from the user ID stored in the session.
@login_manager.user_loader
def load_user(id):
    """
    Get the particular user id
    """
    return User.query.get(int(id))

def create_figure():
    """
    Testing function, creating a figure
    """
    data = requests.get('https://msds603-swolemate-s3.s3.us-west-2.amazonaws.com/shiqi_xycoords.json').json()
    fig = Figure()
    axis = fig.add_subplot(1, 1, 1)
    lwrist = [v for record in data for k, v in record.items() if k=='left_wrist']
    x = [i[0] for i in lwrist]
    y = [i[1] for i in lwrist]
    axis.scatter(x,y)
    axis.set_xlabel('X')
    axis.set_ylabel('Y')
    axis.set_title('Left Wrist Position')
    return fig
