from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    hash = db.Column(db.String(120), unique=True, nullable=False)
    cash = db.Column(db.Float, nullable=False, default=10000.00)
    records = db.relationship('Stock', backref='holders', lazy=True)

    def add_record(self, symbol, shares, price):
        record = Stock(
                symbol=symbol, shares=shares, price=price, userID=self.id)
        db.session.add(record)
        db.session.commit()

class Stock(db.Model):
    __tablename__ = "stocks"
    id = db.Column(db.Integer, primary_key=True)
    symbol = db.Column(db.String(20), nullable=False)
    shares = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False, default=0.00)
    userID = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    date = db.Column(db.DateTime, nullable=False, default=datetime.now())

