import json
import zipfile
# from models import *
from app import app, db
from app.ai.retrain import Retrain
from app.ai.classify_image import ImageClassification
from app.ai.label_image import ImageLabelling
from app.models import Trained_model
import os
from os import listdir
from os.path import isfile, join

from flask import Flask, request, redirect, url_for, render_template, send_from_directory
from werkzeug.utils import secure_filename
from threading import Thread
import shutil

UPLOAD_FOLDER = 'app/ai/sample_test'
UPLOAD_FOLDER_ZIP = 'app/ai/dataset/dataset_temp'
DATASET_UPLOAD_FOLDER = 'app/ai/dataset/'
UPLOAD_FOLDER2 = 'ai/sample_test'
ALLOWED_EXTENSIONS = set(['zip', 'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])
ALLOWED_DATASET = set(['jpg', 'png', 'jpeg'])


@app.route('/')
def index():
    script_url = url_for('static', filename='index.js')

    models = Trained_model.query.filter_by(status="Completed").all()

    # insert at the beggining of the array
    models.insert(0, {'id': 0, 'title': 'Pre trained', 'folder_name': 'default', 'checked': True})

    return render_template("index.html", models=models, script=script_url)


@app.route('/retrain')
def retrain():
    script_url = url_for('static', filename='retrain.js')
    return render_template("retrain.html", script=script_url)


@app.route('/api/deletebyid', methods=['GET', 'POST'])
def deletebyid():
    id = request.form['id']
    print("Trying to delete id: " + str(id))
    to_delete_model = Trained_model.query.filter_by(id=id).first()
    db.session.delete(to_delete_model)
    db.session.commit()
    return 'Success'


@app.route('/lab')
def lab():
    script_url = url_for('static', filename='lab.js')
    models = Trained_model.query.all()

    models_trained = []
    models_training = []
    for model in reversed(models):

        if model.status == 'Completed':
            models_trained.append(model)
        else:
            models_training.append(model)

    return render_template("lab.html",
                           models_training=models_training,
                           models_trained=models_trained,
                           script=script_url)


@app.route('/api/retrain', methods=['GET', 'POST'])
def api_retrain():
    if request.method == 'POST':
        print ('Retrain controller starting')
        files = request.files.getlist("files[]")
        labels = request.form.getlist("labels[]")
        if not files:
            print ('File format not supported')
            return 'File format not supported', 500
        if not labels:
            print ('Labels not detected')
            return 'Labels not detected', 500
        zips = []
        for i in range(len(files)):
            file = files[i]
            label = labels[i]
            if file.filename == '':
                print ('No file uploaded')
                return 'No file uploaded', 500

            if file and allowed_file(file.filename):
                filename = secure_filename(label) + '.zip'
                zip_path = os.path.join(UPLOAD_FOLDER_ZIP, filename)
                print (zip_path)
                zips.append({'path': zip_path, 'label': label})
                file.save(zip_path)

        data = {
            'title': request.form['title'],
            'labels': zips
        }
        thread_tensorflow = Thread(target=clean_zip_for_learning, args=(data,))
        thread_tensorflow.start()

        return json.dumps({'msg': 'Upload successful. Please wait for the AI to learn'})


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def allowed_img(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def clean_file_extension(path, target_directory):
    # path app/ai/dataset/dataset_temp/beef.zip
    print (path)

    for f in listdir(path):
        if isfile(join(path, f)):
            if not allowed_img(f):
                os.remove(join(path, f))
                print ('Not supported file removed ' + f)
            else:
                if path != target_directory:
                    shutil.move(join(path, f), join(target_directory, f))
        else:
            # is folder, recurse loop
            clean_file_extension(join(target_directory, f), target_directory)
            os.rmdir(join(target_directory, f))
    pass


def startTraining(image_dir, title, id):
    params = {'image_dir': image_dir, 'title': title}
    print('Initiating learning')
    retrainer = Retrain(params)
    retrainer.retrain()
    print('Training done with id', id)
    new_model = Trained_model.query.filter_by(id=id).first()
    new_model.status = "Completed"
    db.session.commit()
    pass


def rename_all_files(path):
    files = listdir(path)
    for i in range(len(files)):
        f = files[i]
        os.rename(join(path, f), join(path, str(i) + "." + f.split(".")[-1]))
    pass


def saveToDatabase(data, trained_model_dir):
    print("Saving to database", trained_model_dir)
    model_to_save = Trained_model(folder_name=trained_model_dir, title=data['title'], status='Pending',
                                  label_count=(len(data['labels'])))
    db.session.add(model_to_save)
    db.session.commit()
    return model_to_save.id


def clean_zip_for_learning(data):
    title = data['title']
    zips = data['labels']
    trained_model_dir = (join(DATASET_UPLOAD_FOLDER, secure_filename(title)))
    # foreach labels
    for zip in zips:
        zip_ref = zipfile.ZipFile(zip['path'], 'r')
        target_directory = join(trained_model_dir, zip['label'])
        if not os.path.isdir(target_directory):
            zip_ref.extractall(target_directory)
        zip_ref.close()
        clean_file_extension(target_directory, target_directory)
        rename_all_files(target_directory)
    # if you reached here, everything is fine, you can now start the training process

    id = saveToDatabase(data, secure_filename(title))
    startTraining(trained_model_dir, title, id)


@app.route('/api/evaluate', methods=['GET', 'POST'])
def api_evaluate():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            return 'File format not supported ', 500
        file = request.files['file']
        # if user does not select file, browser also
        # submit a empty part without filename
        if file.filename == '':
            return 'No file uploaded', 500
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            img_path = os.path.join(UPLOAD_FOLDER, filename)
            print (img_path)
            file.save(img_path)
            model_dir_name = request.form['folder_name']
            print (model_dir_name)
            if not model_dir_name == 'default':
                newLabelling = ImageLabelling(model_dir_name, img_path)
                print('starting labeling')
                result = newLabelling.start()
            else:
                print('Default classification')
                newClassifiction = ImageClassification(img_path)
                result = newClassifiction.start()
            return json.dumps(['sample_test/' + filename, result])

    return 'Failure'


@app.route('/sample_test/<filename>')
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER2, filename)
