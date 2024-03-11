import os
from flask_sqlalchemy import SQLAlchemy
from flask import Flask



database_filename = "database.db"
project_dir = os.path.dirname(os.path.abspath(__file__))
database_path = "sqlite:///{}".format(os.path.join(project_dir, database_filename))

# db = SQLAlchemy()

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = database_path
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

class Drink(db.Model):
    id = db.Column(db.Integer().with_variant(db.Integer, "sqlite"), primary_key=True)
    title = db.Column(db.String(80), unique=True)
    recipe = db.Column(db.String(180), nullable=False)

    def __repr__(self):
        return '<User %r>' % self.title


@app.route('/')
def drop_all_tables():
    with app.app_context():
        db.drop_all()
        db.create_all()
        return 'All tables dropped and recreated'

if __name__ == '__main__':
    app.run(debug=True)