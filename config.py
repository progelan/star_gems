import os


class Config(object):
	SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
	SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:bkmz2006@localhost/flaskdb'
	SQLALCHEMY_TRACK_MODIFICATIONS = False
	BOOTSTRAP_SERVE_LOCAL = True
	# SQLALCHEMY_ECHO = True


# >>> from stargems import app               
# >>> app.config['SECRET_KEY']
# 'you-will-never-guess'
