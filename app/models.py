class Training:
    def __init__(self):
        pass


class Model:
    def __init__(self):
        pass


class Label:
    def __init__(self):
        pass


from app import db


class Trained_model(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    folder_name = db.Column(db.String(120), nullable=False)
    title = db.Column(db.String(120), nullable=False)
    status = db.Column(db.String(120), nullable=True)
    label_count = db.Column(db.Integer(), nullable=True)

    def __repr__(self):
        return '<Trained_model %r>' % self.title
