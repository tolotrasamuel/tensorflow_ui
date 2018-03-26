import sys

sys.path.append('../..')

from app import db
from app.models import Trained_model
db.drop_all()
db.create_all()
dog = Trained_model(folder_name='dog_breeds', title='Dog Breeds', status='Completed', label_count=5)
flower = Trained_model(folder_name='flower_retrained', title='Flower Species', status='Completed', label_count=5)
phone = Trained_model(folder_name='smartphone_brand', title='Smartphone Brand', status='Completed', label_count=4)
db.session.add(dog)
db.session.add(flower)
db.session.add(phone)
db.session.commit()

Trained_model.query.all()
