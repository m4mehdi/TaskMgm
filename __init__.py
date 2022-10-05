from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from flask_migrate import Migrate

#migrate = Migrate()
app = Flask(__name__)
# SQLAlchemy config. Read more: https://flask-sqlalchemy.palletsprojects.com/en/2.x/
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://commuser:commpass@localhost/commdb'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy()
db.init_app(app)

migrate = Migrate(app, db)

def tear_down():
    db.session.close()
    db.drop_all()
