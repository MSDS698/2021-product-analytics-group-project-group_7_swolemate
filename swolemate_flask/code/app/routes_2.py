from app import application
from flask import render_template, redirect, url_for
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired
from wtforms import SubmitField
import os


class UploadFileForm(FlaskForm):
    """Class for uploading file when submitted"""
    file_selector = FileField('File', validators=[FileRequired()])
    submit = SubmitField('Submit')


@application.route('/index')
@application.route('/')
def index():
    """Index Page : Renders index.html with author name."""
    # return ("<h1> Hello World </h1>")
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
    """upload a file from a client machine."""
    file = UploadFileForm()  # file : UploadFileForm class instance
    if file.validate_on_submit():  # Check it's a POST request that's valid
        f = file.file_selector.data  # f : Data of FileField
        filename = f.filename
        # filename : filename of FileField

        file_dir_path = os.path.join(application.instance_path, 'files')
        file_path = os.path.join(file_dir_path, filename)
        # Save file to file_path (instance/ + 'files’ + filename)
        f.save(file_path)

        return redirect(url_for('index'))  # Redirect to / (/index) page.
    return render_template('upload.html', form=file)
