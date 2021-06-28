from app import application, classes, db
from flask import render_template, redirect, url_for, Response, request, send_file
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired
from utils import *
from wtforms import SubmitField
from werkzeug.utils import secure_filename
import os
import boto3
import subprocess
import io
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas

from flask_login import current_user, login_user, login_required, logout_user

#docker run --rm -it -p 5000:5000 zwy8203302/app:v0 bash
first_time = 1
value = 0
uploaded_file = None
range_ang_1 = 0
range_ang_2 = 0
range_user_ang_1 = 0
range_user_ang_2 = 0
label = None

@application.route('/index')
@application.route('/')
def index():
    """
    Index Page : Renders index.html
    """
    return (render_template('index.html'))

@application.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    """
    Upload Page
    Lets the user upload a video of performing an exercise
    After the video is uploaded, pose estimation and evaluation is done before directing to the userpage
    """
    aws_access_key_id = os.environ.get('AWS_ACCESS_KEY_ID')
    aws_secret_access_key = os.environ.get('AWS_SECRET_ACCESS_KEY')
    bucket_name = "swolemate-s3"
    s3_location = 'https://s3.console.aws.amazon.com/s3/buckets/swolemate-s3'

    # upload a file from a client machine. 
    file = classes.UploadFileForm() 
    if file.validate_on_submit():
        workout_type = dict(classes.WORKOUT_CHOICES).get(file.exercise_selection.data)
        side = dict(classes.SIDE_CHOICES).get(file.side_selection.data)
        
        f = file.file_selector.data  # f : Data of FileField
        filename = secure_filename(f.filename)
        
        f.save(os.path.join(
            'videos', filename
        ))

        # Pose Estimation Model 
        items = filename.split('.')
        subprocess.run([
            'python3', 'detectron2/demo.py',
            '--config-file', 'detectron2_repo/configs/COCO-Keypoints/keypoint_rcnn_R_50_FPN_3x.yaml',
            '--video-input', 'videos/' + filename,
            '--output', 'output/' + items[0] + '.json',
            '--opts',
            'MODEL.WEIGHTS', 'detectron2://COCO-Keypoints/keypoint_rcnn_R_50_FPN_3x/137849621/model_final_a6e10b.pkl',
            'MODEL.DEVICE', 'cpu',
        ])
        
        # model evaluation
        json_file_name = 'output/' + items[0] + '.json'
        data = load_tester(json_file_name)
        X_train_names = files_in_order('poses_compressed/bicep')
        y_train = get_labels(X_train_names)
        X_train_1, X_train_2 = load_features(X_train_names)
        
        global value
        global uploaded_file
        global range_ang_1
        global range_ang_2
        global range_user_ang_1
        global range_user_ang_2
        global label
        global first_time
        
        # update all global variables 
        value, _, _, range_ang_1, range_ang_2, range_user_ang_1, range_user_ang_2, label = kmeans_test(['demo'], X_train_names, X_train_1=X_train_1, X_train_2=X_train_2, y_train=y_train, data=data, side=side, bool_val=True, exercise=workout_type)
        first_time = 0
        
        # send video to s3 so that it can be viewed on the userpage
        session = boto3.Session()
        session.resource("s3")\
            .Bucket(bucket_name)\
            .upload_file(os.path.join('videos', filename), filename)
        uploaded_file = 'https://swolemate-s3.s3.us-west-2.amazonaws.com/' + filename
        
        print()
        return redirect(url_for('userpage'))
    return render_template('upload.html', form=file,authenticated_user=current_user.is_authenticated)


@application.route('/register',  methods=('GET', 'POST'))
def register():
    """
    Registration page, allows user to create an account
    """
    registration_form = classes.RegistrationForm()
    if registration_form.validate_on_submit():
        username = registration_form.username.data
        email = registration_form.email.data
        password = registration_form.password.data


        user_count = classes.User.query.filter_by(username=username).count() \
            + classes.User.query.filter_by(email=email).count()
        if (user_count > 0):
            return '<h1>Error - Existing user : ' + username \
                   + ' OR ' + email + '</h1>'
        else:
            user = classes.User(username, email, password)
            db.session.add(user)
            db.session.commit()
            return redirect(url_for('login'))
    return render_template('register.html', form=registration_form)


@application.route('/login', methods=['GET', 'POST'])
def login():
    """
    Allows user to login
    """
    login_form = classes.LogInForm()
    if login_form.validate_on_submit():
        username = login_form.username.data
        password = login_form.password.data
        # Look for it in the database.
        user = classes.User.query.filter_by(username=username).first()

        # Login and validate the user.
        if user is not None and user.check_password(password):
            login_user(user)
            return redirect(url_for('upload'))
            # return("<h1> Welcome {}!</h1>".format(username))

    return render_template('login.html', form=login_form)


@application.route('/logout')
@login_required
def logout():
    """
    Allows user to logout
    """
    logout_user()
    return redirect(url_for('index'))


@application.route('/plot.png')
def plot_png():
    fig = classes.create_figure()
    output = io.BytesIO()
    FigureCanvas(fig).print_png(output)
    return Response(output.getvalue(), mimetype='image/png')


@application.route('/userpage', methods=['GET', 'POST'])
@login_required
def userpage():
    """
    Userpage includes all information about the form of the inputted exercises such as: 
    - numerical value encoding how good/bad the exercise is
    - plot showing distance in angles between two poses between inputted exercise and all training samples
    - plots showing frame by frame angles between 
    """
    return render_template('userpage.html', name=current_user.username, value=value, video_name=uploaded_file, 
                          range_ang_1=range_ang_1, range_ang_2=range_ang_2, range_user_ang_1=range_user_ang_1, 
                           range_user_ang_2=range_user_ang_2, label=label, first_time=first_time, 
                           authenticated_user=current_user.is_authenticated)
