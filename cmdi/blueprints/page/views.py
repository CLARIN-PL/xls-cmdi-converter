import datetime
import os

from flask import Blueprint, render_template, request, url_for, send_from_directory, send_file
from lib.parser import parse

from werkzeug.utils import secure_filename, redirect

page = Blueprint('page', __name__, template_folder='templates')


@page.route('/')
def home():
    return render_template('page/home.html')


@page.route('/upload', methods=['GET', 'POST'])
def upload():
    """
    Handles file uploading.
    :return: Template
    """

    if request.method == 'POST':
        creator = request.form['creator']

        f = request.files['file']

        _format = "%Y-%m-%d %H:%M:%S"
        now = datetime.datetime.utcnow().strftime(_format)

        filename = secure_filename(now + '_' + str(creator) + '_' + f.filename)

        f.save('files/'+filename)
        parse(creator, filename)
        return redirect(url_for('page.downloads'))

    return render_template('page/upload.html')


@page.route('/downloads')
def downloads():
    """
    Generates view with list of all processed files.
    :return: Template
    """

    files = list()
    for root, dirs, filenames in os.walk('files/'):
        for f in filenames:
            if f.endswith('.zip'):
                files.append({'name': f.replace('.zip', ''), 'fullname': f})
    return render_template('page/download.html', files=files)


@page.route('/download/<path:filename>', methods=['GET', 'POST'])
def download(filename):
    """
    Handles file downloading by filename
    :param filename: string
    :return: file
    """
    return send_file('/app/files/'+filename, as_attachment=True)
