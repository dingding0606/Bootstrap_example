from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager

app = Flask(__name__)
app.config['SECRET_KEY'] = 'wtfwyfstevendingding0606_c513'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'  #/// indicates the current project location
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login' #view is the function name of the route
login_manager.login_message_category = 'info' 

from blog import routes

from blog.models import User
@app.shell_context_processor
def make_shell_context():
    return dict(db=db, User=User)
