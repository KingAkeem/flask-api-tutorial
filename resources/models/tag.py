from resources.db import db


class TagModel(db.Model):
    __tablename__ = "tags"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=False, nullable=False)

    foreign_key = db.ForeignKey("stores.id")
    store_id = db.Column(db.Integer, foreign_key, nullable=False)

    store = db.relationship("StoreModel", back_populates="tags")
