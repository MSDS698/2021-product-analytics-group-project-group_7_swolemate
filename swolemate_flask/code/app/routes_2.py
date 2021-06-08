from app import application
from flask import render_template, redirect, url_for
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired
from wtforms import SubmitField
import os
import boto3


# S3 Upload Stuff
def upload_file_to_s3(file, bucket_name, acl="public-read"):

    try:
        s3.upload_fileobj(
            file,
            bucket_name,
            file.filename,
            ExtraArgs={
                "ACL": acl,
                "ContentType": file.content_type
            }
        )

    except Exception as e:
        # This is a catch all exception, edit this part to fit your needs.
        print("Something Happened: ", e)
        return e


class UploadFileForm(FlaskForm):
    """Class for uploading file when submitted"""
    file_selector = FileField('File', validators=[FileRequired()])
    submit = SubmitField('Submit')


@application.route('/index')
@application.route('/')
def index():
    """Index Page : Renders index.html with author name."""
    images = [{'text': 'Good Form', 'image': 'https://images.pexels.com/photos/176782/pexels-photo-176782.jpeg?auto=compress&cs=tinysrgb&dpr=1&w=500'},
              {'text': 'User Input', 'image': 'https://images.pexels.com/photos/176782/pexels-photo-176782.jpeg?auto=compress&cs=tinysrgb&dpr=1&w=500'}]
    return (render_template('index.html', images=images))


@application.route('/team')
def team():
    """Index Page : Renders index.html with author name."""
    # return ("<h1> Hello World </h1>")
    authors = ['Boliang Liu', 'Daniel Carrera', 'Elyse Cheung-Sutton',
               'Kris Johnson', 'Kexin Wang', 'Moh Kaddoura',
               'Suren Gunturu', 'Wenyao Zhang']
    return (render_template('team.html', authors=authors))


@application.route('/upload', methods=['GET', 'POST'])
def upload():
    bucket_name = "msds603-swolemate-s3"
    aws_access_key_id = os.environ.get('AWS_ACCESS_KEY_ID')
    aws_secret_access_key = os.environ.get('AWS_SECRET_ACCESS_KEY')
    # print(aws_access_key_id)
    # print(aws_secret_access_key)

    """upload a file from a client machine."""
    file = UploadFileForm()  # file : UploadFileForm class instance
    if file.validate_on_submit():  # Check it's a POST request that's valid
        f = file.file_selector.data  # f : Data of FileField
        filename = f.filename

        session = boto3.Session(
                aws_access_key_id=aws_access_key_id,
                aws_secret_access_key=aws_secret_access_key
                )

        session.resource("s3")\
            .Bucket(bucket_name)\
            .put_object(Key=filename, Body=f, ACL='public-read-write')

        return redirect(url_for('index'))  # Redirect to / (/index) page.
    return render_template('upload.html', form=file)
