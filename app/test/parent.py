from os import listdir
from os.path import join, isfile
import zipfile
import os
import shutil
import sys

sys.path.append("../../app")

from ai.retrain import main

ALLOWED_EXTENSIONS = set(['zip', 'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])


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


def startTraining(image_dir, title):
    params = {'image_dir': image_dir, 'title': title}
    print('Initiating learning')
    retrainer = main(params)
    retrainer.retrain()
    pass


def rename_all_files(path):
    files = listdir(path)
    for i in range(len(files)):
        f = files[i]
        os.rename(join(path, f), join(path, str(i)+"."+f.split(".")[-1]))
    pass


def clean_zip_for_learning(data):
    title = data['title']
    zips = data['labels']
    trained_model_dir = join(DATASET_UPLOAD_FOLDER, title)
    # foreach labels
    for zip in zips:
        zip_ref = zipfile.ZipFile(zip['path'], 'r')
        target_directory = join(trained_model_dir, zip['label'])
        zip_ref.extractall(target_directory)
        zip_ref.close()
        clean_file_extension(target_directory, target_directory)
        rename_all_files(target_directory)

    # if you reached here, everything is fine, you can now start the training process
    startTraining(trained_model_dir, title)


DATASET_UPLOAD_FOLDER = '../ai/dataset/'

if __name__ == '__main__':
    print ('start')
    path = '../ai/dataset/dataset_temp/cow.zip'
    path1 = '../ai/dataset/dataset_temp/beef.zip'
    clean_zip_for_learning(
        {'title': 'fruits',
         'labels':
             [
                 {'path': path, 'label': 'cow'},
                 {'path': path1, 'label': 'beef'}
             ]
         })
