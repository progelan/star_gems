from flask import Flask
from config import Config

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager

from flask_bootstrap import Bootstrap
from flask_fontawesome import FontAwesome


app = Flask(__name__)# объект приложения 
app.config.from_object(Config)


db = SQLAlchemy(app)# объект, представляет базу данных
migrate = Migrate(app, db)# объект, механизм миграции


bootstrap = Bootstrap(app)
fa = FontAwesome(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"




from app import routes, models, errors# импорт тут, чтобы избежать цикличного импорта


# from flask_admin import Admin
# from flask_admin.contrib.sqla import ModelView
# from app.models import TypeGem, User, Gem, Preference, db

# admin = Admin(app)
# admin.add_view(ModelView(User, db.session))
# admin.add_view(ModelView(Gem, db.session))
# admin.add_view(ModelView(Preference, db.session))
# admin.add_view(ModelView(TypeGem, db.session))



